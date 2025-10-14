# Key Takeaways: MM Wave Radar Human Identification

This research outlines the critical architecture and methodology needed to achieve **individual human identification** (identifying which person is present) using mmWave radar, based on the principles demonstrated by the TI Sensor-to-Cloud project.

---

## 1. Data and Feature Focus: Gait and Micro-Doppler

The system's ability to identify individuals is fundamentally tied to capturing their unique movement signature:

* **Goal:** Human Identification relies on **Gait Recognition**—analyzing the subtle, unique motion patterns (stride length, arm swing, velocity changes) that distinguish one person's walk from another's.
* **Key Feature:** The most valuable feature for identification is the **Micro-Doppler (µD) Signature**. This is the subtle frequency shift caused by smaller moving body parts (hands, feet, head) and is highly unique to the individual.
* **Data Source:** While you can use raw ADC data, most successful identification systems use **Point Cloud Data** sequences because they are sparse, smaller, and easier to process on edge devices.

---

## 2. Model Architecture and Processing Pipeline

Simple fully connected networks are generally insufficient for temporal recognition tasks like gait analysis. You need networks that can understand sequences over time.

| Stage | Data & Processing | Recommended Method/Model | Relevance to our Project |
| :--- | :--- | :--- | :--- |
| **Data Acquisition** | Raw data is processed on-chip (IWRL6432) to generate the point cloud. | **IWRL6432** (using the on-chip Hardware Accelerator) | Ensure chirp parameters give good **velocity resolution** to capture micro-Doppler shifts. |
| **Feature Extraction** | Capturing the *temporal* changes in position, velocity, and Signal-to-Noise Ratio (SNR) for each tracked person. | **PointNet** or custom **Global Embedding** layer | Crucial for extracting useful spatial features from the sparse point cloud data frame-by-frame. |
| **Classification** | The model processes the sequence of extracted features over several frames to learn the subject's identity. | **Bi-directional LSTM** (Bi-LSTM) or **Temporal CNN** (TCNN) |  Planned 1D CNN is a good next step, but pairing it with an LSTM is critical for sequence learning (gait over time). |
| **Tracking** | Must assign a unique ID to each detected object in a multi-person environment. | **Kalman Filter (Extended/Converted)** | Necessary to ensure the ML model is being fed a clean sequence of points belonging *only* to the specific person you are tracking. |

---

## 3. Practical Implementation Considerations

* **Edge Processing (On-Chip ML):** Many successful TI implementations demonstrate that the classification models (sometimes quantized to 8-bit integer format) can run **on-chip** on the integrated Arm Cortex-M4F core, which is ideal for  IWRL6432.
* **Privacy:** A significant advantage of radar over camera systems is that it maintains **human privacy**, as it does not capture visual images.
* **Accuracy vs. Scale:**  **Identification accuracy drops significantly** as the number of individuals being identified increases and as people begin to **occlude** each other (stand in front of one another).