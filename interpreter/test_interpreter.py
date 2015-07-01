import interpreter as i

def test_follow1():
    assert i.test_sent("Follow me") == { "action": "follow", "person": "me" }

def test_follow2():
    assert i.test_sent("Follow Jonathan to the kitchen") == {"action":"follow", "person": "Jonathan", "place":"kitchen"}

def test_move1():
    assert i.test_sent("Move to the bathroom") == {"action": "move", "place": "bathroom"}

def test_move2():
    assert i.test_sent("Move left") == {"action":"move", "direction": "left"}

def test_move3():
    assert i.test_sent("Move right") == {"action":"move", "direction":"right"}

def test_move4():
    assert i.test_sent("Move to the right") == {"action":"move", "direction":"right"}

def test_stop1():
    assert i.test_sent("Stop") == {"action":"stop"}

def test_talk1():
    assert i.test_sent("Talk to me about football") == {"action":"talk", "topic":"football"}

def test_talk2():
    assert i.test_sent("Talk to Jonathan") == {"action":"talk", "person":"Jonathan"}

def test_talk3():
    assert i.test_sent("Talk about movies") == {"action":"talk", "topic":"movies"}

def test_talk4():
    assert i.test_sent("Talk with Brandon about computers") == {"action":"talk", "topic":"computers", "person":"Brandon"}

def test_show1():
    assert i.test_sent("Show me how to wash my hands") == {"action":"show", "person":"me", "show_action":"wash", "object":"hands", "video_title":"wash-hands"}

def test_show2():
    assert i.test_sent("Show the car") == {"action":"show", "object":"car"}

def test_show3():
    assert i.test_sent("Show her what a cow is") == {"action":"show", "object": "cow"}

def test_show4():
    assert i.test_sent("Show me what to do when I want to wash my hands") == {"action":"show", "person":"me", "show_action":"wash", "object":"hands", "video_title":"wash-hands"}

def test_show5():
    assert i.test_sent("Show me to play tennis") == {"action":"show", "person":"me", "show_action":"play", "object":"tennis", "video_title":"play-tennis"}