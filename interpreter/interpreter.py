import nltk
import json
import extractor

# Perform any preprocessing tasks on the text - currently only tokenizes text
def preprocess_text(text):
    """
    Preprocesses a raw text sentence. Currently only tokenizes the sentence.

    Used to do any preprocessing on a sentence in raw text. Currently, the only preprocessing operation is tokenizing the sentence into individual words and punctuation marks.

    Args:
        sent (str): A string containing a command sentence

    Returns:
        list: A list of preprocessed tokens from the sentence

    Note:
        Do not do any part of speech tagging in this function. It is a compute-intensive task and may not be needed for all commands (i.e. erroneous situations).
    """
    res = nltk.word_tokenize(text)
    return res

def extract_action(sent, known_actions):
    """
    Finds the :ref:`action <action>` that LILI can respond to, given a tokenized command sentence and a list of known actions.

    The action is most likely one of the first couple of words of the command, so the sentence is processed from first word to last word. Each word in the sentence is searched for in the given list of known actions. The first word that is found in the known actions array is determined to be the action, and processing ends. A binary search algorithm is used to search for the word to keep processing time short even with large lists of known actions.

    A tuple that contains two values is returned:

       1. The action's :ref:`action set index value <action-set-index>`
       2. The position of the found word in the sentence represented as an index value

    Args:
        sent (list): A list containing the tokenized sentence
        known_actions (list): A list of tuples ``(str, int)``, each containing the string of a known action and its action set index

    Returns:
        (int, int): A tuple that contains the action's set index and position in the command sentence

           * Returns (-1, 0) if no action is found
    """

    token_index = 0
    for token in sent:
        token = token.lower()
        search_res = binary_search_actions(token, known_actions)
        if search_res > -1:
            return (search_res, token_index)
    # If no main action is found, return (-1,0)
    return (-1, 0)

def binary_search_actions(target, pool):
    """
    Binary search to find a ``target`` word in a ``pool`` of possibilities.

    This binary search is used to find a target word with fast performance even with a large search pool. It is implemented recursively to provide a simpler implementation. It assumes that the known actions list is sorted in descending (A to Z) order.

    Args:
        target (str): The word to search for
        pool (list): A list of tuples ``(str, int)``, each containing the string of a known :ref:`action <action>` and its :ref:`action set index <action-set-index>`

    Return:
        int: The action set index of the ``target`` word if it is found in the ``pool``

           * Returns -1 if no match is found
    """

    # If the search pool has been exhausted, the target is not in the pool
    if (len(pool) == 0):
        return -1

    # Gets middle index of the remaining pool
    mid = len(pool)/2

    if target < pool[mid][0]: # Target must be in lower half of pool
        return binary_search_actions(target, pool[:mid])
    elif target > pool[mid][0]: # Target must be in higher half of pool
        return binary_search_actions(target, pool[mid+1:])
    else: # Match has been found
        return pool[mid][1]

def generate_object_dict(sent, action_tuple, object_extractor_functions):
    """
    Creates an :ref:`object dictionary <object-dictionary>` according to the provided :ref:`action <action>`.

    Begins by part of speech tagging the sentence, then trimming the action out of the sentence so that it is not re-processed (depending on implementation details, the presence of the main action in the sentence may throw off results). Then calls the appropriate :ref:`object extractor function <object-extractor-function>` to create the object dictionary. The called object extractor is determined by the action's :ref:`set index value <action-set-index>`.

    Args:
        sent (list): A list containing tokens of the command sentence
        action_tuple (int, int): A tuple ``(action_set_index, position_in_sent)``:

           1. ``action_set_index`` - The action's action set index
           2. ``position_in_sent`` - An index representing the action's position in the command sentence

           * This tuple is in the same format as the return value of :meth:`~interpreter.interpreter.extract_action`

    Returns:
        dict: An object dictionary for the command
    """

    # Tag the sentence with parts of speech
    tagged_sent = nltk.pos_tag(sent)

    # Output for debugging
    print "Tagged sentence:"
    print tagged_sent

    # Remove the main action from the sentence - it does not need to be considered when extracting objects
    # If problems occur later down the road, maybe get rid of the action and everything behind it as well
    # Can't think of any important text that could come before the main action
    trimmed_sent = tagged_sent[:action_tuple[1]] + tagged_sent[action_tuple[1]+1:]

    # Call the main action's corresponding function extractor
    object_dict = object_extractor_functions[action_tuple[0]](trimmed_sent)

    return object_dict

