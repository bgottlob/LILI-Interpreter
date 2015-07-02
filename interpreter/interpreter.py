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
        res (list): A list of preprocessed tokens from the sentence

    Note:
        Do not do any part of speech tagging in this function. It is a computation intensive task and may not be needed for all commands.
    """
    res = nltk.word_tokenize(text)
    return res

# Takes a tokenized sentence and a of known action verbs
# Assumptions: the first occurrence of any of the words in the known_actions list is the main action
# Does not take part of speech tags into account at all because the main action is generally recognized as a noun
# If the POS tagger was 100% accurate, the first verb would most likely be the main action
# In basic examples that are expected to be used with LILI, the assumption and approach taken is accurate enough
def extract_action(sent, known_actions):
    token_index = 0
    for token in sent:
        token = token.lower()
        search_res = binary_search_actions(token, known_actions)
        if search_res > -1:
            return (search_res, token_index)
    # If no main action is found, return (-1,0)
    return (-1, 0)

def binary_search_actions(target, pool):

    if (len(pool) == 0):
        return -1

    mid = len(pool)/2
    
    if target < pool[mid][0]:
        return binary_search_actions(target, pool[:mid])
    elif target > pool[mid][0]:
        return binary_search_actions(target, pool[mid+1:])
    else:
        return pool[mid][1]

def generate_object_dict(sent, action_tuple):

    tagged_sent = nltk.pos_tag(sent)

    print "Tagged sentence:"
    print tagged_sent

    # Remove the main action from the sentence - it does not need to be considered when extracting objects
    # Maybe get rid of the action and everything behind it as well - can't think of any important text that could come before the main action
    trimmed_sent = tagged_sent[:action_tuple[1]] + tagged_sent[action_tuple[1]+1:]

    object_dict = object_extractor_functions[action_tuple[0]](trimmed_sent)

    return object_dict

def generate_json(action, object_dict):
    result = object_dict
    result["action"] = action
    return result
    #return json.dumps(result)

def build_action_structures(filename):
    inp_file = open(filename, "rb")
    known_actions = []
    object_dict_functions = []
    line_num = 0
    for line in inp_file:
        line = line.strip().lower()
        # Checks to make sure the line isn't an empty string after trimming whitespace
        if line:
            actions = line.split(",")
            # Checks to make sure there is at least one action
            if len(actions) > 0:
                func_name = "object_dict_" + actions[0]
                try:
                    object_dict_functions.append(getattr(extractor, "object_dict_" + actions[0]))
                    for action in actions:
                        action = action.strip()
                        known_actions.append((action, line_num))
                    line_num += 1
                except AttributeError:
                    print "Error: There is no object extraction function called " + func_name
                except StandardError as err:
                    print str(err)

    # Sorts the list of known actions by A-Z alphabetical order
    known_actions = sorted(known_actions, key=lambda tup: tup[0])

    return (known_actions, object_dict_functions)

def test_sent(sent_text):
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

res = build_action_structures("known_actions.txt")
known_actions = res[0]
object_extractor_functions = res[1]

print str(known_actions)
print str(object_extractor_functions)
print str(test_sent("Blorggdfslgk me to play tennis"))
