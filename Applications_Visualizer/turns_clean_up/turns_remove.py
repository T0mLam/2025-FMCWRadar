import json
import os
import glob

#Change this path to the data folder one
input_folder = '/home/catbert21/uni/TI/2025-FMCWRadar/Applications_Visualizer/binData/Data'
output_folder = 'output_walking_only'  # will be created next to the script

min_walking_speed = 0.2

os.makedirs(output_folder, exist_ok=True)

json_files = glob.glob(os.path.join(input_folder, '*.json'))

if not json_files:
    print(f"No .json files found in: {input_folder}")
else:
    for input_filepath in json_files:
        filename = os.path.basename(input_filepath)
        output_filepath = os.path.join(output_folder, filename.replace('.json', '_walking_only.json'))

        with open(input_filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        frames = json_data.get('data', [])
        filtered_frames = []

        for frame in frames:
            track_data = frame.get('frameData', {}).get('trackData', [])

            if track_data and len(track_data) > 0:
                track = track_data[0]
                vel_y = track[5]  # speed on Y axis

                if abs(vel_y) >= min_walking_speed:
                    filtered_frames.append(frame)

        # Re-number frameNum sequentially (1-based, matching original style)
        for new_num, frame in enumerate(filtered_frames, start=1):
            frame['frameData']['frameNum'] = new_num

        json_data['data'] = filtered_frames

        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)

        print(f"[{filename}]")
        print(f"  Frames before : {len(frames)}")
        print(f"  Frames after  : {len(filtered_frames)}")
        print(f"  Frames removed: {len(frames) - len(filtered_frames)}")
        print(f"  Saved to      : {output_filepath}\n")