def generate_json(action, object_dict):
    """
    Returns a JSON string representation of an :ref:`object dictionary <object-dictionary>` with an entry for the action's :ref:`set index <action-set-index>`

    First adds the :ref:`action <action>` and its set index to the object dictionary, then uses the ``json`` module to dump the final dictionary into a JSON string.

    Args:
        action (int): The set index of the action
        object_dict (dict): The object dictionary to be converted to a JSON string

    Returns:
        str: A JSON string representation of the object dictionary and the action set index
    """

    result = object_dict
    result["action"] = first_actions[action]
    return result
    #return json.dumps(result)

def build_action_structures(filename):
    """
    MUST UPDATE FOR CREATING THE LIST OF FIRST ACTIONS
    Given a filename that contains a list of known :ref:`actions <action>`, generates the data structures needed to interpret commands.

    Opens a file of known actions, where each action set is represented on one line (see :ref:`this part of the interpreter demo <initial-setup>` for details on the input file). For each word in this file, a tuple *(str, int)* is generated that contains that word along with its :ref:`action set index <action-set-index>`. This tuple is then appended to the list of known actions. This list is sorted by A-Z order before it is returned to prepare it for binary search operations.

    A list of :ref:`object extractor functions <object-extractor-function>` is created to correspond to the action set indices be called later on. For each line, another function is added to the extractor function list. To determine the name of the extractor function to be added next, the first word in the action set is appended to the end of the string ``"object_dict\_"``. Once the function name string is built, the function is retreived from the extractor module and is appended to the extractor function list.

    Args:
        filename (str): The name of the file that contains the list of known actions

    Returns:
        (list, list): A tuple ``(known_actions, object_extractor_functions)`` containing:

           1. ``known_actions`` - The list of tuples each containing a known action and its set index
           2. ``object_extractor_functions`` - The list of object extractor functions whose list indices correspond with the appropriate action set indices

    Note:
        This function only needs to run when the input file is updated. It should not be run every time a new command needs to be interpreted.
    """

    # Initializing data structures
    known_actions = []
    object_dict_functions = []
    first_actions = []
    line_num = 0

    # Start reading input file of known actions
    inp_file = open(filename, "rb")
    for line in inp_file:
        line = line.strip().lower()
        # Checks to make sure the line isn't an empty string after trimming whitespace
        # Blank lines are ignored completely
        if line:
            actions = line.split(",")
            # Checks to make sure there is at least one action, avoid exception
            if len(actions) > 0:
                func_name = "object_dict_" + actions[0]
                try:
                    # Gets the corresponding object extractor function from the extractor module and adds it to the list to be returned
                    object_dict_functions.append(getattr(extractor, func_name))
                    first_actions.append(actions[0])
                    for action in actions:
                        action = action.strip()
                        # Add each known action and its action set index to the list to be returned
                        known_actions.append((action, line_num))
                    line_num += 1
                except AttributeError: # Occurs if getattr fails
                    print "Error: There is no object extraction function called " + func_name
                except StandardError as err: # Catches any other error
                    print str(err)

    # Sorts the list of known actions by A-Z alphabetical order
    known_actions = sorted(known_actions, key=lambda tup: tup[0])

    return (known_actions, object_dict_functions, first_actions)

def interpret_sent(sent_text):
    """
    Implements the order of execution (pipeline) of interpreting a sentence - utilized for checking test cases
    """
    print "Preprocessing this sentence:"
    print sent_text
    sent = preprocess_text(sent_text)
    print "Tokenized:"
    print sent
    action_tuple = extract_action(sent, known_actions)

    # If this occurred, the action was not recognized
    if action_tuple[0] < 0:
        error_dict = {"error":"Main action not found"}
        #return json.dumps(error_dict)
        return error_dict

    print "Action Tuple:"
    print action_tuple
    object_dict = generate_object_dict(sent, action_tuple, object_extractor_functions)
    return generate_json(action_tuple[0], object_dict)
    print "\n"

def build_sem_sim_structure(filename):
    """
    Sem sim module will generate the file, and this function will build the structure according to the file
    The format of each element of these lists will be: (unknown_word, known_word)
    """

# When imported, this module builds the structures needed to interpret commands
res = build_action_structures("interpreter/new_known_actions.txt")
known_actions = res[0]
object_extractor_functions = res[1]
first_actions = res[2]
print first_actions