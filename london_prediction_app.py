import streamlit as st
import pandas as pd
import joblib
import os
import plotly.express as px

# Setting Streamlit config
st.set_page_config(
    page_title="London Bike Smart Maintenance Prediction System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
# st.title("London Bike Automated Predictive Maintenance System")
# st.markdown("---")
col_logo, col_title = st.columns([1, 12])

with col_logo:
    # Adding vertical spacing using HTML to push the logo down slightly for perfect alignment
    st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/TfL_roundel_%28no_text%29.svg/500px-TfL_roundel_%28no_text%29.svg.png",
        width=65
    )

with col_title:
    st.title("London Bike Automated Predictive Maintenance System")

st.markdown("---")

# Keep model is loaded in memory to avoid reloading
@st.cache_resource
def load_predictive_brain():
    # Loading Random Forest model
    model = joblib.load('maintenance_model.pkl')
    # Loading Label Encoder for bike types (Classic vs Ebike)
    encoder = joblib.load('bike_model_encoder.pkl')
    return model, encoder

# Run the model loading function above
try:
    model, encoder = load_predictive_brain()
    st.sidebar.success("Welcome to Trung Anh project!") # Model and data baseline are ready
except Exception as e:
    st.sidebar.error(f"There's no model or encoder file available: {e}")
    st.sidebar.warning("Check the file locations.")

# Create bike baseline file
DB_FILE = 'bike_baseline_db.csv'
ORIGINAL_BACKUP_FILE = 'bike_baseline_db_original.csv' # IMPORTANT*: baseline file

st.sidebar.write("### Section 1. Functions")
page = st.sidebar.radio(
    "Select single function below:",
    ["**1/ Fleet Health Overview**", "**2/ Operational Intelligence**", "**3/ Emergency & Security**"],
    index=0
)

st.sidebar.write("### Section 2. System Admin Tools")
if st.sidebar.button("Reset baseline"):
    if os.path.exists(ORIGINAL_BACKUP_FILE):
        clean_df = pd.read_csv(ORIGINAL_BACKUP_FILE)
        clean_df.to_csv(DB_FILE, index=False)
        st.session_state.bike_db = clean_df
        if 'uploaded_files_history' in st.session_state:
            st.session_state.uploaded_files_history = [] 
        
        if 'stolen_bikes_live' in st.session_state: del st.session_state.stolen_bikes_live
        if 'broken_bikes_live' in st.session_state: del st.session_state.broken_bikes_live

        st.sidebar.success("System has been reset completely! Reloading.")
        st.rerun()
    else:
        if 'bike_db' in st.session_state:
            clean_df = st.session_state.bike_db.copy()
            clean_df['accumulated_hours_past'] = 0.0 
            clean_df['total_trips_past'] = 0
            clean_df.to_csv(DB_FILE, index=False)
            st.session_state.bike_db = clean_df
            if 'uploaded_files_history' in st.session_state:
                st.session_state.uploaded_files_history = []
            st.sidebar.success("Baseline hours have been wiped clean back to 0! Reloading...")
            st.rerun()

if 'bike_db' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.bike_db = pd.read_csv(DB_FILE)
        st.sidebar.info(f"Connected to baseline database. Records found: {len(st.session_state.bike_db):,}.")
    else:
        st.sidebar.error("Missing 'bike_baseline_db.csv' file.")


