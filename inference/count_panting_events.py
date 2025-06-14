import torch
import torch.nn as nn
from torchvision import models, transforms
import cv2
from PIL import Image
import os

# --- CONFIG ---
MODEL_PATH = os.path.join("models", "panting_frame_model.pth")  # Ensure correct path
IMG_SIZE = 224
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
FRAME_INTERVAL = 1
THRESHOLD = 0.5

# --- Load Model ---
def load_model():
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, 1)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

# --- Transform ---
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor()
])

# --- Predict Frame Confidence & Label ---
def predict_frame(model, frame):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    image = transform(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        output = torch.sigmoid(model(image)).item()
    return output, 1 if output > THRESHOLD else 0

# --- Analyze Video ---
def analyze_video(video_path):
    model = load_model()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return "Error: Could not open video."

    predictions = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % FRAME_INTERVAL == 0:
            _, pred = predict_frame(model, frame)
            predictions.append(pred)
        frame_idx += 1

    cap.release()
    
    # --- Check Overall Panting ---
    panting_detected = any(predictions)
    return "The dog is panting." if panting_detected else "The dog is not panting."