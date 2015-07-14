import speech_recognition as sr
import interpreter.interpreter as interp
import webbrowser
from subprocess import call

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
        elif res["action"] == "turn":
            print "turnAround"
        elif res["action"] == "stop":
            print "stop"
        elif res["action"] == "follow":
            print "follow"
        elif res["action"] == "show":
            if "video_title" in res:
                command = '/Applications/VLC.app/Contents/MacOS/VLC --play-and-exit ./videos/' + res['video_title'] + '.mp4'
                print command
                call(command , shell=True)
            elif "object" in res:
                command = '/Applications/VLC.app/Contents/MacOS/VLC --play-and-exit ./images/' + res['object'] + '.jpg'
                print command
                call(command , shell=True)
        # LILI master control has no actual actions for talking to the user, so when that action is detected, nothing is sent to the master control

