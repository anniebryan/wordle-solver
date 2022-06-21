from helper import remaining_words, best_guesses

def run():
  guesses = []
  finished = False

  while len(guesses) < 6 and not finished:
    guess = input("Guess: ")
    result = input("Result: ")
    guesses.append((guess, result))
    rw = remaining_words(guesses)

    if len(rw) == 1:
      finished = True
      print(f"The word must be: {rw[0]}")
    else:
      bg = best_guesses(rw, 5)
      print(f"The word could be any of the following {len(rw)} words: {rw}")
      print(f"The best choices for your next guess are: {bg}")

run()
