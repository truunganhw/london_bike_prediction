# Project tile: London Bike Automated Predictive Maintenance System
> A Data Science solution supporting predictive maintenance for the Smart City bicycle fleet and emergency response for the London bicycle system based on real-time bicycle journey data at https://tfl.gov.uk/

---

## Project Overview
This software product is a Data Science product designed to provide a solution for automating predictive maintenance and real-time security management for the London bike-sharing network.

Built using "*Streamlit*" and powered by a robust "*Random Forest Classification Model*", this system transforms raw, chaotic journey telemetry data into useful operational intelligence. The system leverages the journey tracking resources between dock stations of a public bike system, enabling non-technical fleet operators to monitor vehicle degradation, implement accurate maintenance schedules, and respond instantly to critical security indicators (stolen assets or malfunctions) through a unified, intuitive interface.

---

## Key Functions

### 1. Dashboard - Visualisation the Strategic Fleet Health & Operational Performance
* **Display index** Calculate the size of the vehicle fleet, clarify the overall view of the bicycle model (classic vs e-bike) in general, safety ratio of the vehicle fleet system
* **Health Bike Segmentation:** Use an automatic clustering matrix on vehicle condition based on their health according to usage history displayed on a bar chart.
* **The Intensity of Bike Using:** Implement an interactive multidimensional scatter plot comparing total accumulated hours with total accumulated trips to identify the most frequently used equipment and minimize the risk of unexpected component failures.

### 2. Operational Intelligence Pipeline
* Apply the Random Forest model to predict cars based on the vehicle identification number, while also calculating the total running time of the vehicle to consider making warranty decisions for bicycles

* Calculate the accumulated activity of the vehicle through the journey, creating constraints to automatically prevent duplicate accumulation of data that could lead to system errors. 

* Carry out the vehicle status change process after the maintenance team has repaired or checked it to zero value to perform the next cycles.

* Authenticate the bicycle status through the synchronization function for the background dataset, supporting the cumulative travel hours function of the bicycle.

### 3. Emergency & Security Tracking View
* **Check vehicles exceeding 24 hours duration:** Filter abnormal trips exceeding 24 hours, branch data to alert the system, support operational staff to monitor the bike's departure station, record security diagnostics, and initiate field recalls.

* **Check bikes under 1 minute to consider Hardware Failure:** Automatically mark trips under 1 minute, alert the inspection system, handle vehicle conditions on site.

* **Synchronise the vehicle in real time:** Ensure the system is synchronised with real-time, remove processed vehicles, send them to the pipeline to reset their value to 0 and store them for the backend database for the next cycle.

* **Enhance the vehicle status inspection feature to ensure system consistency :** Vehicle inspection feature, using dropdown boxes to check vehicle conditions such as "engine failure", "stolen", "system errors", "incorrect warnings", "normal status" to ensure consistency in the management platform

---

## Repository & Package Structure
The package architecture is meticulously organized to maintain a strict separation of concerns, ensuring frictionless deployment:

