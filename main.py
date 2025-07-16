import streamlit as st
from collections import Counter
from typing import List, Tuple
import math

# debug
# WORD_LIST = [
#     "crane", "slate", "slice", "grime", "spike", "pride", "brine", "stone",
#     "plane", "trace", "shine", "flame", "blame", "chore", "grace", "climb",
#     "blitz", "plaza", "sling", "crisp", "brick", "stare", "glare", "fluke",
#     "grain", "prize", "glide", "crank", "drink", "plumb", "stint"
# ]

def load_words_from_file(path: str, length: int) -> List[str]:
    with open(path, 'r') as f:
        return [line.strip().lower() for line in f if len(line.strip()) == length and line.strip().isalpha()]

def feedback(guess: str, target: str) -> str:
    word_length = len(target)
    result = ['B'] * word_length
    target_count = Counter(target)

    for i in range(word_length):
        if guess[i] == target[i]:
            result[i] = 'G'
            target_count[guess[i]] -= 1

    for i in range(word_length):
        if result[i] == 'B' and target_count[guess[i]] > 0:
            result[i] = 'Y'
            target_count[guess[i]] -= 1

    return ''.join(result)

def filter_candidates(candidates: List[str], guess: str, result: str) -> List[str]:
    return [word for word in candidates if feedback(guess, word) == result]

def score_words_by_letter_frequency(candidates: List[str]) -> List[Tuple[str, int]]:
    if not candidates:
        return []

    word_length = len(candidates[0])
    position_freq = [Counter() for _ in range(word_length)]

    for word in candidates:
        for i, ch in enumerate(word):
            position_freq[i][ch] += 1

    scored = []
    for word in candidates:
        score = sum(position_freq[i][ch] for i, ch in enumerate(word))
        scored.append((word, score))

    scored.sort(key=lambda x: -x[1])
    return scored

def score_words_by_entropy(candidates: List[str]) -> List[Tuple[str, float]]:
    if not candidates:
        return []

    word_length = len(candidates[0])
    total = len(candidates)
    position_freq = [Counter() for _ in range(word_length)]

    # Count letter frequencies at each position
    for word in candidates:
        for i, ch in enumerate(word):
            position_freq[i][ch] += 1

    scored = []
    for word in candidates:
        log_prob = 0.0
        for i, ch in enumerate(word):
            freq = position_freq[i][ch]
            if freq == 0:
                continue  # skip impossible letters
            prob = freq / total
            log_prob += math.log2(prob)
        scored.append((word, log_prob))  # Note: higher = more probable (less informative)

    # Sort by most informative (lowest log-prob)
    scored.sort(key=lambda x: x[1])
    return scored

def simulate_game(target: str, word_list: List[str]):
    candidates = word_list.copy()
    history = []
    word_length = len(target)
    turn = 0

    while True:
        turn += 1
        print(len(candidates)) ######### debug line
        # scores = score_words_by_letter_frequency(candidates)
        scores = score_words_by_entropy(candidates)
        if not scores:
            print("No words left to guess. Game failed.")
            break

        guess = scores[0][0]
        fb = feedback(guess, target)
        history.append((turn, guess, fb))
        print(f"Turn {turn}: Guess = {guess.upper()} -> Feedback = {fb}")

        if fb == "G" * word_length:
            print(f"\nSolved in {turn} turns!")
            break

        candidates = filter_candidates(candidates, guess, fb)

    return history

if __name__ == "__main__":
    target = "aardwolves"  # or any length word like "tool", "grains", "abacus"
    word_length = len(target)
    WORD_LIST = load_words_from_file("dictionary.txt", word_length)
    simulate_game(target, WORD_LIST)
