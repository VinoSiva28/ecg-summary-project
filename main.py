
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

raw=pd.read_csv('ecg_recording-2.csv')
time=raw['time_seconds']
voltage=raw['voltage_raw']
voltage_array = voltage.values.astype(float)
fs = len(time) / (time.iloc[-1] - time.iloc[0])  # Calculate sampling frequency
even_time = np.arange(len(time)) / fs  # Create an evenly spaced time axis


def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = fs / 2                                    # Nyquist frequency
    low = lowcut / nyq                              # normalize to 0-1 range
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band') # design the filter
    return filtfilt(b, a, data)                     # apply it 

filtered = bandpass_filter(voltage_array, 0.5, 40.0, fs)
r_peaks,_=find_peaks(filtered,height=np.percentile(filtered,85),distance=int(fs*0.4)) #find peaks that are above 85th percentile, at least 0.4 seconds apart, and have a prominence of at least 0.5

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=True) #shows 2 plots that share the same axis
ax1.plot(even_time, voltage_array, lw=0.5, label='Raw')
ax1.set_title('Raw Signal')
ax2.plot(even_time, filtered, lw=0.5, color='orange', label='Filtered')
ax2.set_title('Filtered (0.5–40 Hz)')
ax2.set_xlabel('Time (s)')
ax2.plot(even_time[r_peaks],filtered[r_peaks],'ro',label='R-peaks')
plt.tight_layout()
plt.savefig("results/raw_and_filtered.png", dpi=300)
plt.show()

rr=np.diff(time[r_peaks])
print(rr)
bpm=60/rr
bpm_per_beat= np.delete(bpm, [0, 1, 2]) # Deletes indices 0, 1, and 2 since it is out of range and noise
print(bpm_per_beat)
max=print(np.max(bpm_per_beat))
min=print(np.min(bpm_per_beat))
mean=print(np.mean(bpm_per_beat))
count=print(len(bpm_per_beat))

plt.plot(rr * 1000, marker='o') 
plt.xlabel('Number of beats')
plt.ylabel('RR(ms)')
plt.savefig("results/rr_intervals.png", dpi=300)
plt.show()

#irregular flagging
rr_median=np.median(rr)
irregular_intervals=[]
for i in rr:
    if abs(rr_median-i)/rr_median>0.2:
        irregular_intervals.append(i)
print(irregular_intervals)

noise = voltage_array - filtered  # what the filter removed
signal_power = np.std(filtered)    # how much real signal there is
noise_power = np.std(noise)         # how much noise there was
snr = signal_power / noise_power  # ratio

if snr > 2:
    quality = "Good"
elif snr > 1:
    quality = "Fair"
else:
    quality = "Poor"
print(f"Signal quality: {quality} (SNR: {snr:.2f})")

#heart rate range analysis
if bpm_per_beat<50 or bpm_per_beat>120:
    print("Warning: Abnormal heart rate detected.")
else:
    print("within normal range")




