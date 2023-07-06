import random
import speech_recognition as sr
import pyttsx3
import time,math
import numpy as np
import datetime
#import winsound
import cv2,torch
import numpy as np
from PIL import Image, ImageDraw
import guide
import RPi.GPIO as GPIO
import argparse
import pygame


model = torch.hub.load('ultralytics/yolov5', 'yolov5l6', pretrained=True)

# Define the field of view and focal length of the camera
field_of_view = 60 # in degrees
camera_focal_length = 800 # in pixels

frequency=7000
duration=500

# Set the radius of the circles
circle_radius = 10

# Initialize the center points of the circles
frame_center_x = None
box_center_x = None


# Set the scaling factor for distance estimation
scaling_factor =0.13 #0.0002

vibration_pin = 27



def vibrate():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(vibration_pin, GPIO.OUT)
	GPIO.output(vibration_pin, GPIO.HIGH)
	time.sleep(1.4)
	GPIO.output(vibration_pin, GPIO.LOW)

def distance(class_name):
    # Set the known object dimensions (in meters)
    object_height = 1.5
    object_width = 0.5
    
    
    cap = cv2.VideoCapture(0)

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

        #dis = (2 * 3.14 * 180) / (box[2]+ box[3] * 360) * 1000 + 3
        #dis=round(dis)*2.54
        # Convert distance to centimeters
        dis=distance*100000
        dis=round(dis,2)
        print(dis)
        return dis

        
def detect(class_name):
    speak("The requested object is present")
    #print("The requested object is present")
    
    
    while True:
        speak("To know the distance say distance")
        if takeCommand()=='distance':
            dis=distance(class_name)
            break
        
    speak("The distance is"+str(dis))

    #to guide the user
    while True:
        speak("say guide to guide you towards the object")
        time.sleep(1)
        if takeCommand()=='guide':
            guide.capture(class_name)
            break
          
'''
def sound():
    pygame.mixer.init()
    speaker_volume=0.5
    pygame.mixer.music.set_volume(speaker_volume)
    pygame.mixer.music.load("beep.wav")
    pygame.mixer.music.play()
 '''   
#check if the word is there in dataset
def wordcount(usersaid):
    flag=1

    class_name = usersaid
    l=model.names
    if list(filter(lambda x: l[x] == class_name, l)):
        class_idx = list(filter(lambda x: l[x] == class_name, l))[0]
        #print(class_idx)
    else:
        speak("object is not present in dataset")
        return 0

    cap = cv2.VideoCapture(0)
    count=0
    while True:
        time.sleep(5)
        ret, frame = cap.read()
        if ret:
            assert not isinstance(frame,type(None))
        results = model(frame)
        if(flag==1):
            a=1
            obj=[]
            res=results.pandas().xyxy[0]
            obj=res['name']
            print(obj)
            for i in obj:
                if usersaid ==i:
                    cap.release()
                    a=detect(class_name)
                    if a==0:
                        return     
                if(a):
                    count+=1
                    num=random.randint(1,10)
                    if num%2==0:
                        speak("The"+class_name+"is not present")
                    else:
                        speak("Try again")
                    
                    if count%5==0:
                        speak("do you like quit and  find other items?")
                        user=takeCommand()
                        if user=='yes' or user=='ES' or user=='SS':
                            return 0
                        elif user=='no':
                            continue

                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cap.release()
    cv2.destroyAllWindows()
    return 


#function to speak any text that is passed to it 
def speak(text):
    engine= pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# function to listen to microphone and convert spoken words to text
def takeCommand(): #hear wht is being said
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=2)
        #r.pause_threshold=1
        print("Listening...", end=" ")
        #winsound.Beep(frequency,duration)
        vibrate()
        GPIO.cleanup()
        
        audio=r.listen(source)
        #audio=r.listen(source,phrase_time_limit=7)
        query=''

        try:
            print("Recognizing...",end=" ")
            query = r.recognize_google(audio,language='en-US')
            print(f"User said:{query}") #Displays what was said

        except Exception as e:
            print("Exception:"+str(e))

        if query.lower()=='stop':
            speak("Thank you")
            

    return query.lower()

#audio to the user
def ConversationFlow():
    while True:
        speak("What do you want to search")
        userSaid=takeCommand()
        if "sleep" in userSaid:
            speak("i am going to sleep now")
            time.sleep(5)
            wish()
            ConversationFlow()

        if "stop" in userSaid:
            speak("Thank you")
            return 
        
        time.sleep(1)

        if userSaid:
            return userSaid
               

#wake word
def wake():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=2)
        #r.pause_threshold=1
        print("Wake me...", end=" ")
        #winsound.Beep(frequency,duration)
        vibrate()
        GPIO.cleanup()
        #audio=r.listen(source,timeout=4,phrase_time_limit=7)
        audio=r.listen(source)
        query=''
        try:
            print("Recognizing...",end=" ")
            query = r.recognize_google(audio,language='en-US')

        except Exception as e:
            print("Exception:"+str(e))
    return query.lower()
        
#to wish
def wish():
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Get the current time
    now = datetime.datetime.now()

    # Get the hour of the day
    hour = now.hour

    # Determine the appropriate greeting based on the time of day
    if hour < 12:
        greeting = "Good morning!"
    elif hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"

    # Use the text-to-speech engine to speak the greeting and current time
    engine.say(greeting)
    engine.say("The current time is " + now.strftime("%I:%M %p"))
    engine.runAndWait()
    

def start():
    while True:
        #sound()
        if takeCommand()=='vision':
            speak("wait for some time")
            return 
            
if _name_ == "_main_":
    
    start()
    wish()
    while True:
        r=1
        speak('To start tell vision after vibration')
        if wake()=='vision':
            speak("I'm listening")
            while r!=0:
                usersaid=ConversationFlow()
                if len(usersaid)>0:
                    r=wordcount(usersaid)
                if r==0:
                    speak("do you like to find other items?")
                    user=takeCommand()
                    if user=='yes' or user=='ES' or user=='SS':
                        r=1
                    elif user=='no':
                        r=0
            speak("thank you have a nice day")
            time.sleep(120)
        else:
            speak("Please tell the correct word to start")
		
    
    #wordcount('person')
    #guide.capture('person')
    #distance('person')