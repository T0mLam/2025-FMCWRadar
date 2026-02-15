import json
import numpy as np
import matplotlib.pyplot as plt






def load_data(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def plot_subject(data, subject_name, num_frames=9):
    plt.figure(figsize=(10, 6))
    frames_plotted = 0

    for entry in data["data"]:
        frame_data = entry["frameData"]

        if "microDopplerRawData" not in frame_data:
            continue
        if len(frame_data["microDopplerRawData"]) == 0:
            continue

        md_values = np.array(frame_data["microDopplerRawData"][0])
        if len(md_values) == 0:
            continue
        sample_index = np.arange(len(md_values))
        plt.plot(sample_index, md_values)

        frames_plotted += 1
        if frames_plotted >= num_frames:
            break

    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude / Value")
    plt.title(f"Micro Doppler Raw Data - {subject_name}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()



def main():
    file_path = f"human_gait/data/raw/2026-02-11/Alina/alina5.json"

    data = load_data(file_path)

    plot_subject(data, "alina")


if __name__ == "__main__":
    main()
