# Try code for assessing patterns from input text
#    > Update the punctuation chances based on the source?

import random
import sys

from string import letters, digits

class ProbabilitySet(object):
    """Takes a dict of values and probabilities and can randomly sample them.
    
    Takes a dict with values as keys and probabilities as values.
    Randomly takes a weighted sample from the collection with get()."""

    ADJUSTMENT = 0.9998

    def __init__(self, data={}, adjust=False, redo_repeats=False):
        self.values = data
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


class NovelCreator(object):

    NEW_WORD_CHANCE = 0.96
    CAPITAL_CHANCE = 0.98
    PUNCTUATION_MIDLINE_CHANCE = 0.92
    PUNCTUATION_MATCHED_CHANCE = 0.97
    OPTIMAL_WORD_COUNT = 1000
    VOWEL_DISTANCE_THRESHOLD = 3
    LETTERS = ProbabilitySet({"a": 110, "b": 20, "c": 37, "d": 57, "e": 171, "f": 30,
                              "g": 27, "h": 82, "i": 94, "j": 2, "k": 10, "l": 54,
                              "m": 32, "n": 91, "o": 101, "p": 26, "q": 1, "r": 81,
                              "s": 86, "t": 122, "u": 37, "v": 13, "w": 32, "x": 2,
                              "y": 27, "z": 1}, adjust=True, redo_repeats=True)
    MATCHED_PUNCTUATION = '<>[]{}()""'
    MIDLINE_PUNCTUATION = '`¬¦£$%^&*_+-=€;:\'@#~/\\|'
    ENDING_PUNCTUATION = '!?.…'
    VOWELS = "aeiou"
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
    LETTER_COUNT = 0
    SENTENCE_TYPE_COUNT = 0
    PARAGRAPH_TYPE_COUNT = 0
    PUNCTUATION_MIDLINE_COUNT = 0
    PUNCTUATION_ENDLINE_COUNT = 0

    def __init__(self, size, source_text=""):
        self.size = size + int(random.randrange(0, size/100))
        self.words = []
        self.word_count = self.OPTIMAL_WORD_COUNT
        if source_text:
            self.parse_text(source_text)


    def write(self, filepath):
        """Write a novel at `filepath`."""
    
        with open(filepath, 'w') as f:
            written = 0
            while written < self.size:
                paragraph, length = self.get_paragraph()
                f.write(paragraph)
                written += length

    def get_paragraph(self):
        """Return a paragraph of text and its wordcount."""
        
        size = self.PARAGRAPH_SIZES.get()
        size += int(random.randrange(int(size * 0.8), int(size * 1.2)))
        
        lines = []
        paragraph_length = 0
        while paragraph_length < size:
            sentence, length = self.get_sentence()
            lines.append(sentence)
            paragraph_length += length

        paragraph = "\t" + " ".join(lines) + "\n\n"
        return paragraph, paragraph_length


    def get_sentence(self):
        """Return a sentence of text and its wordcount."""
        
        size = self.SENTENCE_SIZES.get()
        size += int(random.randrange(int(size * 0.8), int(size * 1.5)))

        sentence = ""
        opener = closer = None
        match_chance = self.PUNCTUATION_MATCHED_CHANCE
        
        for i in range(size):
            if i == 0:
                sentence += self.get_word().capitalize()
            elif opener:
                sentence += " " + opener + self.get_word()
                opener = None
            else:
                sentence += " " + self.get_word()
                
            if i != 0 and i != (size - 1):
                if random.random() > match_chance:
                    if closer:
                        sentence += closer
                        closer = None
                        match_chance = self.PUNCTUATION_MATCHED_CHANCE
                    else:
                        opener, closer = self.PUNCTUATION_MATCHED.get()
                    continue
                elif closer:
                    # Make it increasingly likely to roll a closer
                    match_chance *= 0.8
                if random.random() > self.PUNCTUATION_MIDLINE_CHANCE:
                    sentence += self.PUNCTUATION_MIDLINE.get()

        end_of_line = self.PUNCTUATION_ENDLINE.get()
        if closer:
            sentence = sentence.strip() + closer + end_of_line
        else:
            sentence = sentence.strip() + end_of_line
        return sentence, size


    def get_word(self):
        """Return a string word."""

        # Get a unique word anyway
        if random.random() > self.NEW_WORD_CHANCE:
            self.word_count += 1
            return self.create_word() 
        else:
            word_choice = random.randrange(0, self.word_count)
            try:
                return self.words[word_choice]
            except IndexError:
                return self.create_word()


    def get_letter(self, vowel_need):
        """Return a letter character."""

        return self.LETTERS.get(vowel_need, "aeiou")


    def create_word(self):
        """Return a newly generated string word."""
        
        for c in template:
            if c == "v":
                letter = self.get_letter(100)
            else:
                letter = self.get_letter(0)
            word += letter

        while not any(letter in self.VOWELS for letter in word):
            length = len(word)
            if length == 1:
                index = 0
            elif length == 2:
                index = random.randrange(0, 2)
            else:
                a = len(word) / 2
                index = a + random.randrange(-a / 2, a / 2)
            word = word[:index] + self.get_letter(100) + word[index + 1:]

        if random.random() > self.CAPITAL_CHANCE:
            word = word.capitalize()
        self.words.append(word)
        return word
    
    def parse_text(self, source):
        """Read the file at source to get ProbabilitySets"""
        
        self.LETTERS.empty()
        self.PUNCTUATION_ENDLINE.empty()
        self.PUNCTUATION_MIDLINE.empty()
        self.PUNCTUATION_MATCHED.empty()
        
        self.WORD_CONSTRUCTIONS.empty()
        self.WORD_SIZES.empty()
        self.SENTENCE_SIZES.empty()
        # May not be readable
        new_paragraphs = ProbabilitySet()
        
        line_count = 0
        word_count = 0
        with open(source) as f:
            for line in f:
                if line_count and not line.strip() or line.startswith("\t"):
                    new_paragraphs.add(line_count)
                    line_count = 0
                
                words = line.split()
                for word in words:
                    if not word:
                        continue
                    self.WORD_SIZES.add(len(word))
                    construction = ""
                    word_count += 1
                    for c in word.lower():
                        if word_count and c in self.ENDING_PUNCTUATION:
                            line_count += 1
                            self.SENTENCE_SIZES.add(word_count)
                            word_count = 0
                        self.parse_character(c)
                        if c in self.VOWELS:
                            construction += "v"
                        elif c in letters:
                            construction += "c"
                    self.WORD_CONSTRUCTIONS.add(construction)
        if not new_paragraphs.is_empty():
            self.PARAGRAPH_SIZES = new_paragraphs

        for s in (self.LETTERS, self.PUNCTUATION_ENDLINE, self.PUNCTUATION_MATCHED,
                  self.PUNCTUATION_MIDLINE, self.WORD_CONSTRUCTIONS,
                  self.WORD_SIZES, self.SENTENCE_SIZES, new_paragraphs):
            print s
            print "="*78
        

    def parse_character(self, character):
        """Take a character and add it to the relevant ProbabilitySet."""
        
        if character in letters:
            self.LETTERS.add(character)
        elif character in self.MATCHED_PUNCTUATION:
            index = self.MATCHED_PUNCTUATION.find(character)
            if index % 2 != 0:
                # Ignore odds, as they're the closing mark.
                return
            # Take the character and it's closing value.
            key = self.MATCHED_PUNCTUATION[index:index + 2]
            self.PUNCTUATION_MATCHED.add(key)
        elif character in self.ENDING_PUNCTUATION:
            self.PUNCTUATION_ENDLINE.add(character)
        elif character in self.MIDLINE_PUNCTUATION:
            self.PUNCTUATION_MIDLINE.add(character)
            

def main(output):
    global novel
    novel = NovelCreator(50000, "C:\Users\Gary\Documents\NaNoGenMo\input.txt")
    novel.write(output)
    print(novel.LETTERS)


if __name__ == "__main__":
    #main(sys.argv[1])
    main("output.txt")
