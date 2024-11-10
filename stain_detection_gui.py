import tkinter as tk
from tkinter import filedialog, Label
from PIL import Image, ImageTk
import cv2
import os
import time
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import numpy as np

# Main function
def process_video(cap):
    # Get the first frame and allow the user to select the working area
    ret, first_frame = cap.read()
    if not ret:
        print("Could not read the video file.")
        cap.release()
        return

    # Resize the first frame
    scale_percent = 50
    width = int(first_frame.shape[1] * scale_percent / 100)
    height = int(first_frame.shape[0] * scale_percent / 100)
    first_frame = cv2.resize(first_frame, (width, height))

    # Select the working area
    working_area = cv2.selectROI("Select Working Area", first_frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select Working Area")

    if working_area == (0, 0, 0, 0):
        print("No valid working area selected.")
        cap.release()
        return

    x, y, w, h = working_area

    # Data set preparation
    data_dir = "Dirty-Clothes-Image-Classifications"
    resin_dir = os.path.join(data_dir, "implemented")
    no_resin_dir = os.path.join(data_dir, "not_implemented")
    images = []
    labels = []

    for filename in os.listdir(resin_dir):
        img = cv2.imread(os.path.join(resin_dir, filename))
        images.append(img)
        labels.append(1)

    for filename in os.listdir(no_resin_dir):
        img = cv2.imread(os.path.join(no_resin_dir, filename))
        images.append(img)
        labels.append(0)

    features = [cv2.mean(img)[:3] for img in images]

    # Train the model
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    print("Model Accuracy:", accuracy)

    # Loop through video frames
    frame_count = 0
    resin_detected = False
    start_time = time.time()
    end_time = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or camera feed unavailable.")
            break

        frame = cv2.resize(frame, (width, height))
        
        if end_time is None:
            elapsed_time = time.time() - start_time
        else:
            elapsed_time = end_time - start_time

        cv2.putText(frame, f"Time: {elapsed_time:.2f}s", (w - 150, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if not resin_detected:
            # Extract the working area and calculate its average color
            roi_area = frame[y:y+h, x:x+w]
            avg_color = cv2.mean(roi_area)[:3]
            prediction = model.predict([avg_color])[0]

            # If the model detects a coffee stain, draw a blue outline
            if prediction == 1:
                resin_detected = True
                end_time = time.time()

                # Draw a blue outline around the detected coffee-stained area
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
                # Capture and show frame in Tkinter
                capture_and_show_frame(frame)

        # Resin detection output
        if resin_detected:
            cv2.putText(frame, "Coffee Stain Detected!", (w - 150, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "No Stain", (w - 150, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("Video", frame[y:y+h, x:x+w])

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    print("Done processing video.")

def capture_and_show_frame(frame):
    # Display the selected frame
    color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(color_converted)
    img_tk = ImageTk.PhotoImage(pil_image)
    img_label.config(image=img_tk)
    img_label.image = img_tk

# Load video or open camera functions
def load_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
    if file_path:
        cap = cv2.VideoCapture(file_path)
        process_video(cap)

def open_camera():
    cap = cv2.VideoCapture(0)
    process_video(cap)

# GUI setup
root = tk.Tk()
root.title("Camera and Video Processing")
root.geometry("800x800")
root.configure(bg="#f0f0f0")

# Updated button style for better visibility
button_style = {
    "font": ("Helvetica", 14, "bold"),
    "bg": "#4682B4",  # Dodger Blue
    "fg": "white",
    "relief": "raised",
    "bd": 2,
    "highlightthickness": 2,
    "highlightbackground": "#4682B4",  # Steel Blue border for emphasis
    "activebackground": "#4682B4",  # Deep Sky Blue when clicked
    "cursor": "hand2"
}

camera_button = tk.Button(root, text="Open Camera", command=open_camera, **button_style)
camera_button.config(width=20, height=2)
camera_button.pack(pady=20)

gallery_button = tk.Button(root, text="Load Video from Gallery", command=load_video, **button_style)
gallery_button.config(width=20, height=2)
gallery_button.pack(pady=20)

img_label = Label(root)
img_label.pack()

root.mainloop()