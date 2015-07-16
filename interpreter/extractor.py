from nltk.stem.snowball import SnowballStemmer

def is_direction(word):
    """
    Checks if a ``word`` represents a direction.

    The word is checked against a hard-coded list of directional words. If there is a match, then the ``word`` is determined to be a directional word. This function is present to provide a space to make this operation more robust in the future.

    Args:
        word (str): The word to be checked

    Returns:
        bool: ``True`` if the ``word`` represents a directional word, ``False`` if not
    """
    # Words that can be interpreted as a direction - for use with the move and turn object extractors
    directional_words = ["left", "right", "up", "down", "forward", "backward"]

    for direction in directional_words:
        if word.lower() == direction:
            return True

    return False



def is_noun(tag):
    """
    Checks if a part of speech tag represents a noun. The tags ``"PRP"`` and those that begin with ``"NN"`` are considered nouns.

    Args:
        tag (str): The part of speech tag to be checked

    Returns:
        bool: ``True`` if the tag represents a noun, ``False`` if not
    """
    # Considers personal pronouns as nouns as long as any type of tagged noun (proper noun, etc.)
    return (tag == "PRP" or tag.startswith("NN"))

def is_preposition(tag):
    """
    Checks if a part of speech tag represents a preposition. The tags ``"TO"`` and ``"IN"`` considered to be prepositions.

    Args:
        tag (str): The part of speech tag to be checked

    Returns:
        bool: ``True`` if the tag represents a preposition, ``False`` if not
    """
    # IN is the general preposition tag, but the word "to" has its own TO tag whenever it is being used as a preposition
    return (tag == "TO" or tag == "IN")

def object_dict_follow(sent):
    """
    Extracts objects out of a sentence that contains *follow* as its :ref:`action <action>`

    Rules:

    1. The first noun encountered is always the *person*
    2. The second noun (if included) is always the *place*

    Objects:

    1. *person* - The person who will be followed
    2. *place* - The location that the person will be followed to

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: An :ref:`object dictionary <object-dictionary>` for the command
    """

    object_dict = {}
    for token in sent:
        if is_noun(token[1]):
            # The current length of object_dict shows how many other nouns have been extracted from the sentence
            if len(object_dict) == 0:
                object_dict["person"] = token[0].lower()
            elif len(object_dict) == 1:
                object_dict["place"] = token[0].lower()

    return object_dict

def object_dict_turn(sent):
    """
    Extracts objects out of a sentence that contains *turn* as its :ref:`action <action>`.

    Currently uses the same rules as :meth:`~interpreter.extractor.object_dict_move`

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: An :ref:`object dictionary <object-dictionary>` for the command
    """

    return object_dict_move(sent)

def object_dict_stop(sent):
    """
    Extracts objects out of a sentence that contains *stop* as its :ref:`action <action>`

    Currently returns an empty dictionary.

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: An :ref:`object dictionary <object-dictionary>` for the command - currently returns an empty dictionary under all inputs
    """
    return {}

def object_dict_move(sent):
    """
    Extracts objects out of a sentence that contains *move* as its :ref:`action <action>`

    Rules:

    1. Only the first noun is detected as an object
    2. If the first noun is preced by a preposition, then it is the *place*
    3. If the first noun is not preceded by a preposition, then it is the *direction*

    Objects:

    1. *place* - A location to move to
    2. *direction* - A direction to move in

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: An :ref:`object dictionary <object-dictionary>` for the command
    """

    object_dict = {}
    prep_found = False

    for token in sent:
        # The directional words tend to be tagged as one of these four parts of speech
        if (token[1] == "VBD" or token[1] == "NN" or token[1] == "IN" or token[1] == "RB") and (is_direction(token[0])):
            object_dict["direction"] = token[0].lower()
        elif is_noun(token[1]):
            object_dict["place"] = token[0].lower()

    return object_dict

