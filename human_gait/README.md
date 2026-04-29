# Human Gait

Radar micro-Doppler pipeline for preprocessing JSON recordings and training a 1D CNN gait classifier.

## Layout

```text
human_gait/
├── data/
│   ├── raw/
│   └── processed/
├── output/
├── src/
│   ├── dataset.py
│   ├── preprocess.py
│   ├── train.py
│   └── models/
└── requirements.txt
```

## Setup

Run from the `human_gait` directory:

```bash
pip install -r requirements.txt
```

## Raw Data Format

`src.preprocess` expects:

```text
data/raw/<dataset>/<person>/*.json
```

Example:

```text
data/raw/ta_without_turns_3_people/
├── alina/
├── henry/
└── michal/
```

Each person folder becomes one class. Class IDs are assigned from sorted folder names.

## Preprocess

```bash
python -m src.preprocess --raw-dir data/raw/ta_without_turns_3_people --processed-dir data/processed
```

What it does:

- Optionally trims unstable frames at the start using timestamp spacing.
- Reads `frameData.microDopplerRawData` and uses the first track only.
- Drops frames with no micro-Doppler data.
- Builds sliding windows and saves tensors in `(num_windows, features, seq_len)` format.

Flags:

| Flag | Long Flag | Description | Default |
| --- | --- | --- | --- |
| `-r` | `--raw-dir` | Raw dataset root. | `data/raw/2026-01-23` |
| `-p` | `--processed-dir` | Output folder for `.pt` files. | `data/processed` |
| `-l` | `--seq-len` | Window length in frames. | `32` |
| `-s` | `--stride` | Sliding window stride. | `1` |
| `-t` | `--trim-unstable-start` | Trim unstable frames at the start. | `False` |
| `-ncd` | `--no-clear-dir` | Keep existing processed files. | `False` |
| `-sb` | `--start-bin` | First micro-Doppler bin to keep. | `0` |
| `-eb` | `--end-bin` | Last micro-Doppler bin to keep, inclusive. | `-1` |

Output:

```text
data/processed/
├── alina/
│   └── <dataset>_<file>.pt
└── henry/
```

Each `.pt` file stores `(tensor_data, label)`.

## Train

```bash
python -m src.train --data-dir data/processed --label remove_turns_3_people
```

Training uses `GaitDataset` and `src.models.cnn_1d.CNN1D`. By default it splits by file: the first `80%` of `.pt` files per class go to train, the rest to validation. Use `--no-split-by-file` to split individual windows instead.

Flags:

| Flag | Long Flag | Description | Default |
| --- | --- | --- | --- |
| `-lr` | `--learning-rate` | Optimizer learning rate. | `0.001` |
| `-e` | `--epochs` | Number of epochs. | `1000` |
| `-b` | `--batch-size` | Batch size. | `32` |
| `-wd` | `--weight-decay` | AdamW weight decay. | `0.0001` |
| `-d` | `--data-dir` | Processed data folder. | `data/processed` |
| `-t` | `--train-split` | Train fraction. | `0.8` |
| `-nspf` | `--no-split-by-file` | Split windows instead of files. | `False` |
| `-dev` | `--device` | Device, for example `cpu` or `cuda`. | `cpu` |
| `-s` | `--model-save-dir` | Output root for run artifacts. | `output/` |
|  | `--seed` | Random seed. | `42` |
| `-l` | `--label` | Suffix added to the run folder name. | `""` |

Training outputs are written to a timestamped folder under `output/` and include:

- `gait_model_weights.pt`
- `gait_model_full.pt`
- `metrics.csv`
- `accuracy.png`
- `loss.png`
- `confusion_matrix.png`
- `run_command.sh`
