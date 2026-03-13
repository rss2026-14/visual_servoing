#!/usr/bin/env python3
import rosbag2_py
import numpy as np
import cv2
from rclpy.serialization import deserialize_message
from vs_msgs.msg import ConeLocationPixel

# Your homography points (same as homography_transformer.py)
PTS_IMAGE_PLANE = [[320, 240],
                   [410, 195],
                   [230, 195],
                   [320, 150]]

PTS_GROUND_PLANE = [[12, 0],
                    [12, -6],
                    [12,  6],
                    [18, 0]]

METERS_PER_INCH = 0.0254

# Ground truth: pixel coords you clicked WHILE bagging
# (pixel_u, pixel_v, true_x_inches, true_y_inches)
GROUND_TRUTH = [
    (350, 220, 14, -2),
    (290, 210, 13,  3),
    (360, 170, 20, -1),
]

# Compute homography
np_pts_ground = np.float32(np.array(PTS_GROUND_PLANE) * METERS_PER_INCH)
np_pts_image  = np.float32(np.array(PTS_IMAGE_PLANE))
H, _ = cv2.findHomography(np_pts_image, np_pts_ground)

def transform(u, v):
    pt = np.array([[u], [v], [1]], dtype=np.float32)
    xy = H @ pt
    xy /= xy[2]
    return xy[0, 0], xy[1, 0]

# Evaluate
errors = []
print(f"{'Point':<6} {'Predicted (m)':<22} {'True (m)':<22} {'Error (cm)'}")
print("-" * 65)

for i, (pu, pv, tx, ty) in enumerate(GROUND_TRUTH):
    pred_x, pred_y = transform(pu, pv)
    true_x = tx * METERS_PER_INCH
    true_y = ty * METERS_PER_INCH
    err = np.sqrt((pred_x - true_x)**2 + (pred_y - true_y)**2)
    errors.append(err)
    print(f"{i+1:<6} ({pred_x:.3f}, {pred_y:.3f})         ({true_x:.3f}, {true_y:.3f})         {err*100:.2f}")

print("-" * 65)
print(f"Mean error : {np.mean(errors)*100:.2f} cm")
print(f"RMSE       : {np.sqrt(np.mean(np.array(errors)**2))*100:.2f} cm")
print(f"Max error  : {np.max(errors)*100:.2f} cm")