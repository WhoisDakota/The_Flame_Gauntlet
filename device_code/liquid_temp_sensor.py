import time
import subprocess

from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()

def textToSpeech(speech):
    speech = speech.replace(' ','_')
    subprocess.run(("espeak \"" + speech + "\" 2>/dev/null").split(" "))
    
while True:
    temperature = sensor.get_temperature()
    print("Temp is %s celcius" % temperature)
    textToSpeech("Temp is %s celcius" % temperature)
    time.sleep(5)
