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
