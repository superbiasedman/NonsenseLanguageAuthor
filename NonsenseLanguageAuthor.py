# Try code for assessing patterns from input text
#    > Update the punctuation chances based on the source?

import random
import sys

from string import letters, digits

import probabilities

class NovelCreator(object):

    MATCHED_PUNCTUATION = '<>[]{}()""'
    MIDLINE_PUNCTUATION = "$%^&*_+-=;:'@#~/\\|"
    ENDING_PUNCTUATION = '!?.'
    VOWELS = "aeiou"

    def __init__(self, size, source_text=""):
        self.size = size + int(random.randrange(0, size/100))
        self.words = []
        self.word_count = 0
        self.last_word = ""
        if source_text:
            self.parse_text(source_text)
            self.set_defaults(False)
        else:
            self.set_defaults(True)


    def set_defaults(self, all_defaults):
        """Sets default values for the object."""
        
        if all_defaults:
            # Set every value from the defaults.
            self.letters = probabilities.LETTERS
            self.word_constructions = probabilities.WORD_CONSTRUCTIONS
            self.word_sizes = probabilities.WORD_SIZES
            self.sentence_sizes = probabilities.SENTENCE_SIZES
            self.paragraph_sizes = probabilities.PARAGRAPH_SIZES
            self.punctuation_midline = probabilities.PUNCTUATION_MIDLINE
            self.punctuation_endline = probabilities.PUNCTUATION_ENDLINE
            self.punctuation_matched = probabilities.PUNCTUATION_MATCHED

        # Common values even when parsing imported text
        self.new_word_chance = probabilities.NEW_WORD_CHANCE
        self.capital_chance = probabilities.CAPITAL_CHANCE
        self.punctuation_midline_chance = probabilities.PUNCTUATION_MIDLINE_CHANCE
        self.punctuation_matched_chance = probabilities.PUNCTUATION_MATCHED_CHANCE
        self.optimal_word_count = probabilities.OPTIMAL_WORD_COUNT
        self.vowel_distance_threshold = probabilities.VOWEL_DISTANCE_THRESHOLD


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
        
        size = self.paragraph_sizes.get()
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
        
        size = self.sentence_sizes.get()
        size += int(random.randrange(int(size * 0.8), int(size * 1.5)))

        sentence = ""
        opener = closer = None
        match_chance = self.punctuation_matched_chance
        
        for i in range(size):
            word = self.get_word()
            if self.last_word == word:
                # Retry to avoid repeats.
                word = self.get_word()
            self.last_word = word
        
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
                        match_chance = self.punctuation_matched_chance
                    else:
                        opener, closer = self.punctuation_matched.get()
                    continue
                elif closer:
                    # Make it increasingly likely to roll a closer
                    match_chance *= 0.8
                if random.random() > self.punctuation_midline_chance:
                    sentence += self.punctuation_midline.get()

        end_of_line = self.punctuation_endline.get()
        if closer:
            sentence = sentence.strip() + closer + end_of_line
        else:
            sentence = sentence.strip() + end_of_line
        return sentence, size


    def get_word(self):
        """Return a string word."""

        # Get a unique word anyway
        if not self.word_count or random.random() > self.new_word_chance:
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

        return self.letters.get(vowel_need, self.VOWELS)


    def create_word(self):
        """Return a newly generated string word."""

        template = self.word_constructions.get()
        word = ""
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

        if random.random() > self.capital_chance:
            word = word.capitalize()
        self.words.append(word)
        self.word_count += 1
        return word
    
    def parse_text(self, source):
        """Read the file at source to get ProbabilitySets"""
        
        self.letters = probabilities.ProbabilitySet(adjust=True)
        self.punctuation_endline = probabilities.ProbabilitySet()
        self.punctuation_midline = probabilities.ProbabilitySet()
        self.punctuation_matched = probabilities.ProbabilitySet()
        self.word_constructions = probabilities.ProbabilitySet(redo_repeats=True)
        self.word_sizes = probabilities.ProbabilitySet(redo_repeats=True)
        self.sentence_sizes = probabilities.ProbabilitySet(redo_repeats=True)
        self.paragraph_sizes = probabilities.ProbabilitySet(redo_repeats=True)
        
        line_count = 0
        word_count = 0
        with open(source) as f:
            for line in f:
                if line_count and not line.strip() or line.startswith("\t"):
                    self.paragraph_sizes.add(line_count)
                    line_count = 0
                
                words = line.split()
                for word in words:
                    if not word:
                        continue
                    self.word_sizes.add(len(word))
                    construction = ""
                    word_count += 1
                    for c in word.lower():
                        if word_count and c in self.ENDING_PUNCTUATION:
                            line_count += 1
                            self.sentence_sizes.add(word_count)
                            word_count = 0
                        self.parse_character(c)
                        if c in self.VOWELS:
                            construction += "v"
                        elif c in letters:
                            construction += "c"
                    self.word_constructions.add(construction)
        if not self.paragraph_sizes.is_empty():
            # Liable to not parse in certain sources.
            self.paragraph_sizes = probabilities.PARAGRAPH_SIZES

        
        for probability_set in (self.letters, self.punctuation_endline, self.punctuation_matched,
                                self.punctuation_midline, self.word_constructions,
                                self.word_sizes, self.sentence_sizes):
            print(probability_set)
            print("="*78)

    def parse_character(self, character):
        """Take a character and add it to the relevant ProbabilitySet."""
        
        if character in letters:
            self.letters.add(character)
        elif character in self.MATCHED_PUNCTUATION:
            index = self.MATCHED_PUNCTUATION.find(character)
            if index % 2 != 0:
                # Ignore odd indices, as they're the closing mark.
                return
            # Take the character and it's closing value.
            key = self.MATCHED_PUNCTUATION[index:index + 2]
            self.punctuation_matched.add(key)
        elif character in self.ENDING_PUNCTUATION:
            self.punctuation_endline.add(character)
        elif character in self.MIDLINE_PUNCTUATION:
            self.punctuation_midline.add(character)
            

def main(output):
    global novel
    novel = NovelCreator(50000, "C:\Users\Gary\Documents\NaNoGenMo\input.txt")
    novel.write(output)
    print(novel.letters)


if __name__ == "__main__":
    #main(sys.argv[1])
    main("output.txt")
