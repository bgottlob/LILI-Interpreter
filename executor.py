import speech_recognition as sr
import interpreter.interpreter as interp
import webbrowser
from subprocess import call
import os

# Path for Mac
vlc_path = "/Applications/VLC.app/Contents/MacOS/VLC"

while True:
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audo = r.adjust_for_ambient_noise(source, duration=1)
        r.energy_threshold = 1000
        print "Listening again"
        audio = r.listen(source)"""

    try:
        print "Type a sentence: "
        sent = raw_input()
        #sent = "" + r.recognize(audio)
        sent = sent.encode('ascii', 'ignore')
        res = interp.interpret_sent(sent)
        print res
    except Exception,e:
        res = {'error': 'exception occurred during interpretation'}
        print str(e)

    # Based on the action and any other parameters, sends a command to LILI master control
    if 'error' not in res:
        if res['action'] == "move":
            if "direction" in res and (res["direction"] == "left" or res["direction"] == "right"):
                print res['direction'] + "Wave"
            else:
                print "Unknown direction"
        elif res["action"] == "turn":
            print "turnAround"
        elif res["action"] == "stop":
            print "stop"
        elif res["action"] == "follow":
            print "follow"
        elif res["action"] == "show":

            if "video_title" in res:
                video_path = "./videos/" + res["video_title"] + ".mp4"
                if os.path.exists(video_path):
                    command = vlc_path + " --play-and-exit " + video_path
                    print command
                    call(command , shell=True)
                else:
                    print "Video " + video_path + " not found!"

            elif "object" in res:
                img_path = "./images/" + res["object"] + ".jpg"
                if os.path.exists(img_path):
                    command = vlc_path + " --play-and-exit " + img_path
                    print command
                    call(command , shell=True)
                else:
                    print "Image " + img_path + " not found!"

        # LILI master control has no actual actions for talking to the user, so when that action is detected, nothing is sent to the master control

