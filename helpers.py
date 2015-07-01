from nltk.corpus import wordnet as wn

def displaySynsets(verb):
    for synset in wn.synsets(verb):
        if 'v' in synset.name() and verb in synset.name():
            print '%s: %s' % (synset.name(), synset.definition())
