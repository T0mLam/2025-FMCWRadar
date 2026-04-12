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