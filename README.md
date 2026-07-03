# ECG Monitoring System with Embedded Signal Acquisition and Biomedical Rhythm Analysis

This is a low-cost portable ECG monitoring prototype that records heart electrical activity using an ECG sensor and microcontroller. The system collects ECG data, sends it to a computer through USB (and possibly Bluetooth later), processes the signal in Python, detects heartbeats, calculates heart rate, flags irregular beat intervals, visualizes the results on a dashboard, and generates a PDF summary report.

---

## Overview

```
AD8232 + ESP32 (hardware)
        ↓
Raw ECG data over Serial → CSV (Python)
        ↓
Signal cleaning (filtering, smoothing, baseline correction)
        ↓
R-peak detection
        ↓
Heartbeat & rhythm analysis (BPM, R-R intervals, signal quality)
        ↓
Irregularity flagging
        ↓
Streamlit dashboard + PDF report export
```

## Main Features

- Records ECG signal using an AD8232 ECG sensor.
- Uses an ESP32 microcontroller to read analog ECG data.
- Sends ECG data to a laptop through USB serial communication.
- Saves ECG recordings as CSV files.
- Filters and cleans the ECG signal.
- Detects R-peaks, which represent heartbeats.
- Calculates heart rate in BPM.
- Calculates R-R intervals between beats.
- Flags possible irregular rhythm patterns.
- Displays ECG data and metrics on a dashboard.
- Generates a PDF report with plots and summary results.
- Can later be upgraded to Bluetooth streaming and a physical case.

## Repository Contents

| File | Description |
|---|---|
| `main.py` | Entry point — runs the ECG processing pipeline (loading, filtering, peak detection, analysis). |
| `report.py` | Generates the PDF summary report from a processed recording. |
| `dashboard.py` | Streamlit dashboard for visualizing raw/filtered ECG signals and analysis results. |
| `ecg_recording-2.csv` | Sample ECG recording (time/voltage pairs) used for testing the pipeline. |
| `results/` | Output directory for generated plots, summaries, and reports. |

---

## Hardware Setup

- ESP32 development board
- AD8232 ECG sensor module
- ECG electrodes and leads
- USB cable for ESP32 ↔ laptop connection

**Wiring:**
```
AD8232 3.3V  → ESP32 3.3V
AD8232 GND   → ESP32 GND
AD8232 OUT   → ESP32 ADC1 analog pin
AD8232 LO+   → ESP32 digital pin
AD8232 LO-   → ESP32 digital pin
```

## Software Requirements

- Python 3.x
- Arduino IDE (for flashing the ESP32)
- Python packages: `pandas`, `numpy`, `scipy`, `matplotlib`, `streamlit`, `reportlab`
- (For capturing data from the ESP32 over serial, a package like `pyserial` is also needed.)

## Usage

The pipeline expects a CSV recording with two columns: `time_seconds` and `voltage_raw` (an example is provided in `ecg_recording-2.csv`).

```bash
# Run the core analysis pipeline on a recording (reads ecg_recording-2.csv, saves plots to results/)
python main.py

# Launch the interactive dashboard (upload a CSV recording, view live analysis, export PDF)
streamlit run dashboard.py
```

The dashboard applies a 0.5–40 Hz bandpass filter to clean the signal, detects R-peaks, computes BPM/RR intervals, flags irregular intervals (RR deviating more than 20% from the median) and low signal quality, and can generate a PDF report on demand via `report.py`.

## Example Output

```
Recording Length: 30.0 seconds
Average BPM: 79
Minimum BPM: 67
Maximum BPM: 96
Beats Detected: 40
Irregular Intervals: 0
Signal Quality: Good
SNR: 4.38
```

Sample report includes plots for the raw ECG signal, the filtered ECG with detected R-peaks, and R-R intervals over time.