def object_dict_talk(sent):
    """
    Extracts objects out of a sentence that contains *talk* as its :ref:`action <action>`

    Rules:

    1. The noun to come after the word *about* is the *topic*
    2. The noun to come after any preposition that is not *about* is the *person*
    3. Other nouns will be tagged as *unknown*

    Objects:

    1. *person* - The person to talk to
    2. *topic* - The subject to talk about
    3. *unknown* - The role of this noun is not known

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: An :ref:`object dictionary <object-dictionary>` for the command
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
                object_dict["person"] = token[0].lower()
                prep_found = False
            elif about_found and not prep_found:
                object_dict["topic"] = token[0].lower()
                about_found = False
            else:
                obj_tag = "unknown"
                object_dict["unknown"] = token[0].lower()

    return object_dict

def object_dict_show(sent):
    """
    Extracts objects out of a sentence that contains *show* as its :ref:`action <action>`

    Rules:

    1. The verb preceded by a *to* is the *shown_action*
    2. The noun that is not preceded by a determiner or *to* is the *person*
    3. The noun that is preceded either by a determiner or the *shown_action* is the *object*

    Objects:

    1. *shown_action* - The action that will be shown in a video
    2. *person* - The person who will be shown the action or object
    3. *object* - The object that is acted on in the video or a static object to be shown as a picture
    4. *video_title* - The title of the video to be played; it is currently generated by concatentating the *shown_action* with the *object*

    Args:
        sent (list): A part of speech tagged list of tokens representing a sentence

    Returns:
        dict: An :ref:`object dictionary <object-dictionary>` for the command
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
                object_dict["object"] = token[0].lower()
            else:
                object_dict["person"] = token[0].lower()
        elif token[1] ==  "VB":
            if to_found:
                object_dict["show_action"] = token[0].lower()
                prec_found = True

    # Create the stemmer to get root words if needed
    stemmer = SnowballStemmer("english")
    if "object" in object_dict:
        search_res = binary_search_shown_words(object_dict["object"], known_shown_objects)
        if search_res > -1:
            object_dict["object"] = first_shown_objects[search_res]
        else:
            # If the object word wasn't found, try looking for its stem
            stem = stemmer.stem(object_dict["object"])
            search_res = binary_search_shown_words(stem, known_shown_objects)
            if search_res > -1:
                object_dict["object"] = first_shown_objects[search_res]


    if "show_action" in object_dict:

        search_res = binary_search_shown_words(object_dict["show_action"], known_shown_actions)
        if search_res > -1:
            object_dict["show_action"] = first_shown_actions[search_res]
        else:
            # If the show action word wasn't found, try looking for its stem
            stem = stemmer.stem(object_dict["show_action"])
            search_res = binary_search_shown_words(stem, known_shown_actions)
            if search_res > -1:
                object_dict["show_action"] = first_shown_actions[search_res]

        video_title = object_dict["show_action"]
        if "object" in object_dict:
            video_title = video_title + "-" + object_dict["object"]
        object_dict["video_title"] = video_title.lower()

    return object_dict

def build_shown_words(filename):
    # Initializing data structures
    known_words = []
    first_words = []
    line_num = 0

    # Start reading input file of known actions
    inp_file = open(filename, "rb")
    for line in inp_file:
        line = line.strip().lower()
        # Checks to make sure the line isn't an empty string after trimming whitespace
        # Blank lines are ignored completely
        if line:
            words = line.split(",")
            # Checks to make sure there is at least one action, avoid exception
            if len(words) > 0:
                try:
                    first_words.append(words[0])
                    for word in words:
                        word = word.strip()
                        # Add each known action and its action set index to the list to be returned
                        known_words.append((word, line_num))
                    line_num += 1
                except AttributeError: # Occurs if getattr fails
                    sys.stderr.write("Error: There is no object extraction function called " + func_name + "\n")
                except StandardError as err: # Catches any other error
                    sys.stderr.write(str(err) + "\n")

    # Sorts the list of known actions by A-Z alphabetical order
    known_words = sorted(known_words, key=lambda tup: tup[0])

    return (known_words, first_words)

def binary_search_shown_words(target, pool):

    # If the search pool has been exhausted, the target is not in the pool
    if (len(pool) == 0):
        return -1

    # Gets middle index of the remaining pool
    mid = len(pool)/2

    if target < pool[mid][0]: # Target must be in lower half of pool
        return binary_search_shown_words(target, pool[:mid])
    elif target > pool[mid][0]: # Target must be in higher half of pool
        return binary_search_shown_words(target, pool[mid+1:])
    else: # Match has been found
        return pool[mid][1]

# Builds synonym lists that are utilized when resolving shown actions and objects to words that are already known by LILI
shown_action_res = build_shown_words("input_files/known_words/known_shown_actions_small.txt")
shown_object_res = build_shown_words("input_files/known_words/shown_objects_small.txt")

known_shown_actions = sorted(shown_action_res[0], key=lambda tup: tup[0])
first_shown_actions = shown_action_res[1]

known_shown_objects = sorted(shown_object_res[0], key=lambda tup: tup[0])
first_shown_objects = shown_object_res[1]