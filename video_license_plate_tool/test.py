import cv2
from ultralytics import YOLO
import pytesseract
import os

def extract_text_from_image(image):
    """
    OCR op een uitgesneden afbeelding (bounding box).
    :param image: Numpy-array van de afbeelding.
    :return: Herkende tekst als string.
    """
    # Converteer naar grijswaarden voor betere OCR-resultaten
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Pas OCR toe
    text = pytesseract.image_to_string(gray, config="--psm 7")
    return text.strip()

def process_video_with_yolo(video_path, model_path, output_dir, confidence_threshold=0.5):
    """
    Analyseert een video met YOLO, detecteert kentekens, en past OCR toe op de bounding boxes.
    :param video_path: Pad naar de video.
    :param model_path: Pad naar het YOLO-model.
    :param output_dir: Map om resultaten op te slaan.
    :param confidence_threshold: Drempel voor detectie.
    """
    # Laad het YOLO-model
    model = YOLO(model_path)
    
    # Zorg ervoor dat de uitvoermap bestaat
    os.makedirs(output_dir, exist_ok=True)
    
    # Analyseer de video
    results = model(video_path, stream=True)  # YOLO streaming-inferentie
    counter = 0
    for result in results:
        frame = result.orig_img  # Het originele frame
        detections = result.boxes  # Bounding boxes
        
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Bounding box-coördinaten
            confidence = box.conf[0].item()  # Vertrouwen
            cls_id = int(box.cls[0].item())  # Class ID
            counter = counter + 1
            
            # Filter op vertrouwen en (optioneel) class ID
            if confidence >= confidence_threshold:
                # Snijd de bounding box uit
                cropped_plate = frame[y1:y2, x1:x2]
                
                # OCR toepassen
                plate_text = extract_text_from_image(cropped_plate)
                
                if plate_text:  # Als OCR tekst vindt
                    print(f"Kenteken gevonden: {plate_text} (Vertrouwen: {confidence:.2f})")
                    
                    # Optioneel: sla het beeld op
                    # frame_filename = f"frame_{counter}_plate_{plate_text}.jpg"
                    # frame_path = os.path.join(output_dir, frame_filename)
                    # cv2.imwrite(frame_path, cropped_plate)
                    
                    # Debug: markeer de bounding box op het originele frame
                    # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # cv2.putText(frame, plate_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Optioneel: toon elk frame met bounding boxes
        # cv2.imshow("YOLO Video Processing", frame)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

    cv2.destroyAllWindows()

# Parameters
video_path = "downloads/demo.mp4"
model_path = "models/license_plate_detector.pt"
output_dir = "output/"

process_video_with_yolo(video_path, model_path, output_dir)
