import sys
import speech_recognition as sr
import pyaudio
import pyttsx3
import time
import struct
import os
import datetime
#check if the word is there in dataset
def wordcount(filename,usersaid):
    file=open(filename,'r')
    read=" "
    while(read):
        read=file.readline()
        #print(read)
        if usersaid in read:
            return True
    file.close()

#function to speak any text that is passed to it 
def speak(text):
    engine= pyttsx3.init('sapi5')
    voices=engine.getProperty('voices')
    engine.setProperty('voice',voices[0].id)
    engine.say(text)
    engine.runAndWait()

# function to listen to microphone and convert spoken words to text
def takeCommand(): #hear wht is being said
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=2)
        #r.pause_threshold=1
        print("Listening...", end=" ")
        
        audio=r.listen(source)
        #audio=r.listen(source,phrase_time_limit=7)
        query=''

        try:
            print("Recognizing...",end=" ")
            query = r.recognize_google(audio,language='en-US')
            print(f"User said:{query}") #Displays what was said

        except Exception as e:
            print("Exception:"+str(e))
    return query.lower()

#audio to the user
def ConversationFlow():
    while True:
        speak("What do you want to search")
        userSaid=takeCommand()
        
        if "sleep" in userSaid:
            speak("i am going to sleep now")
            break

        if wordcount("objects.txt",userSaid):
            speak("The requested object is "+ userSaid)
        else:
            speak("Requested object is not there in dataset")
        
        time.sleep(1)

#wake word
def wake():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=2)
        #r.pause_threshold=1
        print("Wake me...", end=" ")
        #audio=r.listen(source,timeout=4,phrase_time_limit=7)
        audio=r.listen(source)
        try:
            print("Recognizing...",end=" ")
            query = r.recognize_google(audio,language='en-US')

        except Exception as e:
            print("Exception:"+str(e))
    return query.lower()
        
#to wish
def wish():
    hour=int(datetime.datetime.now().hour)
    #mint=int(datetime.datetime.now().minute)
    #secc=int(datetime.datetime.now().second)
    time=datetime.datetime.now().strftime("%I:%M")

    if hour>=0 and hour<=12:
        speak("Good Morning.The time is"+time)
    elif hour>12 and hour<18:
        speak("Good Afternoon.The time is"+time)
    else:
        speak("Good evening.The time is"+time)

    speak("to start tell vision")
if __name__ == "__main__":
    wish()
    
    while True:
        permission=wake()
        if "vision" in permission:
            ConversationFlow()
        elif "goodbye" in permission:
            speak("Have a good Day")
            sys.exit()