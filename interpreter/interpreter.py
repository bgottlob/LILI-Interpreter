import nltk
import json
import extractor

# Perform any preprocessing tasks on the text - currently only tokenizes text
def preprocess_text(text):
    """
    Preprocesses a raw text sentence. Currently only breaks it up into tokens.

    Used to do any preprocessing on a sentence in raw text. Currently, the only preprocessing operation is tokenizing the sentence into individual words and punctuation marks.

    Args:
        sent (str): A string containing a command sentence

    Returns:
        list: A list of preprocessed tokens from the sentence

    Note:
        Do not do any part of speech tagging in this function. It is a computation intensive task and may not be needed for all commands.
    """
    res = nltk.word_tokenize(text)
    return res

def extract_action(sent, known_actions):
    """
    Finds the main action that LILI can respond to given a tokenized command sentence.

    The main action is most likely one of the first couple of words of the command, so the sentence is processed from first to last word. Each word in the sentence is searched for in an array of known actions. The first word that is found in the known actions array is determined to be the main action, and processing ends. A binary search algorithm is used to search for the word to keep processing time short even with large lists of known actions. A tuple that contains two values is returned. The first value is an index value that corresponds to the set of words that the found word maps to. The second value is an index value representing the position of the found word in the sentence.

    Args:
        sent (list): A list containing the tokenized sentence
        known_actions (list): A list of tuples, each containing the string of an action and an index value of the set of actions it corresponds to

    Returns:
        (int, int): Tuple - first int is an index value that maps the found word to the other actions it is synonymous with - second int is an index value representing the position of the found word in the given sentence - Returns (-1, 0) if no main action is found
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
    Binary search to find a target word in a pool of possibilities.

    This binary search is used to find a target word with fast performance even with a large search pool. It is implemented recursively to provide a simpler implementation. Assumes that the known actions list is sorted in descending (A to Z) order.

    Args:
        target (str): The word to search for
        pool (list): A list of tuples - the first value of each tuple is the word to compare agains - the second value in each tuple is an index value that corresponds to a set of synonymous actions

    Return:
        int: The index of the found word's corresponding set of synonymous actions - returns -1 if no match is found
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

def generate_object_dict(sent, action_tuple):
    """
    Creates a dictionary of keywords from the sentence that are objects of the action to be taken.

    Begins by part of speech tagging the sentence, then trimming the main action out of the sentence, so that it is not re-processed (depending on implementation details, the presence of the main action in the sentence may throw off results). Then calls upon the appropriate object extractor from the extractor module. The called object extractor is determined by the index value of the action that maps it to its set of synonymous actions.

    Args:
        sent (list): A list containing the tokenized sentence
        action_tuple (int, int): Tuple - first int is an index value that maps the found word to the other actions it is synonymous with - second int is an index value representing the position of the found word in the given sentence - Returns (-1, 0) if no main action is found - same as the return value for extract_action

    Returns:
        dict: A dictionary that maps words from the sentence to types of objects that will be acted on
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
    Returns a JSON string representation of an object dictionary with an entry for the main action's index.

    First adds the main action and its index to the object dictionary, then uses the json module to dump the final dictionary into a JSON string.

    Args:
        action (int): The index of the action that corresponds to its synonym set
        object_dict (dict): An object dictionary to be converted to a JSON string

    Returns:
        str: A JSON string representation of the object dictionary and the main action index
    """
    result = object_dict
    result["action"] = action
    return result
    #return json.dumps(result)

def build_action_structures(filename):
    """
    Given a filename that contains a list of known main actions, generates the data structures needed to interpret commands.

    Opens a file of known actions, where each action set is represented on one line, and each word contained in that action set is separated by a comma (if there are multiple words in that set). For each word in this file, a tuple is generated that contains that word along with the line number it is found on in the file (starting with 0). That line number value is the main action's index, which maps the word to it's set of synonymous actions. This tuple is then appended to the list of known actions. This list is sorted by A-Z order before it is returned to prepare it for binary search operations. A list of object extractor functions is created to correspond to the main action indices to be called later on. For each line, another function is added to the extractor function list. To determine the name of the extractor function to be added next, the first word in the action set (effectively the first word in the current line) is appended to the end of the string "object_dict_". Once the function name string is built, the function is retreived from the extractor module and is appended to the extractor function list.

    Args:
        filename (str): The path (or filename if in the current directory) of the file that contains the list of known actions

    Returns:
        (list, list): A tuple containing the two list structures needed to interpret sentences. The first list is the sorted list of known actions coupled with their aciton index values. The second list is a list of object extractor functions whose list indices correspond with the appropriate action index

    Note:
        This function only needs to run when the file is updated. It should not be run every time a new command needs to be interpreted.
    """

    # Initializing data structures
    known_actions = []
    object_dict_functions = []
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
                try:
                    # Gets the corresponding object extractor function from the extractor module and adds it to the list to be returned
                    object_dict_functions.append(getattr(extractor, "object_dict_" + actions[0]))
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

    return (known_actions, object_dict_functions)

def test_sent(sent_text):
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
    object_dict = generate_object_dict(sent, action_tuple)
    return generate_json(action_tuple[0], object_dict)
    print "\n"

"""res = build_action_structures("known_actions.txt")
known_actions = res[0]
object_extractor_functions = res[1]

print str(known_actions)
print str(object_extractor_functions)
print str(test_sent("Blorggdfslgk me to play tennis"))"""
