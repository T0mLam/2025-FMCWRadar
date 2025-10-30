# Getting Data Off the Radar

## Two Main Methods

There are two main ways to collect data from TI mmWave radars:

### 1. Raw ADC Streaming 

- Uses a **DCA1000** capture board.
- Streams unprocessed ADC samples directly to a computer over **Ethernet**.
- All signal processing is done later in **MATLAB** or **Python**.
- Offers **maximum flexibility** to reprocess data in different ways.

**Drawbacks:**
- Very large files
- Requires extra hardware
- Higher bandwidth needs

---

### 2. Feature Vector Streaming

- The radar processes data **on-board** using its built-in hardware accelerator and MCU.
- Only **compressed feature vectors** (e.g 6 numbers per frame) are sent out via **UART** or **SPI**.
- Saves bandwidth and storage, ideal for embedded systems.

**Drawbacks:**
- Less flexibility - if processing algorithms change, the stored features may no longer match.

---

## Data Format: TLV (Type-Length-Value)

TI’s radar SDK uses a **TLV structure** for UART data:

| Field | Description |
|-------|--------------|
| **Type** | Identifies what kind of data (e.g., point cloud, features) |
| **Length** | Number of bytes in this data block |
| **Value** | The actual data (e.g., feature vector array) |

Each packet corresponds to one radar frame and includes padding so the total packet size aligns with 32 bytes (for efficient hardware transfers).

---

## Summary of Trade-offs

| Method | Data Type | Processing Location | Advantages | Disadvantages |
|---------|------------|---------------------|-------------|----------------|
| Raw ADC Streaming | Raw complex samples | Off-chip (PC) | Full control, tunable processing | High data rate, large files |
| Feature Vector Streaming | Compact feature vectors | On-chip (radar) | Low bandwidth, real-time capable | No offline reprocessing |
