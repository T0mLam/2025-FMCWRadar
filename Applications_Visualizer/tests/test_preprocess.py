import sys
import os
import json
import pytest
import torch
import numpy as np
import shutil

# Ensure the module is on the path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

HUMAN_GAIT_SRC = os.path.join(ROOT, "human_gait","src")
if HUMAN_GAIT_SRC not in sys.path:
    sys.path.insert(0, HUMAN_GAIT_SRC)

from preprocess import get_stable_start_index, process_data

# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def stable_timestamps():
    """Timestamps that are stable from the start at ~9 FPS (111ms intervals)."""
    return [i * 111 for i in range(50)]

@pytest.fixture
def unstable_then_stable_timestamps():
    """Timestamps that start unstable then become stable."""
    unstable = [0, 50, 300, 350, 800]  # irregular intervals
    stable_start = unstable[-1]
    stable = [stable_start + i * 111 for i in range(1, 50)]
    return unstable + stable

@pytest.fixture
def raw_data_dir(tmp_path):
    """
    Create a temporary raw data directory with two classes
    and mock JSON data files.
    """
    raw_dir = tmp_path / "raw"

    for class_name in ["alice", "bob"]:
        class_dir = raw_dir / class_name
        class_dir.mkdir(parents=True)

        # Create two JSON files per class
        for file_idx in range(2):
            data = create_mock_json(num_frames=50, num_bins=64)
            file_path = class_dir / f"recording_{file_idx}.json"
            with open(file_path, "w") as f:
                json.dump(data, f)

    return str(raw_dir)

@pytest.fixture
def processed_dir(tmp_path):
    """Create a temporary output directory."""
    return str(tmp_path / "processed")

# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def create_mock_json(num_frames=50, num_bins=64, fps=9):
    """Create a mock JSON structure matching the expected format."""
    interval = 1000 / fps  # ~111ms
    data = {"data": []}

    for i in range(num_frames):
        frame = {
            "timestamp": int(i * interval),
            "frameData": {
                "microDopplerRawData": [
                    [float(np.random.randn()) for _ in range(num_bins)]
                ]
            }
        }
        data["data"].append(frame)

    return data

def create_mock_json_with_gaps(num_frames=50, num_bins=64, gap_indices=None):
    """Create mock JSON where some frames have no micro-doppler data."""
    if gap_indices is None:
        gap_indices = []

    interval = 1000 / 9
    data = {"data": []}

    for i in range(num_frames):
        if i in gap_indices:
            frame_data = {"microDopplerRawData": []}
        else:
            frame_data = {
                "microDopplerRawData": [
                    [float(np.random.randn()) for _ in range(num_bins)]
                ]
            }

        frame = {
            "timestamp": int(i * interval),
            "frameData": frame_data
        }
        data["data"].append(frame)

    return data

# ─────────────────────────────────────────────
# get_stable_start_index Tests
# ─────────────────────────────────────────────

def test_stable_from_start(stable_timestamps):
    """If timestamps are stable from the start, index should be 0."""
    index = get_stable_start_index(stable_timestamps)
    assert index == 0

def test_unstable_then_stable(unstable_then_stable_timestamps):
    """Should return an index after the unstable region."""
    index = get_stable_start_index(unstable_then_stable_timestamps)
    assert index > 0

def test_empty_timestamps():
    """Should return 0 for empty timestamps."""
    index = get_stable_start_index([])
    assert index == 0

def test_too_few_timestamps():
    """Should return 0 if fewer timestamps than stable_count."""
    index = get_stable_start_index([0, 111, 222])
    assert index == 0

def test_completely_unstable_timestamps():
    """Should return 0 if no stable region is found."""
    timestamps = [0, 500, 600, 2000, 2010, 5000, 5500, 9000]
    index = get_stable_start_index(timestamps)
    assert index == 0

def test_custom_fps():
    """Should work with a different target FPS."""
    # 20 FPS = 50ms intervals
    timestamps = [i * 50 for i in range(20)]
    index = get_stable_start_index(timestamps, target_fps=20)
    assert index == 0

def test_custom_stable_count():
    """Should respect custom stable_count parameter."""
    timestamps = [i * 111 for i in range(10)]
    index = get_stable_start_index(timestamps, stable_count=3)
    assert index == 0

def test_stable_count_higher_than_frames():
    """Should return 0 if stable_count exceeds frame count."""
    timestamps = [i * 111 for i in range(5)]
    index = get_stable_start_index(timestamps, stable_count=10)
    assert index == 0

# ─────────────────────────────────────────────
# process_data Tests
# ─────────────────────────────────────────────

def test_preprocess_creates_output_dir(raw_data_dir, processed_dir):
    """Verify the processed directory is created."""
    process_data(raw_data_dir, processed_dir, seq_len=10, stride=1)
    assert os.path.exists(processed_dir)

