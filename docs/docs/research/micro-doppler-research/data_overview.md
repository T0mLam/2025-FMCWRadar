# What the Data Looks Like

## From Raw Signal to Micro-Doppler Heatmap

Radar data starts as raw analog signals received from moving targets. These signals are converted to digital samples by an **Analog-to-Digital Converter (ADC)**. Each radar frame contains thousands of these complex samples.

---

### Step 1: FFT Processing

To turn those samples into meaningful data, the radar performs several **Fast Fourier Transforms (FFTs):**
- **Range FFT** - determines how far away the object is.
- **Doppler FFT** - measures how fast it’s moving toward or away from the radar.
- **Angle FFT** - estimates the direction or angle of arrival.

The result is a **radar cube**, a 3D structure containing information about:
- **Range (distance)**
- **Velocity (Doppler shift)**
- **Angle of arrival (AoA)**

Each cell  in this cube represents radar energy reflected from a specific range, direction, and velocity.

---

### Step 2: Object Tracking

The radar identifies peaks in the radar cube which are potential targets.  
Over multiple frames, it tracks the motion of these peaks, forming a “point cloud” of moving objects.



---

### Step 3: The Micro-Doppler Heatmap

After tracking an object, the radar extracts a small region around that target in each frame and records the **Doppler spectrum**

The Doppler spectrum is basically a velocity profile for the target

By combining spectra from consecutive frames, we build a **micro-Doppler vs. time heatmap**, which shows how motion changes over time.

For example :

| Frame (Time) | Velocity Range (m/s) | Energy Concentration (Signal Strength) |
|---------------|----------------------|----------------------------------------|
| Frame 1 | -2 → +2 | Strong peak near +0.8 (limb moving toward radar) |
| Frame 2 | -2 → +2 | Peak shifts to -0.6 (limb moving away) |
| Frame 3 | -2 → +2 | Peak returns to +0.9 (next limb swing) |

This repeating pattern of alternating positive and negative velocities forms the distinctive “wave” of human motion.

---

### Step 4: Visualizing the Data

If plotted as an image:
- **X-axis:** Time (in frames or seconds)
- **Y-axis:** Doppler velocity (m/s)
- **Color intensity:** How strong the reflected signal is at that speed

Bright streaks represent active motion, and darker regions correspond to stillness.  
The resulting heatmap visually captures how a person moves.
The heatmap is fairly unique to an individual. This will be the basis of how we go about identifying individuals.


