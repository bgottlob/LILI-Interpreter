# Considers personal pronouns as nouns as long as any type of tagged noun (proper noun, etc.)
def is_noun(tag):
    """
    Checks if a part of speech tag represents a noun. The tags "PRP" and those that begin with "NN" are considered nouns.

    Args:
        tag (str): The part of speech tag to be checked

    Returns:
        bool: True if the tag represents a noun, False if not
    """
    return (tag == "PRP" or tag.startswith("NN"))

# IN is the general preposition tag, but the word "to" has its own TO tag whenever it is being used as a preposition
# The distinction between words tagged as TO and those tagged as IN is not important to interpretation with the basic rules right now
def is_preposition(tag):
    """
    Checks if a part of speech tag represents a preposition. The tags "TO" and "IN" considered to be prepositions.

    Args:
        tag (str): The part of speech tag to be checked

    Returns:
        bool: True if the tag represents a preposition, False if not
    """
    return (tag == "TO" or tag == "IN")

# Assumes that input sentence has been tagged with POS
# Assumes first noun is always a person that will be followed
# Assumes that second noun (if found) is always a place to follow the person to
def object_dict_follow(sent):
    """
    Extracts objects out of a sentence that contains "follow" as its main action

    Rules:
    1. The first noun encountered is always the 'person'
    2. The second noun (if included) is always the 'place'

    Objects:
    'person' - The person who will be followed
    'place' - The location that the person will be followed to

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: A dictionary mapping key words to semantic object categories
    """

    object_dict = {}
    for token in sent:
        if is_noun(token[1]):
            # The current length of object_dict shows how many other nouns have been extracted from the sentence
            if len(object_dict) == 0:
                object_dict["person"] = token[0]
            elif len(object_dict) == 1:
                object_dict["place"] = token[0]

    return object_dict

def object_dict_turn(sent):
    """
    Extracts objects out of a sentence that contains "turn" as its main action. Currently uses the same rules as object_dict_move - see that method for more details

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: A dictionary mapping key words to semantic object categories
    """

    return object_dict_move(sent)

def object_dict_stop(sent):
    """
    Extracts objects out of a sentence that contains "stop" as its main action. Currently returns an empty dictionary.

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: A dictionary mapping key words to semantic objects - currently returns an empty dictionary under all inputs
    """
    return {}

def object_dict_move(sent):
    """
    Extracts objects out of a sentence that contains "move" as its main action

    Rules:
    1. Only the first noun is detected as an object
    1. If the first noun is preced by a preposition, then it is the 'place'
    2. If the first noun is not preceded by a preposition, then it is the 'direction'

    Objects:
    'place' - A location to move to
    'direction' - A direction to move in

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: A dictionary mapping key words to semantic objects
    """

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

def object_dict_talk(sent):
    """
    Extracts objects out of a sentence that contains "talk" as its main action

    Rules:
    1. The noun to come after the word "about" is the 'topic'
    2. The noun to come after any preposition that is not "about" is the 'person'
    3. Other nouns will be tagged as 'unknown'

    Objects:
    'person' - The person to talk to
    'topic' - The subject to talk about
    'unknown' - The role of this noun is not known

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: A dictionary mapping key words to semantic objects
    """

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
    """
    Extracts objects out of a sentence that contains "show" as its main action

    Rules:
    1. The verb preceded by a "to" is the 'shown_action'
    2. The noun that is not preceded by a determiner or "to" is the 'person'
    3. The noun that is preceded either by a determiner or the 'shown_action' is the 'object'

    Objects:
    'shown_action' - The action that will be shown in a video
    'person' - The person who will be shown the action or object
    'object' - The object that is acted on in the video or a static object to be shown as a picture
    'video_title' - The title of the video to be played - it is currently generated by concatentating the 'shown_action' with the 'object'

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: A dictionary mapping key words to semantic objects
    """

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