def test_preprocess_creates_class_dirs(raw_data_dir, processed_dir):
    """Verify subdirectories are created for each class."""
    process_data(raw_data_dir, processed_dir, seq_len=10, stride=1)

    assert os.path.exists(os.path.join(processed_dir, "alice"))
    assert os.path.exists(os.path.join(processed_dir, "bob"))

def test_preprocess_creates_pt_files(raw_data_dir, processed_dir):
    """Verify .pt files are created."""
    process_data(raw_data_dir, processed_dir, seq_len=10, stride=1)

    pt_files = []
    for root, dirs, files in os.walk(processed_dir):
        for f in files:
            if f.endswith(".pt"):
                pt_files.append(os.path.join(root, f))

    assert len(pt_files) > 0, "No .pt files were created"

def test_tensor_shape(raw_data_dir, processed_dir):
    """Verify the saved tensors have the correct shape."""
    seq_len = 10
    num_bins = 64
    process_data(raw_data_dir, processed_dir, seq_len=seq_len, stride=1)

    # Load the first .pt file found
    for root, dirs, files in os.walk(processed_dir):
        for f in files:
            if f.endswith(".pt"):
                tensor_data, label = torch.load(os.path.join(root, f))

                # Shape should be (batch, num_bins, seq_len)
                assert tensor_data.dim() == 3
                assert tensor_data.shape[1] == num_bins
                assert tensor_data.shape[2] == seq_len
                return

    pytest.fail("No .pt files found to check shape")

def test_labels_are_correct(raw_data_dir, processed_dir):
    """Verify labels are assigned correctly (alphabetical order)."""
    process_data(raw_data_dir, processed_dir, seq_len=10, stride=1)

    # alice=0, bob=1 (alphabetical)
    for root, dirs, files in os.walk(processed_dir):
        for f in files:
            if f.endswith(".pt"):
                _, label = torch.load(os.path.join(root, f))

                if "alice" in root:
                    assert label == 0
                elif "bob" in root:
                    assert label == 1

def test_stride_counts(raw_data_dir, processed_dir):
    """Verify that a larger stride produces fewer samples."""
    process_data(raw_data_dir, processed_dir, seq_len=10, stride=1, clear_dir=True)
    count_stride_1 = count_total_samples(processed_dir)

    process_data(raw_data_dir, processed_dir, seq_len=10, stride=5, clear_dir=True)
    count_stride_5 = count_total_samples(processed_dir)

    assert count_stride_1 > count_stride_5, "Stride of 1 should produce more samples than stride of 5"

def test_process_data_with_gaps(tmp_path):
    """Verify windows containing gaps are dropped."""
    raw_dir = tmp_path / "raw_gaps"
    class_dir = raw_dir / "person_a"
    class_dir.mkdir(parents=True)
    processed_dir = str(tmp_path / "processed_gaps")

    # Create data with gaps at frames 10-15
    data = create_mock_json_with_gaps(
        num_frames=50,
        num_bins=64,
        gap_indices=[10, 11, 12, 13, 14, 15]
    )

    with open(class_dir / "recording.json", "w") as f:
        json.dump(data, f)

    process_data(str(raw_dir), processed_dir, seq_len=10, stride=1)

    # Should still produce some valid windows (before and after the gap)
    total = count_total_samples(processed_dir)
    assert total > 0

    # But fewer than if there were no gaps
    raw_dir_clean = tmp_path / "raw_clean"
    class_dir_clean = raw_dir_clean / "person_a"
    class_dir_clean.mkdir(parents=True)
    processed_dir_clean = str(tmp_path / "processed_clean")

    clean_data = create_mock_json(num_frames=50, num_bins=64)
    with open(class_dir_clean / "recording.json", "w") as f:
        json.dump(clean_data, f)

    process_data(str(raw_dir_clean), processed_dir_clean, seq_len=10, stride=1)
    total_clean = count_total_samples(processed_dir_clean)

    assert total_clean > total

def test_process_data_clear_dir(raw_data_dir, tmp_path):
    """Verify clear_dir=True removes old files."""
    processed_dir = str(tmp_path / "processed_clear")
    os.makedirs(processed_dir, exist_ok=True)

    # Create a dummy file
    dummy_file = os.path.join(processed_dir, "old_file.txt")
    with open(dummy_file, "w") as f:
        f.write("old data")

    process_data(raw_data_dir, processed_dir, seq_len=10, stride=1, clear_dir=True)

    assert not os.path.exists(dummy_file)
# ─────────────────────────────────────────────
# Utility function for counting samples
# ─────────────────────────────────────────────

def count_total_samples(processed_dir):
    """Count total samples across all .pt files."""
    total = 0
    for root, dirs, files in os.walk(processed_dir):
        for f in files:
            if f.endswith(".pt"):
                tensor_data, _ = torch.load(os.path.join(root, f))
                total += tensor_data.shape[0]
    return total