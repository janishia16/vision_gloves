import numpy as np
import torch
import cv2
from PIL import Image, ImageDraw
import math,pyttsx3
import three
import RPi.GPIO as GPIO
import wwake

model = torch.hub.load('ultralytics/yolov5', 'yolov5l6')


# Set the scaling factor for distance estimation
scaling_factor =0.13 #0.0002

# Define the field of view and focal length of the camera
field_of_view = 60 # in degrees
camera_focal_length = 800 # in pixels

vibration_pin = 27




	

def speak(text):
    engine= pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def capture(class_name):
    # Set the known object dimensions (in meters)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(vibration_pin, GPIO.OUT)
    GPIO.output(vibration_pin, GPIO.HIGH)
	
    object_height = 1.5
    object_width = 0.5

    cap = cv2.VideoCapture(0)

    count=0
    while True:
        ret, frame = cap.read()
        
        # Convert OpenCV image to PIL Image object
        image = Image.fromarray(frame[...,::-1])

        # Perform object detection on the PIL Image object
        results = model(image)

        l=model.names
        class_idx = list(filter(lambda x: l[x] == class_name, l))[0]

        # Set the minimum confidence score
        confidence_threshold = 0.5

        # Filter the detections by the target class and confidence threshold
        detections = results.pred[0][(results.pred[0][:, 5] == class_idx) & (results.pred[0][:, 4] >= confidence_threshold)]

        if len(detections) == 0:
            # If no target object is detected, continue to next frame
            continue

        # Get the bounding box coordinates of the target object
        box = detections[0][:4].tolist()

        # Extract the x and y coordinates of the center of the bounding box
        x_center = int((box[0] + box[2]) / 2)
        y_center = int((box[1] + box[3]) / 2)

        # Draw a circle at the center of the bounding box
        cv2.circle(frame, (x_center, y_center), 5, (0, 0, 255), -1)

        # Estimate the distance to the target object
        object_width_pixels = box[2] - box[0]
        object_height_pixels = box[3] - box[1]

        if object_width_pixels == 0 or object_height_pixels == 0:
            continue

        object_width_distance = object_width / object_width_pixels
        object_height_distance = object_height / object_height_pixels

        object_width = object_width_pixels * object_width_distance
        object_height = object_height_pixels * object_height_distance

        distance = (object_width_distance + object_height_distance) / 2 * scaling_factor

        # Convert distance to centimeters
        #distance_cm = round(distance * 1000, 2)

        #dis = (2 * 3.14 * 180) / (box[2]+ box[3] * 360) * 1000 + 3
        #distance=round(dis)*2.54

        # Determine the center point of the object
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2

        # Determine the center point of the frame
        frame_center_x = frame.shape[1] / 2

        # Determine the difference between the object center point and frame center point
        delta_x = center_x - frame_center_x

        # Determine the angle between the object and the person
        angle = math.atan(delta_x / camera_focal_length) * (180 / math.pi)

        # Determine if the object is to the left or right of the person
        if delta_x < 0:
            direction = 'left'
        elif delta_x>0:
            direction = 'right'
        elif delta_x==0:
            direction = 'straight'

        # Convert the distance to centimeters and round to 2 decimal places
        dis=distance*100000
        dis=round(dis,2)
        if dis<27:
            GPIO.output(vibration_pin, GPIO.LOW)
            word=f'you have reached the {class_name}'
            speak(word)
            wwake.end(2)
            
			
        
        # Generate the voice command to guide the person towards
        if abs(angle) < (field_of_view / 2):
            count=+1
            if direction == 'left':
                command = f'The {class_name} is {dis} centimeters to your left'
            elif direction == 'right':
                command = f'The {class_name} is {dis} centimeters to your right'
            elif command=='straight':
                if dis <= 20:
                    command = f'The {class_name} is {dis} meters in front of you. Move forward carefully.'
                else:
                    command = f'The {class_name} is {dis} meters in front of you. Move straight.'

            if count%5==0:
                speak("do you like quit and  find other items?")
                user=takeCommand()
                if user=='yes' or user=='ES' or user=='SS':
                    return 0
                elif user=='no':
                    continue

            # Output the voice command
            speak(command)
            print(command)

        draw = ImageDraw.Draw(image)
        color = (0, 255, 0)
        draw.rectangle([(box[0],box[1]),(box[2],box[3])], outline='red', width=3)
        # Convert PIL Image object back to OpenCV image

        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.putText(frame, f'{class_name}: {dis}cm', (int(box[0]), int(box[1])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


        cv2.imshow('YOLO', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release webcam and close windows
    cap.release()
    cv2.destroyAllWindows()