import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── CONFIG ──────────────────────────────────────────────────────────────────
CSV_PATH = r"/home/racecar/racecar_ws/src/visual_servoing/visual_servoing/visual_servoing/parking_rosbags/outrange_real_3/parking_error.csv"

START_TIME = 2.0  # Seconds to trim from the start, if needed
# ────────────────────────────────────────────────────────────────────────────

def plot_parking_errors(csv_path, start_time=0.0):
    print(f"Loading CSV from {csv_path}...")

    try:
        # Load and sort data by time
        df = pd.read_csv(csv_path).sort_values('time').reset_index(drop=True)
    except FileNotFoundError:
        print(f"\nError: Could not find the file at {csv_path}.")
        print("Make sure you have converted your ROS 2 bag (.db) to a CSV first!")
        return

    # Convert timestamps (assuming nanoseconds) to relative seconds
    timestamps = pd.to_datetime(df['time']).astype('int64') / 1e9
    t0 = timestamps.iloc[0]
    time_secs = (timestamps - t0).values

    # Extract the error columns
    x_err = df['x_error'].values
    y_err = df['y_error'].values
    dist_err = df['distance_error'].values

    # Trim data based on START_TIME
    mask = time_secs >= start_time
    time_trim = time_secs[mask] - time_secs[mask][0]  # re-zero time
    x_err_trim = x_err[mask]
    y_err_trim = y_err[mask]
    dist_err_trim = dist_err[mask]

    # ── PLOT ────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot X, Y, and Distance errors
    ax.plot(time_trim, x_err_trim, color='steelblue', linewidth=2.0, label='X Error')
    ax.plot(time_trim, y_err_trim, color='darkorange', linewidth=2.0, label='Y Error')
    ax.plot(time_trim, dist_err_trim, color='forestgreen', linewidth=2.0, label='Distance Error')

    # Add a zero-error reference line to show convergence
    ax.axhline(0, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='Zero Error Target')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Error (m)')
    ax.set_title('Visual Servoing Parking Error over Time')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('parking_controller_errors.png', dpi=150)
    plt.show()

    # ── STATS ───────────────────────────────────────────────────────────────
    # RMSE calculation for overall controller performance
    rmse_x = np.sqrt(np.mean(x_err_trim**2))
    rmse_y = np.sqrt(np.mean(y_err_trim**2))
    rmse_dist = np.sqrt(np.mean(dist_err_trim**2))

    print("\n── Overall Performance (RMSE) ──")
    print(f"  X Error RMSE:        {rmse_x:.4f} m")
    print(f"  Y Error RMSE:        {rmse_y:.4f} m")
    print(f"  Distance Error RMSE: {rmse_dist:.4f} m")

    # Calculate the average error over the last 10 samples to check steady-state offset
    if len(time_trim) >= 10:
        print("\n── Steady-State Errors (Avg of last 10 samples) ──")
        print(f"  Final X Error:        {np.mean(x_err_trim[-10:]):.4f} m")
        print(f"  Final Y Error:        {np.mean(y_err_trim[-10:]):.4f} m")
        print(f"  Final Distance Error: {np.mean(dist_err_trim[-10:]):.4f} m")

if __name__ == "__main__":
    plot_parking_errors(CSV_PATH, START_TIME)
