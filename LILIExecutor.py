import os
import speech_recognition as sr
import interpreter.interpreter as interp
from subprocess import call
import sys
import IPC
import time

is_windows = True

if is_windows:
    # Path for Windows
    vlc_path = '"C:\Program Files (x86)\VideoLAN\VLC\VLC.exe"'
else:
    # Path for Mac
    vlc_path = "/Applications/VLC.app/Contents/MacOS/VLC"

vm = IPC.process(True, "LILIExecutor.py")

started = False # Changes once it gets start command from master controller
lily = False # User must say "Lily" before giving a command

r = sr.Recognizer()
def runRecognizer():
    if lily:
       sys.stderr.write("LILI is listening\n")

    # Comment out this with block to use standard input instead of speech recognition
    with sr.Microphone() as source:
        audio = r.adjust_for_ambient_noise(source, duration=1)
        r.energy_threshold = 1000
        sys.stderr.write("Speak now\n")
        audio = r.listen(source)
        sent = "" + r.recognize(audio)

    # Uncomment this to use standard input instead of speech recognition
    """
    sys.stderr.write("Type a sentence:")
    sent = raw_input()
    """

    sent = sent.encode('ascii', 'ignore').lower()
    return sent

# Only used to receive start command
def onReadLine():
    global started
    message = vm.line.strip()
    if message == "start":
        sys.stderr.write("Got start signal\n")
        started = True

def process_result(res):
    # Based on the action and any other parameters, sends a command to LILI master control
    if 'error' not in res:
        if res['action'] == "move":
            if "direction" in res and (res["direction"] == "left" or res["direction"] == "right"):
                command = res['direction'] + "Wave"
                vm.write(command + "\n")
                sys.stderr.write("Sending command to master control: " + command + "\n")
            else:
                sys.stderr.write("Unknown direction\n")
        elif res["action"] == "turn":
            command = "turnAround"
            vm.write(command + "\n")
            sys.stderr.write("Sending command to master control: " + command + "\n")
        elif res["action"] == "stop":
            command = "stop"
            vm.write(command + "\n")
            sys.stderr.write("Sending command to master control: " + command + "\n")
        elif res["action"] == "follow":
            command = "follow"
            vm.write(command + "\n")
            sys.stderr.write("Sending command to master control: " + command + "\n")
        elif res["action"] == "show":

            if "video_title" in res:
                video_path = "./videos/" + res["video_title"]

                if is_windows:
                    # Switches slashes to backslashes (for Windows only)
                    video_path = video_path.replace("/", "\\")

                video_extensions = ["mov", "mp4"]
                found_video = False
                for ext in video_extensions:
                    video_path_ext = video_path + "." + ext
                    if os.path.exists(video_path_ext):
                        command = vlc_path + " --play-and-exit " + video_path_ext
                        sys.stderr.write("Running command prompt command: " +command + "\n")
                        call(command , shell=True)
                        found_video = True
                        break
                if not found_video:
                    sys.stderr.write("Video named " + video_path + " not found!\n")

            elif "object" in res:
                img_path = "./images/" + res["object"]

                if is_windows:
                    # Switches slashes to backslashes (for Windows only)
                    img_path = img_path.replace("/", "\\")

                img_extensions = ["jpg", "png", "gif"]
                found_img = False
                for ext in img_extensions:
                    img_path_ext = img_path + "." + ext
                    if os.path.exists(img_path_ext):
                        command = vlc_path + " --play-and-exit " + img_path_ext
                        sys.stderr.write("Running command prompt command: " + command + "\n")
                        call(command , shell=True)
                        found_img = True
                        break
                if not found_img:
                    sys.stderr.write("Image named " + img_path + " not found!\n")

        # LILI master control has no actual actions for talking to the user, so when that action is detected, nothing is sent to the master control

vm.setOnReadLine(onReadLine)

IPC.InitSync()
while not started:
    vm.tryReadLine()
    IPC.Sync()

while started:

    try:
        sent = runRecognizer()
        sys.stderr.write("Recognized sentence: " + sent + "\n")
        if sent.lower() == "lily":
            lily = True
        elif sent.lower() == "never mind" or sent.lower() == "nevermind":
            lily = False
            sys.stderr.write("LILI is not listening for your command anymore\n")
        elif lily == True: # If this is satisfied, lily is being talked to
                lily = False
                if sent.lower() == "good bye" or sent.lower() == "goodbye":
                    sys.stderr.write("Got end signal\n")
                    started = False
                else: # Process the result and take appropriate action
                    try:
                        res = interp.interpret_sent(sent)
                        sys.stderr.write("Result: " + str(res) +"\n")
                        process_result(res)
                    except Exception,e:
                        sys.stderr.write("Sentence could not be interpreted due to exception:\n")
                        sys.stderr.write(str(e) + "\n")
        else:
            sys.stderr.write("LILI did not listen to your command, say her name first\n")

    except Exception,e:
        sys.stderr.write("Speech could not be recognized\n")
        sys.stderr.write(str(e) + "\n")

    IPC.Sync()