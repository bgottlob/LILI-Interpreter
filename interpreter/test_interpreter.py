import interpreter as i

def test_follow1():
    assert i.test_sent("Follow me") == { "action": 3, "person": "me" }

def test_follow2():
    assert i.test_sent("Follow Jonathan to the kitchen") == {"action":3, "person": "Jonathan", "place":"kitchen"}

def test_move1():
    assert i.test_sent("Move to the bathroom") == {"action": 0, "place": "bathroom"}

"""def test_move2():
    assert i.test_sent("Move left") == {"action":0, "direction": "left"}

def test_move3():
    assert i.test_sent("Move right") == {"action":0, "direction":"right"}

def test_move4():
    assert i.test_sent("Move to the right") == {"action":0, "direction":"right"}
"""
def test_stop1():
    assert i.test_sent("Stop") == {"action":2}

"""def test_talk1():
    assert i.test_sent("Speak to me about football") == {"action":4, "topic":"football"}
"""
def test_talk2():
    assert i.test_sent("Talk to Jonathan") == {"action":4, "person":"Jonathan"}

def test_talk3():
    assert i.test_sent("Talk about movies") == {"action":4, "topic":"movies"}

def test_talk4():
    assert i.test_sent("Talk with Brandon about computers") == {"action":4, "topic":"computers", "person":"Brandon"}

def test_show1():
    assert i.test_sent("TeacH me how to wash my hands") == {"action":5, "person":"me", "show_action":"wash", "object":"hands", "video_title":"wash-hands"}

def test_show2():
    assert i.test_sent("Show the car") == {"action":5, "object":"car"}

def test_show3():
    assert i.test_sent("Show her what a cow is") == {"action":5, "object": "cow"}

def test_show4():
    assert i.test_sent("Show me what to do when I want to wash my hands") == {"action":5, "person":"me", "show_action":"wash", "object":"hands", "video_title":"wash-hands"}

def test_show5():
    assert i.test_sent("Show me to play tennis") == {"action":5, "person":"me", "show_action":"play", "object":"tennis", "video_title":"play-tennis"}

def test_uk():
    assert i.test_sent("Blorg me to play tennis") == {"error":"Main action not found"}
