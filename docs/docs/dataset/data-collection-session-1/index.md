---
title: "Data Collection Session 1"
---

# mmWave Radar Sensor Data Collection Session 1: Gait Recognition

## 1. Overview

**Project Name:** mmWave Radar Gait Recognition (PoC) <br />
**Data Collection Session:** 1st Session <br />
**Date:** Fri 23 Jan <br />
**Location:** Physics Building G12 Mott Lecture Theatre 

---

## 2. Purpose and Scope

**Purpose:**
To collect high quality micro-Doppler radar signatures of human walking patterns (gait). This data will be used to train and validate a 1D Convolutional Neural Network (CNN) for person identification. The goal is to distinguish between specific individuals based solely on the unique velocity patterns of their limb movements.

**Scope:**

* **Participants:** 2 Subjects (Alina, Michal).
* **Activity:** Walking perpendicular to the radar (Left -> Right and Right -> Left) at around **3 meters away from the sensor**.
* **Duration:** Data is segmented into **around 5 minute clips** per json file.
* **Target Volume:** 1 clip per participant. 

---

## 3. Setup & Configuration

### **Hardware Configuration**

* **Sensor Model:** [IWRL6432](https://www.ti.com/product/IWRL6432)
* **Mounting:**
* **Height:** **1.0m – 1.2m** (Chest/Waist height is optimal for gait; 1.5m is acceptable but lower captures legs better).
* **Orientation:** Standard (Horizontal) is typically preferred for gait to maximize field of view.


* **Capture Zone:**
* **Walk Path:** A straight line marked on the floor, **3.0 meters** from the radar.
* **Walk Width:** Markers placed 2.5m to the left and 2.5m to the right of the center (5m total path).



### **Data Output**

* **Format:** `.json` (JSON) 

---

## 4. Participant Details

| Paricipant ID | Name | Height | Role |
| --- | --- | --- | --- |
| **P0** | Alina | around 170 cm | Target Class 0 |
| **P1** | Michal | around 180 cm | Target Class 1 |

---

## 5. Activity Log 

The data collection duration is measured in minutes, 5 per person.

| Set ID | Participant | Target minutes | Status |
| --- | --- | --- | --- |
| **Set 01** | **Alina** | 5 | [x] |
| **Set 02** | **Michal** | 5 | [x] |

---

## 6. Procedure (The 3-Second Loop)

1. **Get Ready:** Participant stands at the "Start Marker".
2. **Trigger:** Operator starts recording.
3. **Action:** Participant walks at a normal, comfortable pace along the 3m tape line.
4. **Cut:** Recording stops after **5 minutes** manually by operator.

---

## 7. Quality Control Checklist

* [x] **Gait Cycle Check:** Does the spectrogram show at least 2 clear "flashes" (limb swings)?
* [x] **Distance:** Is the participant strictly following the 3m line? (Drifting closer changes the signal intensity).
* [x] **Fatigue:** If participant starts limping or walking lazily, take a break. The model needs "natural" gait.

---

## 8. Next Steps

* **Preprocessing:** Convert Micro-Doppler data from JSON to numpy.
* **Model training:** Implement a script to transform the data into the shape of model input.