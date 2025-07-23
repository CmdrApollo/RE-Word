import random
from collections import Counter

all_words = open('words.txt', 'r').read().splitlines()

class Bot:
    def __init__(self, starting_guess, engine):
        self.starting_guess = starting_guess
        self.engine = engine

        self.guesses = [None for _ in range(6)]
        self.previous_guess = None

        self.filtered_words = all_words

    def evaluate(self) -> str:        
        if self.previous_guess:
            guess_word, feedback = self.previous_guess
            new_filtered = []

            for word in self.filtered_words:
                match = True
                target_counts = Counter(word)

                for i in range(len(guess_word)):
                    g_char = guess_word[i]
                    if feedback[i] == 'G':
                        if word[i] != g_char:
                            match = False
                            break
                        target_counts[g_char] -= 1

                if match:
                    for i in range(len(guess_word)):
                        g_char = guess_word[i]
                        if feedback[i] == 'Y':
                            if word[i] == g_char or target_counts[g_char] == 0:
                                match = False
                                break
                            target_counts[g_char] -= 1
                        elif feedback[i] == '_':
                            if target_counts[g_char] > 0:
                                match = False
                                break

                if match:
                    new_filtered.append(word)

            self.filtered_words = new_filtered
        return random.choice(self.filtered_words) if self.filtered_words else None

    def guess(self, i: int, guess: str):
        self.guesses[i] = guess, self.engine.sequence(guess, self.engine.target_word)
        self.previous_guess = guess, self.engine.sequence(guess, self.engine.target_word)

    def solve(self):
        for i in range(len(self.guesses)):
            if i == 0: guess = self.starting_guess
            else: guess = self.evaluate()
        
            if guess is None:
                break

            self.guess(i, guess)

            if self.previous_guess[1] == "GGGGG":
                break
        
        while self.guesses[-1] is None:
            self.guesses.pop()