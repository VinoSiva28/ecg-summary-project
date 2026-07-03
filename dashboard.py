import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
from report import generate_pdf

st.title("ECG Analysis Dashboard")

uploaded_file = st.file_uploader("Upload your ECG CSV", type="csv")

if uploaded_file is not None:  
    raw = pd.read_csv(uploaded_file)
    time = raw['time_seconds']
    voltage = raw['voltage_raw']

    fs = len(time) / (time.iloc[-1] - time.iloc[0])
    even_time = np.arange(len(time)) / fs
    voltage_array = voltage.values.astype(float)

    # bandpass filter function
    def bandpass_filter(data, lowcut, highcut, fs, order=4):
        nyq = fs / 2
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, data)

    filtered = bandpass_filter(voltage_array, 0.5, 40.0, fs)

    # peaks
    peaks, _ = find_peaks(filtered, height=np.percentile(filtered, 85), distance=fs*0.4)

    # RR and BPM
    rr = np.diff(even_time[peaks])
    bpm_per_beat = 60 / rr
    beat_times = even_time[peaks[1:]]

    # irregularity
    rr_median = np.median(rr)
    irregular_intervals = [i for i in rr if abs(i - rr_median) / rr_median > 0.2]

    # signal quality
    noise = voltage_array - filtered
    snr = np.std(filtered) / np.std(noise)
    if snr > 2:
        quality = "Good"
    elif snr > 1:
        quality = "Fair"
    else:
        quality = "Poor"

    st.subheader("Heart Rate Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average BPM", f"{bpm_per_beat.mean():.0f}")
    col2.metric("Min BPM", f"{bpm_per_beat.min():.0f}")
    col3.metric("Max BPM", f"{bpm_per_beat.max():.0f}")
    col4.metric("Beats Detected", len(peaks))

    st.subheader("Raw ECG Signal")
    fig1, ax1 = plt.subplots(figsize=(14, 3))
    ax1.plot(even_time, voltage_array, lw=0.5)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("ADC counts")
    st.pyplot(fig1)

    st.subheader("Filtered ECG with R-peaks")
    fig2, ax2 = plt.subplots(figsize=(14, 3))
    ax2.plot(even_time, filtered, lw=0.6, color='orange')
    ax2.plot(even_time[peaks], filtered[peaks], 'rv', ms=6, label='R-peaks')
    ax2.set_xlabel("Time (s)")
    ax2.legend()
    st.pyplot(fig2)

    st.subheader("RR Intervals over time")
    fig3, ax3 = plt.subplots(figsize=(14, 3))
    ax3.plot(beat_times, rr * 1000, marker='o', lw=1.2, color='mediumpurple')
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("RR interval (ms)")
    st.pyplot(fig3)

    st.subheader("Signal Flags")
        
    if quality == "Good":
        st.success(f"Signal Quality: {quality} (SNR: {snr:.2f})") #makes a green box
    elif quality == "Fair":
        st.warning(f"Signal Quality: {quality} (SNR: {snr:.2f})") #yellow box
    else:
        st.error(f"Signal Quality: {quality} (SNR: {snr:.2f})") #red box


    if len(irregular_intervals) == 0:
        st.success(f"Rhythm: Regular — no irregular intervals flagged")
    else:
        st.warning(f"Rhythm: {len(irregular_intervals)} irregular interval(s) flagged")


    if bpm_per_beat.mean() < 50 or bpm_per_beat.mean() > 120:
        st.error(f"Heart rate out of expected range: {bpm_per_beat.mean():.0f} bpm")
    else:
        st.success(f"Heart rate within normal range: {bpm_per_beat.mean():.0f} bpm")

    st.caption("Note: This tool flags patterns only and does not provide medical diagnosis.")

    st.subheader("Export Report")
    if st.button("Generate PDF Report"):
        pdf_buf = generate_pdf(even_time, voltage_array, filtered, peaks, rr, bpm_per_beat, beat_times, irregular_intervals, snr, quality)
        st.download_button(
            label="Download PDF",
            data=pdf_buf,
            file_name="ecg_report.pdf",
            mime="application/pdf"
        )