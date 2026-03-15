import cv2
from ultralytics import YOLO

INPUT_VIDEO = "IMG_2373.mp4"
OUTPUT_VIDEO = "IMG_2373_annotated.mp4"

model = YOLO("yolo11n.pt")
cap = cv2.VideoCapture(INPUT_VIDEO)

# Get video properties for output
fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame, conf=0.2, iou=0.7, verbose=False)
    annotated = results[0].plot()  # Ultralytics built-in drawing
    out.write(annotated)
    cv2.imshow("YOLO", annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
print(f"Saved annotated video to {OUTPUT_VIDEO}")