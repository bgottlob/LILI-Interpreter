# This code will be used to test WordNet's ability to match words based on semantic similarity
from nltk.corpus import wordnet as wn
import csv

def verify_synset_name(ss_name, word, pos):
    """
    Checks if the name of a C{Synset} contains the given word and part of speech

    @param ss_name: The name of the C{Synset} to be verified
    @type ss_name: C{str}
    @param word: The word that the name of the C{Synset} should correspond to
    @type word: C{str}
    @param pos: The part of speech that the name of the C{Synset} should correspond to (must be a single character)
    @type pos: C{str}
    """
    splitStr = ss_name.split(".")
    return (splitStr[0] == word and splitStr[1] == pos)

# Maps all unknown words to known words based on semantic similarity - examines all synsets of both known and unknown words
# List assumptions about files
# Handle cases where current score matches the maximum score
# Return array of results
def sem_sim_test1(known_words_filename, unknown_words_filename, pos):
    # Start an empty list of results
    results = []

    # Start an empty list of known verbs
    known_words = []

    # Open the CSV file of known words and read contents
    with open(known_words_filename, "rb") as known_words_file:
        known_word_reader = csv.reader(known_words_file)
        # Assuming first line in CSV file is a header
        next(known_word_reader, None)
        for row in known_word_reader:
            # Add to the list of known verbs
            known_words.append(row[0].lower())

    # Open the file of unknown words and begin processing
    unknown_words_file = open(unknown_words_filename, "rb")
    for line in unknown_words_file:
        max_sem_sim_score = -1 # If words are not semantically similar, this value will not be changed
        max_unknown_synset = None
        max_known_synset = None
        known_choice = 'No match found'
        match_found = False
        unknown = line.lower().strip()
        for known in known_words:
            for known_synset in wn.synsets(known):
                if verify_synset_name(known_synset.name(), known, pos):
                    for unknown_synset in wn.synsets(unknown):
                        if verify_synset_name(unknown_synset.name(), unknown, pos):
                            sem_sim_score = unknown_synset.path_similarity(known_synset)
                            if sem_sim_score > max_sem_sim_score:
                                max_sem_sim_score = sem_sim_score
                                max_unknown_synset = unknown_synset
                                max_known_synset = known_synset
                                known_choice = known
                                match_found = True
        if match_found:
            results.append(SemanticSimilarityResult(unknown, known_choice, max_unknown_synset.name(), max_known_synset.name(), max_unknown_synset.definition(), max_known_synset.definition(), max_sem_sim_score))
        else:
            results.append(SemanticSimilarityResult(unknown,"No match found","N/A","N/A","N/A","N/A",max_sem_sim_score))

        print ("Finished processing " + unknown)

    return results

def process_results(results_list):
    """
    Sorts a list of C{SemanticSimilarityResult} objects in descsending order by semantic similarity score

    @param results_list: The list of C{SemanticSimilarityResult} objects to be sorted
    @type results_list: C{list}
    @return: The sorted list of C{SemanticSimilarityResult} objects
    @rtype: C{list}
    """
    return sorted(results_list, key=lambda res:res.sem_sim_score, reverse=True)

def output_results(results_list, output_filename):
    """
    Prints the given list of C{SemanticSimilarityResult} objects to a CSV file

    Given a list of C{SemanticSimilarityResult} objects and a .csv filename, writes the values of the result objects to specified file.

    @param results_list: The list of C{SemanticSimilarityResult} objects to be printed to the CSV file
    @type results_list: C{list}
    @param output_filename: The name of the CSV file to be written to
    @type output_filename: C{str}
    """
    # Open the output file for writing
    out_file = open(output_filename, "wb")
    out_writer = csv.writer(out_file)

    # Writes a header to the output file
    out_writer.writerow(("unknown","known","unknown_synset","known_synset","unknown_definition","known_definition","semantic_similarity_score"))

    for res in results_list:
        out_writer.writerow((res.unknown, res.known, res.unknown_synset, res.known_synset, res.unknown_definition, res.known_definition,
        res.sem_sim_score))

def filter_results(results_list, threshold):
    """
    Returns a filtered list of the results of the given list based on the given semantic similarity score threshold

    Given a list of C{SemanticSimilarityResult} objects and a threshold value, filters the list removing result objects with semantic similarity scores less than the threshold or greater or equal to 1 (the score will not exceed 1). Returns the filtered list.

    @param results_list: The list of C{SemanticSimilarityResult} objects to be filtered
    @type results_list: C{list}
    @param threshold: The semantic similarity score threshold at which results with a score lower than this threshold will be removed from C{results_list}
    @type threshold: C{number}
    @return: The filtered list of C{SemanticSimilarityResult} objects
    @rtype: C{list}
    """
    return [res for res in results_list if res.sem_sim_score >= threshold and res.sem_sim_score < 1]


class SemanticSimilarityResult:

    def __init__(self, unknown, known, unknown_synset, known_synset, unknown_definition, known_definition, sem_sim_score):
        self.unknown = unknown
        self.known = known
        self.unknown_synset = unknown_synset
        self.known_synset = known_synset
        self.unknown_definition = unknown_definition
        self.known_definition = known_definition
        self.sem_sim_score = sem_sim_score