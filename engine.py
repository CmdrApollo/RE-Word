from collections import Counter

class Wordle:
    def __init__(self, target_word = "start"):
        self.target_word = target_word

    def sequence(self, word: str, target: str) -> str:
        seq = ['_'] * len(word)
        target_counts = Counter(target)

        # First pass: mark greens
        for i, char in enumerate(word):
            if target[i] == char:
                seq[i] = 'G'
                target_counts[char] -= 1

        # Second pass: mark yellows
        for i, char in enumerate(word):
            if seq[i] == '_' and target_counts[char] > 0:
                seq[i] = 'Y'
                target_counts[char] -= 1

        return ''.join(seq)