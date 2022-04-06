#!/usr/bin/env python3
import button
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
import math
import subprocess



# imports sensors from other packages above.
# this will be used to control input to output

#Button Vars
global flameButtonPressed
flameButtonPressed = False
global tempButtonPressed
tempButtonPressed = False


# sets pins for components
BtnPin = 15
BtnPin2 = 29

TRIG = 11
ECHO = 12

Buzzer = 22

DO = 13


#buzzer songs
CL = [0, 131, 147, 165, 175, 196, 211, 248]         # Frequency of Low C notes

CM = [0, 262, 294, 330, 350, 393, 441, 495]         # Frequency of Middle C notes

CH = [0, 525, 589, 661, 700, 786, 882, 990]         # Frequency of High C notes

song_1 = [  CL[0], CM[1], CH[4] ] #Flame

beat_1 = [  1, 1, 1 ]

song_2 = [  CH[0], CM[1], CL[4] ] #No Flame

beat_2 = [  1, 1, 1 ]


# sets up GPIO input and output
def setup():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.setup(BtnPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime=200)
    GPIO.add_event_detect(BtnPin2, GPIO.BOTH, callback=detect, bouncetime=200)
    
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
    GPIO.setup(Buzzer, GPIO.OUT)    # Set pins' mode is output
    global Buzz                     # Assign a global variable to replace GPIO.PWM
    Buzz = GPIO.PWM(Buzzer, 440)    # 440 is initial frequency.

    ADC.setup(0x48)
    GPIO.setup(DO, GPIO.IN)


#Text to Speech Function
def textToSpeech(speech):
    speech = speech.replace(' ','_')
    subprocess.run(("espeak \"" + speech + "\" 2>/dev/null").split(" "))


#Temperature Button Function
def tempButton(buttonIn):
    global tempButtonPressed
    global flameButtonPressed
    if (buttonIn == 0):
        if (tempButtonPressed == False) and (flameButtonPressed == False):
            tempButtonPressed = True
            print("Temperature Button Pressed")
            from w1thermsensor import W1ThermSensor
            sensor = W1ThermSensor()
            temperature = sensor.get_temperature()
            print("Temp is %s celcius" % temperature)
            textToSpeech("Temp is %s celcius" % temperature)
    else:
        tempButtonPressed = False
    
    
#Flame Button Function
def flameButton(buttonIn):
    global flameButtonPressed
    global tempButtonPressed
    if (buttonIn == 0):
        if (flameButtonPressed == False) and (tempButtonPressed == False):
            flameButtonPressed = True
            print("Flame Button Pressed")
            #tmp = GPIO.input(DO)
            tmp = ADC.read(0)
            print(tmp)
            
            #Check if flame sensor is triggered
            if (tmp <= 175):   
                Buzz.start(50)                              # Start Buzzer pin with 50% duty ration
                #Playing song 1...
                for i in range(1, len(song_1)):             # Play song 1
                    Buzz.ChangeFrequency(song_1[i])         # Change the frequency along the song note
                    time.sleep(beat_1[i] * 0.5)             # delay a note for beat * 0.5s
                Buzz.stop()  
            else:
                Buzz.start(50)                              # Start Buzzer pin with 50% duty ration
                #Playing song 2...
                for i in range(1, len(song_2)):             # Play song 2
                    Buzz.ChangeFrequency(song_2[i])         # Change the frequency along the song note
                    time.sleep(beat_2[i] * 0.5)             # delay a note for beat * 0.5s
                Buzz.stop()  
            
    else:
        flameButtonPressed = False
        Buzz.stop()                                         # Stop the buzzer

def detect(chn):
    tempButton(GPIO.input(BtnPin))
    flameButton(GPIO.input(BtnPin2))
    

#core loop
def loop():
    while True:
        run()
        pass
    
def run():
    tempButton(GPIO.input(BtnPin))
    flameButton(GPIO.input(BtnPin2))
    
#program terminator
def destroy():
    Buzz.stop()                     # Stop the buzzer
    GPIO.output(Buzzer, 1)          # Set Buzzer pin to High
    
    GPIO.cleanup()      


#main function
if __name__ == '__main__':
    setup()
    try:
        run()
        
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
