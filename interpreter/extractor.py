# Considers personal pronouns as nouns as long as any type of tagged noun (proper noun, etc.)
def is_noun(tag):
    return (tag == "PRP" or tag.startswith("NN"))

# IN is the general preposition tag, but the word "to" has its own TO tag whenever it is being used as a preposition
# The distinction between words tagged as TO and those tagged as IN is not important to interpretation with the basic rules right now
def is_preposition(tag):
    return (tag == "TO" or tag == "IN")

# Assumes that input sentence has been tagged with POS
# Assumes first noun is always a person that will be followed
# Assumes that second noun (if found) is always a place to follow the person to
def object_dict_follow(sent):
    object_dict = {}
    for token in sent:
        if is_noun(token[1]):
            if len(object_dict) == 0:
                object_dict["person"] = token[0]
            elif len(object_dict) == 1:
                object_dict["place"] = token[0]

    return object_dict

def object_dict_turn(sent):
    return object_dict_move(sent)

def object_dict_stop(sent):
    return {}

# Only the first noun will be detected in this case
# If that first noun is preceded by a preposition, then it is a place for LILI to move to
# If the first noun is not preceded by a preposition, then it is the direction for LILI to move in
def object_dict_move(sent):

    object_dict = {}
    prep_found = False

    for token in sent:
        if is_preposition(token[1]):
            prep_found = True
        elif is_noun(token[1]):
            if prep_found:
                obj_tag = "place"
            else:
                obj_tag = "direction"
            object_dict[obj_tag] = token[0]

    return object_dict

# The first noun to follow "about" is the topic
# The first noun to follow any preposition besides "about" is the person to talk to
def object_dict_talk(sent):

    object_dict = {}
    prep_found = False
    about_found = False

    for token in sent:

        if token[0].lower() != "about" and is_preposition(token[1]):
            prep_found = True
        elif token[0].lower() == "about":
            about_found = True

        if is_noun(token[1]):
            if prep_found and not about_found:
                object_dict["person"] = token[0]
                prep_found = False
            elif about_found and not prep_found:
                object_dict["topic"] = token[0]
                about_found = False
            else:
                obj_tag = "unknown"
                object_dict["unknown"] = token[0]

    return object_dict

def object_dict_show(sent):

    object_dict = {}
    prec_found = False
    to_found = False

    for token in sent:
        if token[1] == "TO":
            to_found = True
        elif token[1] == "DT":
            prec_found = True
        elif is_noun(token[1]):
            if prec_found:
                object_dict["object"] = token[0]
            else:
                object_dict["person"] = token[0]
        elif token[1] ==  "VB":
            if to_found:
                object_dict["show_action"] = token[0]
                prec_found = True

    if to_found:
        object_dict["video_title"] = object_dict["show_action"] + "-" + object_dict["object"]

    return object_dict