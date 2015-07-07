# This code will be used to test WordNet's ability to match words based on semantic similarity
from nltk.corpus import wordnet as wn
import csv

def sem_sim_test2(known_words_filename, unknown_words_filename, **kwargs):
    """
    Tests semantic similarity mapping from unknown words to known words. Synsets of the unknown words are not known in advance and those of the known words are determined in advance.

    Accepts a CSV file of known words paired with their assumed WordNet synset and a text file of unknown words (with one word per line). Each unknown word is matched up with the known word that it is most semantically similar to. "Known" words are words that LILI has been preprogrammed to recognize or respond to in some way, while "unknown" words are those that LILI does not understand by default. Semantic similarity measures are made using WordNet and attempt to allow LILI to understand an open vocabulary beyond the words and phrases it has been preprogrammed to respond to. This test returns a list of :class:`~semsim.wntest.SemanticSimilarityResult` objects to store the results of the test for each unknown word.

    Args:
        known_words_filename (str): The filename of the CSV file containing known words paired with their assumed synsets
        unknown_words_filename (str): The filename of the text file containing unknown words

    Kwargs:
        pos (str): The part of speech of the words to be evaluated. Can have the values "verb", "noun", "adj", or "adv". If neither of these values are used or no value is provided, searching the synsets of the unknown word will not be filtered by part of speech, resulting in more processing time and potentially less accurate results

    Returns:
        list: The sorted list of :class:`~wntest.SemanticSimilarityResult` objects
    """

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
            known_words.append((row[0].lower(), row[1]))

    # Open the file of unknown words and begin processing
    unknown_words_file = open(unknown_words_filename, "rb")
    for line in unknown_words_file:

        max_sem_sim_score = -1 # If words are not semantically similar, this value will not be changed
        max_unknown_synset = None
        max_known_synset = None
        known_choice = "No match found"
        match_found = False
        unknown = line.lower().strip()

        for known_tuple in known_words:

            known = known_tuple[0]
            known_synset = wn.synset(known_tuple[1])

            if unknown in known_synset.lemma_names():
                sem_sim_score = 1

                if sem_sim_score > max_sem_sim_score:

                    max_sem_sim_score = sem_sim_score
                    max_unknown_synset = unknown_synset
                    max_known_synset = known_synset
                    known_choice = known
                    match_found = True

            else:
                # Check if the pos argument has been provided
                if 'pos' in kwargs:
                    pos = kwargs['pos']
                else:
                    pos = "none"

                if pos.lower() == "verb":
                    unknown_synsets = wn.synsets(unknown, wn.VERB)
                elif pos.lower() == "noun":
                    unknown_synsets = wn.synsets(unknown, wn.NOUN)
                elif pos.lower() == "adj":
                    unknown_synsets = wn.synsets(unknown, wn.ADJ)
                elif pos.lower() == "adv":
                    unknown_synsets = wn.synsets(unknown, wn.ADV)
                else:
                    unknown_synsets = wn.synsets(unknown)

                for unknown_synset in unknown_synsets:

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
    Sorts a list of :class:`~wntest.SemanticSimilarityResult` objects in descsending order by semantic similarity score

    Args:
        results_list (list): The list of :class:`~wntest.SemanticSimilarityResult` objects to be sorted

    Returns:
        list: The sorted list of :class:`~wntest.SemanticSimilarityResult` objects
    """
    return sorted(results_list, key=lambda res:res.sem_sim_score, reverse=True)

def output_results(results_list, output_filename):
    """
    Prints the given list of :class:`~wntest.SemanticSimilarityResult` objects to a CSV file

    Given a list of :class:`~wntest.SemanticSimilarityResult` objects and a .csv filename, writes the values of the result objects to specified file.

    Args:
        results_list (list): The list of :class:`~wntest.SemanticSimilarityResult` objects to be printed to the CSV file
        output_filename (str): The name of the CSV file to be written to
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

    Given a list of :class:`~SemanticSimilarityResult` objects and a threshold value, filters the list removing result objects with semantic similarity scores less than the threshold. Returns the filtered list.

    Args:
        results_list (list): The list of :class:`~SemanticSimilarityResult` objects to be filtered
        threshold (number): The semantic similarity score threshold at which results with a score lower than this threshold will be removed from C{results_list}

    Returns:
        list: The filtered list of C{SemanticSimilarityResult} objects
    """
    return [res for res in results_list if res.sem_sim_score >= threshold]


class SemanticSimilarityResult:
    """ This class is used to package results from semantic similarity tests. Each object of this class holds the result of a single unknown to known word mapping.

    This class stores a variety of information for analysis purposes, including the synsets with the highest similarity score, their definitions, the semantic similarity score, and most importantly the known word that the unknown word will map to. This class is to be used for testing and analysis purposes to see how the semantic similarity measure may be improved. The only pieces of information important to the final result of the LILI interpreter is the known word that the unknown word is mapped to.

    Attributes:
        unknown (str): The unknown word that has been mapped to a known word
        known (str): The known word that has been mapped to
        unknown_synset (wn.Synset): The synset of the unknown word
        known_synset (wn.Synset): The synset of the known word that has been mapped to
        unknown_defintion (str): The definition of unknown_synset
        known_definition (str): The definition of known_synset
        sem_sim_score (number): The semantic similarity score between unknown_synset and known_synset
    """
    def __init__(self, unknown, known, unknown_synset, known_synset, unknown_definition, known_definition, sem_sim_score):
        """ Constructor for the :class:`wntest.SemanticSimilarityResult` class. See the class's documentation for details on each parameter
        """
        self.unknown = unknown
        self.known = known
        self.unknown_synset = unknown_synset
        self.known_synset = known_synset
        self.unknown_definition = unknown_definition
        self.known_definition = known_definition
        self.sem_sim_score = sem_sim_score
