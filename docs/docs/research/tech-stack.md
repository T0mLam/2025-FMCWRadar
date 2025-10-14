# Tech Stack

This page proposes the technology stack and frameworks used for the FMCW radar project

## Model Training

| **Layer**                                 | **Component / Tool**                             | **Purpose / Functionality**                                                 | **Language / Framework**            |
| ----------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------- | ----------------------------------- |
| 🛰️ **Data Acquisition**                  | **TI mmWave Radar (IWR6843 / IWRL6432)**          | Captures FMCW radar signals (range–Doppler–angle) for human gait signatures | TI Firmware / C                     |
|                                           | **mmWave SDK / Demo Visualizer**                 | TI tool for configuring radar profiles and exporting raw data               | TI SDK / C / UART                   |
|                                           | **UART Manager**                                  | Streams radar frames to PC for logging and preprocessing                    | Python / C++ (serial)              |
| ⚙️ **Preprocessing & Feature Extraction** | **Radar Signal Processor**                       | Parses ADC/point cloud frames, applies range–Doppler FFTs                   | Python (NumPy, SciPy)               |
|                                           | **Micro-Doppler Feature Generator**              | Converts radar cubes into spectrograms or time–frequency maps               | Python (NumPy, Matplotlib)           |
|                                           | **Data Labeling / Metadata Management**          | Annotates participant sessions, adds YAML/JSON metadata                     | Python                               |
| 💾 **Dataset Management**                 | **Git + GitHub Repo (`spe-uob/2025-FMCWRadar`)** | Stores code, configs, and versioned dataset metadata                        |  Git / GitHub                      |
| 🧠 **Model Training & Evaluation**        | **PyTorch**                                      | CNN model training and inference on ?                                       | Python / PyTorch                    |
|                                           | **Hydra**                                        | Config management for experiments and hyperparameter sweeps                 | Python (hydra-core)                 |
|                                           | **TensorBoard**                                  | Visualize training metrics, losses, and comparisons                         | TensorBoard                           |
|                                           | **ONNX + ONNX Runtime**                          | Model export and post-training quantization                                 | Python (onnxruntime)                |
| ⚡ **Deployment & Runtime**                | ?                                               | No idea                                                                       | ?                                    |



## Radar Data Visualizer

| Layer                  | Technology                                                              | Purpose                                                                     |
| ---------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Sensor Layer**       | TI IWR6843 / IWRL6432                                                    | Produces real-time radar frames                                             |
| **UART Parsing Layer** | **Python + PySerial + threading**                                       | Reads binary frames and emits structured radar data                         |
| **Frame Parsing**      | Custom parser (`parse_frame.py`) + NumPy                                | Converts binary stream → range, doppler, point cloud                        |
| **Backend Server**     | **FastAPI** + **WebSocket** + **PyTorch/ONNX Runtime** + **Hydra**      | Receives parsed data, runs model inference (if needed), streams to frontend |
| **Frontend**           | **React.js** + **Three.js** + **TailwindCSS / ShadcnUI** | Visualizes live point clouds, classification labels, and confidence         |
| **Communication**      | **WebSocket** (`ws://localhost:8000/ws/radar`)                          | Real-time stream between backend ↔ frontend                                 |
| **Environment**        | **Docker Compose with GPU**                                             | Containerized backend + frontend, GPU acceleration for inference            |
| **Monitoring**         | TensorBoard                                                             | Track FPS, latency, model confidence, etc.                                  |
