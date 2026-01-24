# Human Gait Recognition with Radar Micro-Doppler

This project implements a deep learning pipeline for human gait classification using 60GHz mmWave radar data. It utilizes a 1D Convolutional Neural Network (CNN) to classify individuals based on their unique micro-Doppler signatures.

## Project Structure

```
human_gait/
├── configs/               # Configuration files
├── data/
│   ├── raw/               # Original JSON radar recordings
│   └── processed/         # Preprocessed .pt tensors for training
├── src/
│   ├── dataset.py         # PyTorch Dataset class
│   ├── preprocess.py      # Data cleaning and windowing script
│   ├── train.py           # Training loop
│   └── models/            # CNN architecture definitions
├── README.md
└── requirements.txt

```

## Data Preprocessing

The raw radar data should be stored in hierarchical JSON format. To prepare this data for efficient training, we run a preprocessing pipeline that converts raw JSONs into optimized PyTorch tensors.

```
human_gait/
├── data/
│   ├── raw/               # <-- PLACE UNPROCESSED DATA HERE
│   │   └── 2026-01-23/    # (Drag and drop your date folder here)
│   │       ├── alina/
│   │       │   ├── replay_1.json
│   │       │   ├── replay_2.json
│   │       │   ├── replay_3.json
│   │       │   └── ... 
│   │       └── michal/
│   │           ├── replay_1.json
│   │           ├── replay_2.json
│   │           ├── replay_3.json
│   │           └── ... 
│   └── processed/         # Script outputs .pt tensors here
└── ...

```

### Key Processing Steps

The `src/preprocess.py` script performs the following critical operations:

1. **Stability Gating (Warm-up Trim):**
* The data recorder often produces unstable frame rates during the first few seconds of recording.
* The script calculates frame timestamp differences and automatically detects the "stable start index" where the frame rate settles to ~9 FPS.
* Frames prior to this stability point are discarded.

2. **Human Filtering:**
* The radar tracks multiple objects. We strictly filter for the first Human class.
* It checks the `ClassificationDecision` field in the raw data.

3. **Continuous Sliding Window:**
* The continuous data stream is sliced into overlapping windows of **32 frames** (approx. movement).
* **Stride = 1:** The window slides one frame at a time to maximize the number of training samples.
* *Any window containing a "gap" (from filtering step #2) is strictly discarded. This ensures the model never sees discontinuous physics (e.g., a person "teleporting" due to missing frames).

4. **Tensor Output:**
* Each valid window is transposed to shape `(Channels, Time)` -> `(64, 32)` to match PyTorch's `Conv1d` input requirement.
* Data is saved as compressed `.pt` files (Tensors), speeding up training loading times by over 100x compared to parsing JSONs on the fly.



### Usage

To run the preprocessing script:

```bash
# From the project root directory (path/to/human_gait)
python -m src.preprocess

```

**Configuration:**
You can modify the following parameters in `src/preprocess.py`:

* `seq_len`: Length of the time window (Default: 32 frames).
* `target_fps`: Expected frame rate for stability check (Default: 9 FPS).
* `raw_dir`: Path to the directory storing the raw data (Default: `path/to/human_gait/data/raw/2026-01-23`).
* `processed_dir`: Path to the directory storing the raw data (Default: `path/to/human_gait/data/processed`).


### Output

Processed data is saved to `data/processed/` organized by class folders. Each `.pt` file contains a tuple `(data_tensor, label)`.

```text
data/processed/
├── alina/
│   ├── replay_1.pt   # Tensor shape: (N_windows, 64, 32)
│   ├── replay_2.pt
│   └── ...
└── michal/
    ├── replay_1.pt
    └── ...
```
