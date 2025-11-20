---
slug: 2025-10-24-client-meeting
title: Client Meeting - 24/10
authors: [dan] 
tags: [client]
---

*Notes from our client meeting*

**Date:** 24-10-2025 <br />
**Time:** 9:00 - 10:00 <br />
**Team:** Alina Zubova, Dan Robb, Henry Edwards, Talal Aljallal, Tom Lam, Michal Berkasiuk  <br />

<!-- truncate -->
## Key Project Learnings & Context 

1.  **Filter Gap (Last Year):** A critical lesson from the previous project was the **absence of a final filter** on the results. This suggests a major area for us to improve upon in our pipeline.
2.  **AppImage Binaries:** These are essentially the **compiled code for the radar chip**. Their job is to convert the raw radar information into the specific **data format** we need for processing (e.g., point cloud).
3.  **Chirp Configuration:** This refers to the specific kind of **chirps** (radar signals) the hardware sends out, which directly affects measurements like **range**. *Good news: it's built into the chip, so we shouldn't need to worry about configuring it ourselves.*

---

## Minimal Viable Product (MVP) Focus 

The MVP goal for this term is two-fold:

1.  **Replication + Improvement:** We need to **reproduce the previous team's output** but rely *only* on the radar unit for the data source.
2.  **ML Demo:** Get a basic demonstration working that involves **training a model**. This means we need to immediately focus on **dataset handling and collection**.

### ML System Requirements
* The trained **model should be running locally** on our machines.
* The model must be built using the **PyTorch framework**.

---

## Data Collection & Visualisation Strategy 

### Data Types
The raw data we collect will be a mix of:
* **Point Cloud Data:** A set of 3D points representing detected objects.
* **Tracks Data:** Time-series data tracking the movement of detected objects.

### Visualiser Goal
If we develop a visualiser, a high-value feature would be to **superimpose the radar information** (e.g., detected points/boxes) directly **onto the live video feed** for immediate context and verification.

### Recording Specifics
1.  **Radar Height:** Keep the radar unit **fairly low** during recording, roughly 1m off the ground.
2.  **Movement:** When collecting data, ensure people **walk right-to-left AND left-to-right** in front of the radar.
3.  **Final Classification Filter:** We can use data like **height and speed** as a crucial final filter to help **classify** or distinguish different objects/people.

---