```text
London_Bike_App/
│
├── .streamlit/
│   └── config.toml                # Coporate theme & pastel configurations
│
├── london_prediction_app.py          # Central control layout and UI routing execution file
├── maintenance_model.pkl          # Serialized production-ready Random Forest classifier
├── bike_model_encoder.pkl         # Serialized LabelEncoder package for bike category profiles
│
├── bike_baseline_db.csv           # Active, dynamic operational database (modified via accumulative bike duration)
├── bike_baseline_db_original.csv  # Backup file for system restoration
│
├── requirements.txt               # Documented explicit dependency manifest
└── README.md                      # Comprehensive deployment guide and documentation
```
---
## Preparation
**Important**: Ensure your deployment machine has Python 3.9 to 3.11 installed.
* Access this file to take any things you want: [CETM46 - THI TRUNG ANH DO](https://drive.google.com/drive/folders/1MV4DRPUW3FfT66YUXgb_kWJccH-StYqe?usp=sharing)
1. Data
   * Data for training on Google Colab [Link data 1](https://drive.google.com/drive/folders/1oq0JjJhrdzyful01smx8QuZwNgfrPDBw?usp=sharing)
   * Data for base data on Streamlit code [Link data 2](https://drive.google.com/drive/folders/1vrCw6FYT7V_KeoEpmioC68J_tKToVIGC?usp=sharing)
   * Data input for tab 2 on Streamlit app [Link data 3](https://drive.google.com/drive/folders/18XYGckbkWotY-ktb472ottqsz1f_8yED?usp=sharing)
2. Training Model: [Google Colab](https://colab.research.google.com/drive/164i2Vr4VdhWPjH7LZUpOpMVDspVQRxFO?usp=sharing).
   * Import library to connect to Google Drive: `from google.colab import drive`
   * Working with dataframe, table: `import pandas as pd`
   * Machine Learning model: `from sklearn.ensemble import RandomForestClassifier`
     (follow the library on Google Colab file)
   * Save model and data to `london_prediction_app.py`
3. Streamlit App
   * Prepare `'bike_baseline_db_original.csv'` data, `maintenance_model.pkl`, `bike_model_encoder.pkl` files
   * Run the Python file `london_prediction_app.py`
   * Open terminal, `streamlit run tlondon_prediction_app.py`
4. Test on Streamlit App
   * Open tab `2/ Operational Intelligence`, upload file in `Link data 2 above` (about 8-9 files, you can see the list of need maintenance bikes.)
   * After upload each file, remember to click on Sync the data button `Update Baseline Database for Next Cycle`

5. Visit localhost
  * [http://localhost:3000](http://localhost:8501/) in your browser to use the application.
---

<img width="1536" height="812" alt="image" src="https://github.com/user-attachments/assets/3b1551d2-1746-489c-a258-c77af225174a" />

Figure 1: The dashboard of Fleet Health Overview (1) - This screen presents information about public bicycles in London based on data from the first month, giving management an overview of the usage metrics of the bicycles.

<img width="1429" height="759" alt="image" src="https://github.com/user-attachments/assets/1f954be5-0423-4775-a9f5-40937d87a140" />

Figure 2: The dashboard of Fleet Health Overview (2) - The screen displays the total time spent between two types of bicycle models while also creating a search list for bicycle information based on ID.

<img width="1536" height="816" alt="image" src="https://github.com/user-attachments/assets/6a4de1c0-fb3e-4984-bfa3-6521b23366fe" />

Figure 3. The Operation Intelligence Screen (1) - The original screen needs to upload the data file for the next month, retrieving data from cycling.data.tfl.gov.uk.

<img width="1536" height="815" alt="image" src="https://github.com/user-attachments/assets/ba9eb691-730d-4854-a790-13f01ad9cdb1" />

Figure 4. The Operation Intelligence Screen (2). After successfully uploading the data, the list of trips for the vehicles will be displayed.

<img width="1536" height="816" alt="image" src="https://github.com/user-attachments/assets/f541cf53-9e16-442f-bbba-e2eb06140c06" />

Figure 5. The Operation Intelligence Screen (2). After successfully uploading the data, the list of trips for the vehicles will be displayed.

<img width="1536" height="816" alt="image" src="https://github.com/user-attachments/assets/cd08c144-92cc-4329-9216-96ad5a2b8c1f" />

Figure 6. The Operation Intelligence Screen (3) - Whenever uploading data, it is necessary to synchronise the data to save the file to the backend database and activate the trip accumulation feature.

<img width="1536" height="815" alt="image" src="https://github.com/user-attachments/assets/dbdccfe5-0315-4c2f-8564-fe976d13934b" />

Figure 7. The Operation Intelligence Screen (4) - The screen displays a list of uploaded files, while preventing files with duplicate names or dates that have been uploaded previously, eliminating the risk of indefinite cumulative errors and data inaccuracies.

<img width="1429" height="759" alt="image" src="https://github.com/user-attachments/assets/a1abb676-7e80-4487-9323-8545b81d3846" />

Figure 8. The Operation Intelligence Screen (5) - The screen displays a list of vehicles that need maintenance due to reaching the operational hour threshold, while integrating checkboxes to ensure those vehicles are transferred to the backend data with a value of zero.

<img width="1536" height="815" alt="image" src="https://github.com/user-attachments/assets/1f9913b7-3545-44d1-a5d2-bba90f880263" />

Figure 9. Emergency alert for 24h cases - Check the 24h cases as stolen or any emergency situation, integrate the drop-down information of bike status.

<img width="1536" height="815" alt="image" src="https://github.com/user-attachments/assets/34a8a6c3-80b5-4c2b-a9a2-fa188e32b9b4" />

Figure 10. Emergency Alert using click on check box and confirm those bike before update them into data baseline.

<img width="1536" height="813" alt="image" src="https://github.com/user-attachments/assets/b187fa04-4d51-4fe5-83e2-68b072171ab4" />

Figure 11. Emergency alert of under 1 minute cases.

<img width="1536" height="816" alt="image" src="https://github.com/user-attachments/assets/10006c86-41eb-46b6-b8d8-f491015c56b8" />

Figure 12. The visualisation of the station where accomodates many under 1 minute bikes.



