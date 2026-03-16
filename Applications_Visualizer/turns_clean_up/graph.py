import json
import matplotlib.pyplot as plt

file_original = '/home/catbert21/uni/TI/2025-FMCWRadar/Applications_Visualizer/binData/02_14_2026_15_49_24/alina5.json'
file_filtered = 'alina2_1_walking_only.json'

def extract_vel_y(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    frame_nums = []
    vel_ys = []
    
    for frame in data.get('data', []):
        frame_data = frame.get('frameData', {})
        track_data = frame_data.get('trackData', [])
        frame_num = frame_data.get('frameNum') 
        
        if track_data and len(track_data) > 0 and frame_num is not None:
            vel_y = track_data[0][5]
            frame_nums.append(frame_num)
            vel_ys.append(vel_y)
            
    return frame_nums, vel_ys

frames_orig, vels_orig = extract_vel_y(file_original)
frames_filt, vels_filt = extract_vel_y(file_filtered)


plt.plot(frames_orig, vels_orig, label='Original data (with turns)', 
         color='gray', linestyle='--', marker='o', alpha=0.6)

plt.plot(frames_filt, vels_filt, label='Filtered (|velY| >= 0.5 m/s)', 
         color='blue', linestyle='-', marker='x', linewidth=2)

plt.axhline(y=0.5, color='green', linestyle=':', linewidth=2, label=' +0.5 m/s (from the radar)')
plt.axhline(y=-0.5, color='green', linestyle=':', linewidth=2, label=' -0.5 m/s (to the radar)')

plt.axhline(y=0.0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

plt.title('Y-axis velocity (velY) before and after filtering')
plt.xlabel('Radar frame number (frameNum)')
plt.ylabel('Speed velY (m/s)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()