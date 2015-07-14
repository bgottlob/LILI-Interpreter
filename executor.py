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

    if 'error' not in res:
        if res['action'] == "move" and 'direction' in res:
            print res['direction'] + "Wave"
        if res['action'] == "show" and 'video_title' in res:
            command = '/Applications/VLC.app/Contents/MacOS/VLC --play-and-exit ./videos/' + res['video_title'] + '.mov'
            print command
            call(command , shell=True)

