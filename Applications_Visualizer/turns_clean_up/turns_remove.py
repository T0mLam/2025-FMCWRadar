import json

input_filepath = '/home/catbert21/uni/TI/2025-FMCWRadar/Applications_Visualizer/binData/02_14_2026_15_49_24/alina5.json'
output_filepath = 'alina2_1_walking_only.json'

min_walking_speed = 0.5 

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

json_data['data'] = filtered_frames

with open(output_filepath, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=4)

print(f"Was frames: {len(frames)}")
print(f"Left frames: {len(filtered_frames)}")
print(f"Total frames removed: {len(frames) - len(filtered_frames)}")