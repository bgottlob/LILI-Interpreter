import speech_recognition as sr
import interpreter.interpreter as interp
from subprocess import call
import os
import sys

# Path for Mac
vlc_path = "/Applications/VLC.app/Contents/MacOS/VLC"

while True:
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.adjust_for_ambient_noise(source, duration=1)
        r.energy_threshold = 1000
        sys.stderr.write("Listening again\n")
        audio = r.listen(source)"""

    try:
        sys.stderr.write("Type a sentence:\n")
        sent = raw_input()
        #sent = "" + r.recognize(audio)
        sent = sent.encode('ascii', 'ignore')
        res = interp.interpret_sent(sent)
        sys.stderr.write(res)
    except Exception,e:
        res = {'error': 'exception occurred during interpretation'}
        sys.stderr.write(str(e) + "\n")

    # Based on the action and any other parameters, sends a command to LILI master control
    if 'error' not in res:
        if res['action'] == "move":
            if "direction" in res and (res["direction"] == "left" or res["direction"] == "right"):
                print res['direction'] + "Wave"
            else:
                sys.stderr.write("Unknown direction\n")
        elif res["action"] == "turn":
            print "turnAround"
        elif res["action"] == "stop":
            print "stop"
        elif res["action"] == "follow":
            print "follow"
        elif res["action"] == "show":

            if "video_title" in res:
                video_path = "./videos/" + res["video_title"]
                video_extensions = ["mov", "mp4"]
                for ext in video_extensions:
                    video_path_ext = video_path + "." + ext
                    if os.path.exists(video_path_ext):
                        command = vlc_path + " --play-and-exit " + video_path_ext
                        sys.stderr.write(command + "\n")
                        call(command , shell=True)
                        break
                sys.stderr.write("Video named " + video_path + " not found!\n")

            elif "object" in res:
                img_path = "./images/" + res["object"]
                img_extensions = ["jpg", "png", "gif"]
                for ext in img_extensions:
                    img_path_ext = img_path + "." + ext
                    if os.path.exists(img_path_ext):
                        command = vlc_path + " --play-and-exit " + img_path_ext
                        sys.stderr.write(command + "\n")
                        call(command , shell=True)
                        break
                sys.stderr.write("Image named " + img_path + " not found!\n")

        # LILI master control has no actual actions for talking to the user, so when that action is detected, nothing is sent to the master control

