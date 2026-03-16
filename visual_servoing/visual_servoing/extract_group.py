import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── CONFIG ──────────────────────────────────────────────────────────────────
# Point these to the 3 CSV files you extracted for your parking trials
TRIAL_1 = r"/home/racecar/racecar_ws/src/visual_servoing/visual_servoing/visual_servoing/parking_rosbags/outrange_real_1/parking_error.csv"
TRIAL_2 = r"/home/racecar/racecar_ws/src/visual_servoing/visual_servoing/visual_servoing/parking_rosbags/outrange_real_2/parking_error.csv"
TRIAL_3 = r"/home/racecar/racecar_ws/src/visual_servoing/visual_servoing/visual_servoing/parking_rosbags/outrange_real_3/parking_error.csv"

TRIALS = [TRIAL_1, TRIAL_2, TRIAL_3]

# How many seconds of the run you want to plot
# CLIP_TIME = 10.0
# ────────────────────────────────────────────────────────────────────────────
def load_trial_data(csv_path):
    """Loads a single CSV and returns time (seconds) and errors."""
    df = pd.read_csv(csv_path).sort_values('time').reset_index(drop=True)

    # Convert timestamps to relative seconds starting at 0
    timestamps = pd.to_datetime(df['time']).astype('int64') / 1e9
    t0 = timestamps.iloc[0]
    time_secs = (timestamps - t0).values

    x_err = df['x_error'].values
    y_err = df['y_error'].values
    dist_err = df['distance_error'].values

    return time_secs, x_err, y_err, dist_err

def average_errors(trial_paths):
    """Dynamically scales to the longest trial and averages all data."""
    all_data = []
    max_time = 0

    # First pass: load everything and find the longest running trial
    for path in trial_paths:
        t, x, y, dist = load_trial_data(path)
        all_data.append((t, x, y, dist))
        if t[-1] > max_time:
            max_time = t[-1]

    # Create a shared time axis spanning the entire run
    common_time = np.linspace(0, max_time, 1000)

    x_interps, y_interps, dist_interps = [], [], []

    for t, x, y, dist in all_data:
        # Interpolate this trial's errors onto the common time axis.
        # (If a trial ends slightly earlier, it holds the last value)
        x_interps.append(np.interp(common_time, t, x))
        y_interps.append(np.interp(common_time, t, y))
        dist_interps.append(np.interp(common_time, t, dist))

    # Calculate the mean across the 3 trials
    avg_x = np.mean(x_interps, axis=0)
    avg_y = np.mean(y_interps, axis=0)
    avg_dist = np.mean(dist_interps, axis=0)

    return common_time, avg_x, avg_y, avg_dist

# ── PROCESS & PLOT ──────────────────────────────────────────────────────────
print("Loading and averaging trials...")
time_axis, avg_x, avg_y, avg_dist = average_errors(TRIALS)

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(time_axis, avg_x, color='steelblue', linewidth=2.0, label='Average X Error')
ax.plot(time_axis, avg_y, color='darkorange', linewidth=2.0, label='Average Y Error')
ax.plot(time_axis, avg_dist, color='forestgreen', linewidth=2.0, label='Average Distance Error')

ax.axhline(0, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='Zero Error Target')

ax.set_xlabel('Time (s)')
ax.set_ylabel('Error (m)')
ax.set_title('Average Visual Servoing Parking Error for Path Within Parking Distance (3 Trials)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('average_parking_error_full.png', dpi=150)
plt.show()

# ── OVERALL STATS ───────────────────────────────────────────────────────────
print("\n── OVERALL PERFORMANCE (Entire Run) ──")
print(f"X Error        -> Max: {avg_x.max():.4f} m | Min: {avg_x.min():.4f} m | Avg: {avg_x.mean():.4f} m")
print(f"Y Error        -> Max: {avg_y.max():.4f} m | Min: {avg_y.min():.4f} m | Avg: {avg_y.mean():.4f} m")
print(f"Distance Error -> Max: {avg_dist.max():.4f} m | Min: {avg_dist.min():.4f} m | Avg: {avg_dist.mean():.4f} m")
