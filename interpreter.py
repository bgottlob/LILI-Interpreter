import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import verbnet as vn

# Get input from user - will be replaced by data from speech recognizer
# sent = raw_input("Enter a sentence:\n")

sent = "Lily, rotate right"

# Tokenize input and tag parts of speech
taggedSent = nltk.pos_tag(nltk.word_tokenize(sent))
print taggedSent

# Extract the verb of the sentence
wordNum = 0
foundVerb = False
verb = ''
while wordNum < len(taggedSent) and (not foundVerb):
    if taggedSent[wordNum][1] == "VB":
        foundVerb = True
        verb = taggedSent[wordNum][0]
    wordNum += 1

print "The verb is " + verb

if not foundVerb:
    verb = raw_input("Verb not found, enter one yourself:\n")
    foundVerb = True
if foundVerb:
    knownVerbs = ["turn", "follow", "stop"]
    knownSynsets = ["turn.v.01", "follow.v.01", "stop.v.01"]
    semanticSim = []
    for kSs in knownSynsets:
        uVerbSynset = wn.synset(verb + ".v.01")
        print uVerbSynset.definition()
        kVerbSynset = wn.synset(kSs)
        print kVerbSynset.definition()
        semanticSim.append(uVerbSynset.path_similarity(kVerbSynset))

    print "semanticSim"
    print semanticSim