# Create Tab 1: Dashboard for Fleet Health
if page == "**1/ Fleet Health Overview**":
    st.subheader("Strategic Fleet Health & Operational Performance")
    st.markdown("The dashboard presents information about the journey of public bicycles in London since 1 January 2024, while also highlighting the wear and tear of the bicycles based on the usage time between docking stations.")

    df_fleet = st.session_state.bike_db.copy()

    if not df_fleet.empty:
        # KPI Counters
        total_bikes = len(df_fleet)
        classic_count = len(df_fleet[df_fleet['bike_model'] == 'CLASSIC'])
        ebike_count = len(df_fleet[df_fleet['bike_model'] == 'PBSC_EBIKE'])
        
        high_risk_bikes = len(df_fleet[df_fleet['accumulated_hours_past'] >= 200.0])
        safe_rate = ((total_bikes - high_risk_bikes) / total_bikes) * 100

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric(label="Overall Fleet Size", value=f"{total_bikes:,}")
        with kpi2:
            st.metric(label="Classic Bikes", value=f"{classic_count:,}", delta=f"{classic_count/total_bikes:.1%}")
        with kpi3:
            st.metric(label="E-Bikes", value=f"{ebike_count:,}", delta=f"{ebike_count/total_bikes:.1%}")
        with kpi4:
            st.metric(label="Safety Rate", value=f"{safe_rate:.1f}%", delta=f"-{high_risk_bikes} high-risk bikes", delta_color="inverse")

        st.markdown("")
        st.markdown("---")

        # Graph: Composition & Health Segmentation
        col_donut, col_urgency = st.columns([4, 6])
        
        with col_donut:
            fig_donut = px.pie(
                df_fleet, 
                names='bike_model', 
                hole=0.5,
                title="Distribution of Bike Model",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_donut.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                title_x=0.0
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            st.caption("**Figure 1.1**: An overview of the differences in the use of Classic and Ebike vehicles in London shows that the adoption rate of the e-bike system is gradually entering the real market.")
        with col_urgency:
            # Segment bikes into smart maintenance buckets
            bins = [0, 50, 100, 150, 200, float('inf')]
            group_names = ['Brand New (0-50h)', 'Healthy (50-100h)', 'Moderate (100-150h)', 'Watchlist (150-200h)', 'Critical (>200h)']
            df_fleet['Health Segment'] = pd.cut(df_fleet['accumulated_hours_past'], bins=bins, labels=group_names)
            
            segment_summary = df_fleet['Health Segment'].value_counts().reindex(group_names).reset_index()
            segment_summary.columns = ['Health Condition Tier', 'Asset Count']
            
            fig_segment = px.bar(
                segment_summary, 
                x='Health Condition Tier', 
                y='Asset Count', 
                color='Health Condition Tier',
                title="Bike Health Usage Strategic Segmentation",
                labels={'Health Condition Tier': 'Asset Condition Category', 'Asset Count': 'Number of Bikes'},
                color_discrete_sequence=px.colors.sequential.Teal_r
            )
            fig_segment.update_layout(showlegend=True, legend_title_text='Condition Categories', title_x=0.0)
            st.plotly_chart(fig_segment, use_container_width=True)
            st.caption("**Figure 1.2**: The bar chart showing the condition of bicycles in the early days indicates that most bikes are in good health with appropriate usage intensity.")
        # Graph: Usage Intensity Scatter & Data Grid
        st.markdown("---")
        col_scatter, col_table = st.columns([6, 4])

        with col_scatter:
            fig_scatter = px.scatter(
                df_fleet, 
                x='accumulated_hours_past', 
                y='total_trips_past',
                color='bike_model', 
                size='accumulated_hours_past',
                hover_name='bike_number',
                title="Usage Intensity Profile between Trips and Accumulated Hours",
                labels={'accumulated_hours_past': 'Total Hours Logged', 'total_trips_past': 'Total Cumulative Trips'},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_scatter.update_layout(title_x=0.0)
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("**Figure 1.3**: Strategy correlating the total number of hours travelled with the total number of trips for a vehicle to compare the differences in the use of Classic Bikes and E-bikes.")

        with col_table:
            st.write("#### Asset Journey Database Lookup")
            search_query = st.text_input("Enter 'bike_number' to search for historical journey:")
            
            if search_query:
                search_results = df_fleet[df_fleet['bike_number'].astype(str).str.contains(search_query)]
                st.write(f"Found {len(search_results)} matching results:")
                st.dataframe(search_results, use_container_width=True)
            else:
                st.write("*Top 10 vehicles with the highest accumulated usage hours:*")
                top_10_busy = df_fleet.sort_values(by='accumulated_hours_past', ascending=False).head(10)
                st.dataframe(top_10_busy[['bike_number', 'accumulated_hours_past', 'total_trips_past', 'bike_model']], use_container_width=True)

    else:
        st.warning("The current database is empty. Please check the file 'bike_baseline_db.csv'.")

# Create Tab 2: Predict Bike Maintenance and Check the bikes status
elif page == "**2/ Operational Intelligence**":
    st.subheader("New Monthly Data Upload and Automatic Bike Predictive Maintenance Pipeline")
    st.markdown("*This section allows the provision of cycling journey files in London to predict the maintenance conditions of the bicycles. It creates a new loop for the journeys of the next cycle to track the accumulated operating hours of each bicycle in the Transport for London (TfL) public bike system.*")

    if 'uploaded_files_history' not in st.session_state:
        st.session_state.uploaded_files_history = []

    uploaded_raw_file = st.file_uploader("Please upload the raw trip data file - csv file required.", type="csv")
    
    if uploaded_raw_file is not None:
        file_name = uploaded_raw_file.name
        raw_df = pd.read_csv(uploaded_raw_file)
        
        raw_df['Start date'] = pd.to_datetime(raw_df['Start date'])
        start_date_min = raw_df['Start date'].min().strftime('%d/%m/%Y')
        end_date_max = raw_df['Start date'].max().strftime('%d/%m/%Y')
        file_period_range = f"{start_date_min} to {end_date_max}"
        
        st.info(f"**Current File:** {file_name} | **Exact Data Period:** {file_period_range}")
        is_duplicate = any(h['name'] == file_name or h['period'] == file_period_range for h in st.session_state.uploaded_files_history)
        
        if is_duplicate:
            st.error(f"**Data Conflict Detected!** The file '{file_name}' or the data period '{file_period_range}' has already been processed in a previous cycle. Uploading this will cause incorrect duplicated accumulation. Processing halted.")
        else:
            st.success("Successfully uploaded, let's activate processing system.")
            
            df_emergency = raw_df[(raw_df['Total duration (ms)'] > 86400000) | (raw_df['Total duration (ms)'] <= 60000)]
            st.session_state.emergency_data = df_emergency
            
            df_normal = raw_df[(raw_df['Total duration (ms)'] > 60000) & (raw_df['Total duration (ms)'] <= 86400000)].copy()
            df_normal['duration_hour'] = df_normal['Total duration (ms)'] / (1000 * 3600)
            
            monthly_summary = df_normal.groupby(['Bike number', 'Bike model']).agg(
                hours_this_month=('duration_hour', 'sum'),
                trips_this_month=('Bike number', 'count'),
                avg_duration_hour_this_month=('duration_hour', 'mean'), 
                last_active_date_per_bike=('Start date', 'max')        
            ).reset_index()
            
            monthly_summary.rename(columns={'Bike number': 'bike_number', 'Bike model': 'bike_model'}, inplace=True)
            
            current_db = st.session_state.bike_db.copy()
            merged_df = pd.merge(current_db, monthly_summary, on=['bike_number', 'bike_model'], how='outer')
            
            merged_df['accumulated_hours_past'] = merged_df['accumulated_hours_past'].fillna(0)
            merged_df['total_trips_past'] = merged_df['total_trips_past'].fillna(0)
            merged_df['hours_this_month'] = merged_df['hours_this_month'].fillna(0)
            merged_df['trips_this_month'] = merged_df['trips_this_month'].fillna(0)
            
            merged_df['total_hours'] = merged_df['accumulated_hours_past'] + merged_df['hours_this_month']
            merged_df['total_trips'] = merged_df['total_trips_past'] + merged_df['trips_this_month']
            
            merged_df['avg_trip_duration'] = merged_df['avg_duration_hour_this_month'].fillna(0)
            merged_df['last_active_date_per_bike'] = pd.to_datetime(merged_df['last_active_date_per_bike'])
            latest_time_system = merged_df['last_active_date_per_bike'].max()
            
            merged_df['latest_active'] = (latest_time_system - merged_df['last_active_date_per_bike']).dt.days
            merged_df['latest_active'] = merged_df['latest_active'].fillna(30)
            
            active_bikes_df = merged_df[(merged_df['hours_this_month'] > 0) | (merged_df['total_hours'] > 0)].copy()
            
            if not active_bikes_df.empty:
                try:
                    active_bikes_df['bike_model_encoded'] = encoder.transform(active_bikes_df['bike_model'])
                except:
                    active_bikes_df['bike_model_encoded'] = active_bikes_df['bike_model'].apply(lambda x: 1 if x == 'PBSC_EBIKE' else 0)
                
                X_matrix = active_bikes_df[['total_trips', 'avg_trip_duration', 'latest_active', 'bike_model_encoded']]
                X_matrix.columns = ['total_trips', 'avg_trip_duration', 'latest_active', 'bike_model']
                
                active_bikes_df['prediction'] = model.predict(X_matrix)
                
                display_df = active_bikes_df[[
                    'bike_number', 'bike_model', 'total_hours', 'total_trips', 'avg_trip_duration', 'latest_active', 'prediction'
                ]].copy()
                
                display_df['total_hours'] = display_df['total_hours'].round(2)
                display_df['avg_trip_duration'] = display_df['avg_trip_duration'].round(3)
                display_df['latest_active'] = display_df['latest_active'].astype(int).astype(str) + " days ago"
                
                safe_bikes_df = display_df[display_df['prediction'] == 0].drop(columns=['prediction'])
                maint_bikes_df = display_df[display_df['prediction'] == 1].drop(columns=['prediction'])
                
                col_safe, col_warn = st.columns(2)
                with col_safe:
                    st.write(f"The number of normal bikes ({len(safe_bikes_df)})")
                    if not safe_bikes_df.empty:
                        st.dataframe(safe_bikes_df, use_container_width=True)
                        
                with col_warn:
                    st.write(f"Bikes requiring maintenance ({len(maint_bikes_df)})")
                    st.markdown("*Tick the checkbox next to the bike ID once the maintenance check is complete:*")
                    
                    if not maint_bikes_df.empty:
                        maint_bikes_df.insert(0, "Checked & Cleared", False)
                        edited_maint_df = st.data_editor(
                            maint_bikes_df,
                            key="maint_editor",
                            hide_index=True,
                            use_container_width=True,
                            disabled=['bike_number', 'bike_model', 'total_hours', 'total_trips', 'avg_trip_duration', 'latest_active']
                        )
                    else:
                        st.success("There's no bikes require maintenance for this month.")
                        edited_maint_df = pd.DataFrame()

                st.write("### Database Synchronization")
                if st.button("Update Baseline Database for Next Cycle"):
                    next_month_db = merged_df.copy()
                    next_month_db['accumulated_hours_past'] = next_month_db['total_hours']
                    next_month_db['total_trips_past'] = next_month_db['total_trips']
                    
                    if not edited_maint_df.empty:
                        cleared_bikes = edited_maint_df[edited_maint_df["Checked & Cleared"] == True]['bike_number'].tolist()
                        if cleared_bikes:
                            next_month_db.loc[next_month_db['bike_number'].isin(cleared_bikes), 'accumulated_hours_past'] = 0.0
                            next_month_db.loc[next_month_db['bike_number'].isin(cleared_bikes), 'total_trips_past'] = 0
                            st.sidebar.success(f"Successfully reset {len(cleared_bikes)} bikes back to 0 hours.")
                    
                    next_month_db = next_month_db[['bike_number', 'accumulated_hours_past', 'total_trips_past', 'bike_model']]
                    next_month_db.to_csv(DB_FILE, index=False)
                    st.session_state.uploaded_files_history.append({'name': file_name, 'period': file_period_range})
                    st.session_state.bike_db = next_month_db
                    st.success("Database synchronized successfully! Ready for the next cycle.")
                    st.rerun()

    if st.session_state.uploaded_files_history:
        st.markdown("---")
        st.write("Processed Files Log")
        log_df = pd.DataFrame(st.session_state.uploaded_files_history)
        log_df.columns = ["Uploaded File Name", "Data Period Covered"]
        st.table(log_df)

# Create Tab 3: Check Emergency Bike for abnormal datetime
elif page == "**3/ Emergency & Security**":
    if 'emergency_data' in st.session_state and not st.session_state.emergency_data.empty:
        df_emg = st.session_state.emergency_data.copy()
        
        if 'stolen_bikes_live' not in st.session_state:
            st.session_state.stolen_bikes_live = df_emg[df_emg['Total duration (ms)'] > 86400000].copy()
        
        if 'broken_bikes_live' not in st.session_state:
            st.session_state.broken_bikes_live = df_emg[df_emg['Total duration (ms)'] <= 60000].copy()

        # Case 1: Check 24 hours duration bikes
        st.error("### Emergency Alert: The bike is suspected to be stolen or lost (Trip duration > 24 hours)")
        st.markdown("The list below shows the trips that have been flagged as potential theft or loss cases. *Tick the checkbox and select the status. Once confirmed, these bikes will be reset to 0 in the baseline database and removed from this operational view.*")
        
        if not st.session_state.stolen_bikes_live.empty:
            stolen_display = st.session_state.stolen_bikes_live[[
                'Bike number', 'Bike model', 'Start date', 'Start station', 'End date', 'End station', 'Total duration'
            ]].rename(columns={
                'Bike number': 'Bike ID', 'Bike model': 'Bike Model', 'Start date': 'Start Date',
                'Start station': 'Start Station', 'End date': 'End Date', 'End station': 'End Station', 'Total duration': 'Total Duration'
            })
            
            stolen_display.insert(0, "Retrieved & Actioned", False)
            stolen_display["Security Status / Diagnosis"] = "Investigating"
            
            edited_stolen_df = st.data_editor(
                stolen_display,
                key="stolen_editor_live",
                hide_index=True,
                use_container_width=True,
                disabled=['Bike ID', 'Bike Model', 'Start Date', 'Start Station', 'End Date', 'End Station', 'Total Duration'],
                column_config={
                    "Security Status / Diagnosis": st.column_config.SelectboxColumn(
                        "Security Status / Diagnosis",
                        help="Select the final security audit result after retrieving",
                        width="medium",
                        options=["Investigating", "Stolen", "System Lock Error - Safe Bike", "Customer Forgot to Dock", "Damaged"],
                        required=True
                    )
                }
            )
            
            col_btn1, _ = st.columns([3, 7])
            with col_btn1:
                if st.button("Confirm Selected Retrievals", key="btn_stolen_clear_selected"):
                    cleared_stolen_bikes = edited_stolen_df[edited_stolen_df["Retrieved & Actioned"] == True]['Bike ID'].tolist()
                    if cleared_stolen_bikes:
                        if os.path.exists(DB_FILE):
                            db_df = pd.read_csv(DB_FILE)
                            db_df.loc[db_df['bike_number'].isin(cleared_stolen_bikes), 'accumulated_hours_past'] = 0.0
                            db_df.loc[db_df['bike_number'].isin(cleared_stolen_bikes), 'total_trips_past'] = 0
                            db_df.to_csv(DB_FILE, index=False)
                            st.session_state.bike_db = db_df
                        st.session_state.stolen_bikes_live = st.session_state.stolen_bikes_live[~st.session_state.stolen_bikes_live['Bike number'].isin(cleared_stolen_bikes)]
                        st.sidebar.success(f"Successfully reset {len(cleared_stolen_bikes)} stolen bikes back to 0 hours.")
                        st.success(f"Successfully processed {len(cleared_stolen_bikes)} bikes. Baseline updated and assets removed from active alerts.")
                        st.rerun()
                    else:
                        st.warning("Please tick the 'Retrieved & Actioned' checkbox for the specific bikes you have handled first.")
            
            # Chart: Stolen Incidents Plotly Bar Chart
            st.markdown("<br>", unsafe_allow_html=True)
            top_stolen_stations = stolen_display['Start Station'].value_counts().head(5).reset_index()
            top_stolen_stations.columns = ['Station Name', 'Incident Count']
            
            if not top_stolen_stations.empty:
                fig_stolen = px.bar(
                    top_stolen_stations, x='Station Name', y='Incident Count', color='Station Name',
                    title='Top 5 Origin Stations with Most Long-Duration Incidents (> 24 Hours)',
                    labels={'Station Name': 'Station Location', 'Incident Count': 'Number of Critical Alerts'},
                    color_discrete_sequence=px.colors.sequential.Teal_r
                )
                fig_stolen.update_layout(showlegend=True, legend_title_text='Station Legend', title_x=0.0)
                st.plotly_chart(fig_stolen, use_container_width=True)
        else:
            st.success("All potential theft or loss cases have been completely resolved and cleared from the system.")

        #  Case 2: Check 1 minute duration bike
        st.markdown("---")
        st.warning("### Operational Alert: The bike is suspected to have a minor hardware issue (Trip duration <= 1 minute)")
        st.markdown("The list below shows the trips that have been flagged as potential minor hardware issues. *Tick the checkbox and log the failure. Once confirmed, these bikes will be reset to 0 and removed from this view.*")
        
        if not st.session_state.broken_bikes_live.empty:
            broken_display = st.session_state.broken_bikes_live[[
                'Bike number', 'Bike model', 'Start date', 'Start station', 'Total duration'
            ]].rename(columns={
                'Bike number': 'Bike ID', 'Bike model': 'Bike Model', 'Start date': 'Start Date',
                'Start station': 'Station Located', 'Total duration': 'Total Duration'
            })
            
            broken_display.insert(0, "Inspected & Fixed", False)
            broken_display["Hardware Failure Type"] = "Awaiting Inspection"
            
            edited_broken_df = st.data_editor(
                broken_display,
                key="broken_editor_live",
                hide_index=True,
                use_container_width=True,
                disabled=['Bike ID', 'Bike Model', 'Start Date', 'Station Located', 'Total Duration'],
                column_config={
                    "Hardware Failure Type": st.column_config.SelectboxColumn(
                        "Hardware Failure Type",
                        help="Select the hardware issue found by the technician",
                        width="medium",
                        options=["Awaiting Inspection", "Flat Tyre", "Chain Slipped", "Brake Component Failure", "System Error", "No Issue Found"],
                        required=True
                    )
                }
            )
            
            if st.button("Confirm Selected Inspections", key="btn_broken_clear_selected"):
                cleared_broken_bikes = edited_broken_df[edited_broken_df["Inspected & Fixed"] == True]['Bike ID'].tolist()
                if cleared_broken_bikes:
                    if os.path.exists(DB_FILE):
                        db_df = pd.read_csv(DB_FILE)
                        db_df.loc[db_df['bike_number'].isin(cleared_broken_bikes), 'accumulated_hours_past'] = 0.0
                        db_df.loc[db_df['bike_number'].isin(cleared_broken_bikes), 'total_trips_past'] = 0
                        db_df.to_csv(DB_FILE, index=False)
                        st.session_state.bike_db = db_df
                    st.session_state.broken_bikes_live = st.session_state.broken_bikes_live[~st.session_state.broken_bikes_live['Bike number'].isin(cleared_broken_bikes)]
                    st.sidebar.success(f"Successfully reset {len(cleared_broken_bikes)} station bikes back to 0 hours.")
                    st.success(f"Technician database synchronized. {len(cleared_broken_bikes)} bikes cleared and redeployed to service.")
                    st.rerun()
                else:
                    st.warning("Please tick the 'Inspected & Fixed' checkbox for the specific bikes you have checked first.")
            
            # Chart: Broken Stations Plotly Bar Chart
            st.markdown("<br>", unsafe_allow_html=True)
            top_broken_stations = broken_display['Station Located'].value_counts().head(5).reset_index()
            top_broken_stations.columns = ['Station Name', 'Failure Count']
            
            if not top_broken_stations.empty:
                fig_broken = px.bar(
                    top_broken_stations, x='Station Name', y='Failure Count', color='Station Name',
                    title='Top 5 Stations with Most Short-Duration Hardware Anomalies (≤ 1 Minute)',
                    labels={'Station Name': 'Station Location', 'Failure Count': 'Number of Hardware Alerts'},
                    color_discrete_sequence=px.colors.sequential.Teal_r
                )
                fig_broken.update_layout(showlegend=True, legend_title_text='Station Legend', title_x=0.0)
                st.plotly_chart(fig_broken, use_container_width=True)
        else:
            st.success("All recorded hardware anomaly metrics have been systematically verified and cleared by ground operations.")
            
    else:
        if 'stolen_bikes_live' in st.session_state: del st.session_state.stolen_bikes_live
        if 'broken_bikes_live' in st.session_state: del st.session_state.broken_bikes_live
        st.info("Currently, there is no raw data available. Please upload a raw CSV file in Tab 2 to activate the emergency alert system.")