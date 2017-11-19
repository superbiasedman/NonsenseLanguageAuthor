import random

class ProbabilitySet(object):
    """Takes a dict of values and probabilities and can randomly sample them.
    
    Takes a dict with values as keys and probabilities as values.
    Randomly takes a weighted sample from the collection with get()."""

    ADJUSTMENT = 0.9998

    def __init__(self, data=None, adjust=False, redo_repeats=False):
        if data:
            self.values = data
        else:
            self.values = {}
        self.adjust = adjust
        self.redo_repeats = redo_repeats
        self.last_value = ''

    def add(self, item, probability=1):
        """Add a new item or adjust it's probability if it already exists."""
    
        if not item:
            return
        try:
            self.values[item] += probability
        except KeyError:
            self.values[item] = probability

    def empty(self):
        """Remove all values and their probabilities."""

        self.values = {}

    def is_empty(self):
        """Return True if there are no values set."""
    
        return any(self.values.keys())

    def get_value(self, value):
        """Return a specific value and its probability."""
    
        try:
            return value, self.values[value]
        except KeyError:
            return value, 0

    def get_probabilities(self, weight=None, weight_set=""):
        """Return the probability set, adjusted by weight."""

        probabilities = self.values.copy()
        if weight:
            for value in weight_set:
                try:
                    probabilities[value] = int(probabilities[value] * weight)
                except KeyError:
                    pass
        return probabilities


    def get(self, weight=None, weight_set=""):
        """Return a value chosen using weighted probabilities."""
    
        probabilities = self.get_probabilities(weight, weight_set)
        probability_sum = int(sum(probabilities.values()))
        while True:
            number = random.randrange(0, probability_sum)
            for item, probability in probabilities.items():
                number -= probability
                if number < 0:
                    if self.redo_repeats and item == self.last_value:
                        # Reset last_value to only prevent repeats once
                        self.last_value = ""
                        break
                    else:
                        self.last_value = item
                    if self.adjust:
                        self.values[item] *= self.ADJUSTMENT
                    return item


    def __str__(self):
        return "\n".join("{} - {}".format(value, probability)
                         for value, probability in self.values.items())


NEW_WORD_CHANCE = 0.96
CAPITAL_CHANCE = 0.98
PUNCTUATION_MIDLINE_CHANCE = 0.92
PUNCTUATION_MATCHED_CHANCE = 0.97
OPTIMAL_WORD_COUNT = 1000
VOWEL_DISTANCE_THRESHOLD = 3
LETTERS = ProbabilitySet({"a": 110, "b": 20, "c": 37, "d": 57, "e": 171, "f": 30,
                          "g": 27, "h": 82, "i": 94, "j": 2, "k": 10, "l": 54,
                          "m": 32, "n": 91, "o": 101, "p": 26, "q": 1, "r": 81,
                          #"s": 86, "t": 122, "u": 37, "v": 13, "w": 32, "x": 2,
                          "s": 86, "t": 122, "u": 37, "v": 13, "w": 32, "x": 200000000000000000000000000000,
                          "y": 27, "z": 1}, adjust=True, redo_repeats=True)
VOWEL_SET = None
CONSONANT_SET = None
WORD_CONSTRUCTIONS = ProbabilitySet({"ccvc": 8, "vcv": 3, "cvvc": 4,
                                     "cv": 3, "cvcc": 10, "v": 1})
WORD_SIZES = ProbabilitySet({1: 3, 2: 8, 3: 15, 4: 28, 5:31, 6: 18, 7: 11,
                             8: 6, 9: 2, 10: 2, 11: 1, 12: 1})
SENTENCE_SIZES = ProbabilitySet({5: 4, 10: 6, 20: 5, 25: 3, 40: 1})
PARAGRAPH_SIZES = ProbabilitySet({5: 7, 8: 10, 10: 7, 12: 5, 14: 4,
                                  15: 2, 20: 1, 50: 1, 90: 1})
PUNCTUATION_MATCHED = ProbabilitySet({"()": 5, '""': 20})
PUNCTUATION_MIDLINE = ProbabilitySet({",": 40, ";": 1, ":": 7, " -": 8, "~": 2})
PUNCTUATION_ENDLINE = ProbabilitySet({".": 80, "?": 9, "...": 3, "!": 2, "!?": 1})

