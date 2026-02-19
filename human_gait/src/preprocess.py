import json 
import torch 
import glob
import os 
import numpy as np 
import argparse
import shutil 

def get_stable_start_index(timestamps, target_fps=9, tolerance=0.2, stable_count=5):
    """
    Return the stable index where the recording becomes stable.
    Stable = stable_count consecutive frames with time diff within 20% of the target_interval.  
    """
    if len(timestamps) < stable_count:
        return 0
    
    target_interval = 1000 / target_fps
    min_interval = target_interval * (1 - tolerance)
    max_interval = target_interval * (1 + tolerance)

    consecutive_stable_frames = 0

    diffs = np.diff(timestamps)

    for i, diff in enumerate(diffs):
        if min_interval <= diff <= max_interval:
            consecutive_stable_frames += 1

            if consecutive_stable_frames >= stable_count:
                return max(0, i - stable_count + 1)
                
        else:
            consecutive_stable_frames = 0

    return 0

def process_data(raw_dir, processed_dir, seq_len=32, stride=1, trim_unstable_start=False, clear_dir=True, start_bin=0, end_bin=-1):
    """
    Parses JSON, removes unstable frames at the start of each file, filters human using ClassificationDecision, 
    and saves continuous sliding windows of sequences without gaps in Timestamp.
    """
    if clear_dir and os.path.exists(processed_dir):
        shutil.rmtree(processed_dir)
    os.makedirs(processed_dir, exist_ok=True)

    # Map names to integers: {'alina': 0, 'michal': 1}
    classes = {name: i for i, name in enumerate(sorted(os.listdir(raw_dir)))} 
    print(f"Classes: {classes} | Window size: {seq_len} frames | Stride: {stride}")

    for class_name, label in classes.items():
        # Create a output dir
        class_out_dir = os.path.join(processed_dir, class_name)
        os.makedirs(class_out_dir, exist_ok=True)

        # Match all .json files
        files = glob.glob(f"{raw_dir}/{class_name}/*.json")
        total_sample_count = 0

        print(f"\nScanned {class_name}/: found {len(files)} JSON files")

        for file_path in files:
            file_name = os.path.basename(file_path).replace(".json", "")

            with open(file_path, "r") as f:
                data = json.load(f)

            # Step 1: Start parsing the data from the first stable index (optional)
            start_idx = 0
            if trim_unstable_start:
                timestamps = [frame["timestamp"] for frame in data["data"]]
                start_idx = get_stable_start_index(timestamps)

            stable_frames = data["data"][start_idx:]
            full_sequence = []

            # Step 2: Take the first object by default (ignore classification output)
            for frame in stable_frames:
                frame_data = frame["frameData"]

                raw_dopplers = frame_data.get("microDopplerRawData", [])
                is_valid_human = len(raw_dopplers) > 0

                # Append the bin data or None to mark a gap
                bin_slice = slice(start_bin, (end_bin + 1) or None)
                full_sequence.append(raw_dopplers[0][bin_slice] if is_valid_human else None)

            if not full_sequence:
                continue

            # Step 3: Sliding window to generate seq_len sequences
            chunks = []

            for i in range(0, len(full_sequence) - seq_len + 1, stride):
                # Window shape: (seq_len, 64)
                raw_window = full_sequence[i: i + seq_len]

                # Drop window if any frame is None
                if any(frame is None for frame in raw_window):
                    continue

                # Chunk: (Channel, Time) -> (64, seq_len)
                window_np = np.array(raw_window, dtype=np.float32)
                chunks.append(window_np.T)

            if chunks:
                # Stack: (Batch, 64, 32)
                tensor_data = torch.tensor(np.array(chunks), dtype=torch.float32)
                # Save tensors
                save_path = os.path.join(class_out_dir, f"{os.path.basename(raw_dir)}_{file_name}.pt")
                torch.save((tensor_data, label), save_path)

                print(f"Saved {file_name}: {tensor_data.shape}")
                total_sample_count += tensor_data.shape[0]
            
        print(f"--- Total samples in {class_name}/: {total_sample_count} ---")

def parse_args():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    default_raw  = os.path.join(project_root, "data", "raw", "2026-01-23")
    default_proc = os.path.join(project_root, "data", "processed") 
    default_seq_len = 32
    default_stride = 1
    default_start_bin = 0
    default_end_bin = -1

    parser = argparse.ArgumentParser(description="Process micro-doppler JSON into training sequences.")
    parser.add_argument("-r", "--raw-dir", type=str, default=default_raw, help=f"Path to raw data folder (default: {default_raw})")
    parser.add_argument("-p", "--processed-dir", type=str, default=default_proc, help=f"Path to output processed data folder (default: {default_proc})")
    parser.add_argument("-l", "--seq-len", type=int, default=default_seq_len, help=f"Sliding window length in frames (default: {default_seq_len})")
    parser.add_argument("-s", "--stride", type=int, default=default_stride, help=f"Sliding window stride in frames (default: {default_stride})")
    parser.add_argument("-t", "--trim-unstable-start", action="store_true", default=False, help="Trim unstable frames at the start of each file (default: False)")
    parser.add_argument("-ncd", "--no-clear-dir", dest="clear_dir", action="store_false", help="Do not delete processed-dir before writing outputs")
    parser.add_argument("-sb", "--start-bin", type=int, default=default_start_bin, help=f"Inclusive starting feature in the micro doppler array (default: {default_start_bin})")
    parser.add_argument("-eb", "--end-bin", type=int, default=default_end_bin, help=f"Inclusive ending feature in the micro doppler array (default: {default_end_bin})")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    process_data(
        args.raw_dir,
        args.processed_dir,
        seq_len=args.seq_len,
        stride=args.stride,
        trim_unstable_start=args.trim_unstable_start,
        clear_dir=args.clear_dir,
        start_bin=args.start_bin,
        end_bin=args.end_bin,
    )
    
