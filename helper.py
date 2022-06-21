from wordfreq import word_frequency

filename = "words.txt"
words = [w.strip() for w in open(filename).readlines()]


def process_guesses(known_letter_counts, known_green_letters, restricted_letters, restricted_letter_counts, restricted_letter_positions, w=words):

  for letter, count in known_letter_counts.items():
    w = contains_n_or_more_of_letter(letter, count, w)

  for i, letter in known_green_letters.items():
    w = contains_letter_at(letter, i, w)

  for letter in restricted_letters:
    w = doesnt_contain_letter(letter, w)

  for letter, count in restricted_letter_counts.items():
    w = contains_exactly_n_of_letter(letter, count, w)

  for letter, positions in restricted_letter_positions.items():
    for position in positions:
      w = doesnt_contain_letter_at(letter, position, w)

  return list(w)


def contains_n_or_more_of_letter(letter, n, w):
  fn = lambda word: len([ch for ch in word if ch == letter]) >= n
  return filter(fn, w)


def contains_exactly_n_of_letter(letter, n, w):
  fn = lambda word: len([ch for ch in word if ch == letter]) == n
  return filter(fn, w)


def contains_letter_at(letter, position, w):
  fn = lambda word: word[position] == letter
  return filter(fn, w)


def doesnt_contain_letter_at(letter, position, w):
  fn = lambda word: word[position] != letter
  return filter(fn, w)


def doesnt_contain_letter(letter, w):
  fn = lambda word: letter not in word
  return filter(fn, w)


def add_to_dict(key, val, d):
  if key in d:
    d[key] += val
  else:
    d[key] = val


def get_most_common_letters(remaining_words, known_letter_counts):
  counts = {}

  for word in remaining_words:
    word_counts = {}

    for ch in word:
      add_to_dict(ch, 1, word_counts)

    for ch in set(word):
      if ch in known_letter_counts:
        c = word_counts[ch] - known_letter_counts[ch]
        add_to_dict(ch, c, counts)

      else:
        c = word_counts[ch]
        add_to_dict(ch, c, counts)
        
  return [(c, counts[c]) for c in sorted(counts, key=counts.get) if counts[c] > 0][::-1]


def get_known_letter_counts(guesses):
  known_letter_counts = {}

  for guess in guesses:
    known_letters_from_guess = {}

    for i, ch in enumerate(guess[0]):
      if guess[1][i] == 'g' or guess[1][i] == 'y':
        add_to_dict(ch, 1, known_letters_from_guess)
    all_keys = set(known_letter_counts.keys()).union(
        set(known_letters_from_guess.keys()))

    for key in all_keys:
      known_letter_counts[key] = max(
          known_letter_counts[key] if key in known_letter_counts else 0,
        known_letters_from_guess[key] if key in known_letters_from_guess else 0
      )

  return known_letter_counts


def get_known_green_letters(guesses):
  known_green_letters = {}

  for guess in guesses:
    for i, ch in enumerate(guess[0]):
      if guess[1][i] == 'g':
        known_green_letters[i] = ch

  return known_green_letters


def get_restrictions(guesses):
  restricted_letters = set()
  restricted_letter_counts = {}
  restricted_letter_positions = {}

  for guess in guesses:
    occurrences = {} # ex. {'a': {0: 'b', 2: 'y'}}
    for i, ch in enumerate(guess[0]):
      if ch in occurrences:
        occurrences[ch][i] = guess[1][i]
      else:
        occurrences[ch] = {i: guess[1][i]}
    for ch in occurrences:
      type_of_ch_occurrences = set()
      for i, result in occurrences[ch].items():
        type_of_ch_occurrences.add(result)
      if len(type_of_ch_occurrences) == 1 and list(type_of_ch_occurrences)[0] == 'b':
        restricted_letters.add(ch)
      elif 'b' in type_of_ch_occurrences:
        num_ch = sum([1 for result in occurrences[ch].values() if result == 'g' or result == 'y'])
        restricted_letter_counts[ch] = num_ch
        ixs = {i for i, result in occurrences[ch].items() if result == 'b' or result == 'y'}
        if ch in restricted_letter_positions:
          for i in ixs:
            restricted_letter_positions[ch].add(i)
        else:
          restricted_letter_positions[ch] = ixs
      else:
        ixs = {i for i, result in occurrences[ch].items() if result == 'y'}
        if ch in restricted_letter_positions:
          for i in ixs:
            restricted_letter_positions[ch].add(i)
        else:
          restricted_letter_positions[ch] = ixs
  return restricted_letters, restricted_letter_counts, restricted_letter_positions


def remaining_words(guesses, w=words):
  known_letter_counts = get_known_letter_counts(guesses)
  known_green_letters = get_known_green_letters(guesses)
  restricted_letters, restricted_letter_counts, restricted_letter_positions = get_restrictions(guesses)
  return process_guesses(known_letter_counts, known_green_letters, restricted_letters, restricted_letter_counts, restricted_letter_positions, w)


def best_guesses(rw, num=3):
  fs = normalized_frequencies(rw)
  ew = expected_words_remaining_after_guess(rw, fs)
  num = min(num, len(ew))
  sorted_ew = sorted(ew.keys(), key=ew.get)
  ret_list = []
  for i in range(num):
    ret_list.append(sorted_ew[i])
  return ret_list

def initial_frequencies(rw):
  fs = {}
  for w in rw:
    fs[w] = word_frequency(w, 'en')
  return fs

def normalized_frequencies(rw):
  fs = initial_frequencies(rw)
  sum_fs = sum(fs.values())
  new_fs = {}
  for w in fs:
    new_fs[w] = fs[w]/sum_fs
  return new_fs

def expected_words_remaining_after_guess(rw, fs):
  ew = {}
  for guess in rw:
    total = 0
    for answer in rw:
      p = fs[answer]
      r = words_remaining_after_guess(guess, answer, rw)
      total += r*p
    ew[guess] = total
  return ew

def words_remaining_after_guess(guess, answer, rw):
  result = get_result(guess, answer)
  guesses = [(guess, result)]
  new_rw = remaining_words(guesses, rw)
  return len(new_rw)

def get_result(guess, answer):
  s = {}  # 5-character string of 'b','y','g'
  for i in range(5):
    if guess[i] == answer[i]:
      s[i] = "g"
    elif guess[i] not in answer:
      s[i] = "b"
  if len(s) == 5:

    return f"{s[0]}{s[1]}{s[2]}{s[3]}{s[4]}"

  reduced_guess = {i: ch for i, ch in enumerate(guess) if i not in s}
  reduced_answer = [ch for i, ch in enumerate(answer) if i not in s or s[i] != "g"]

  i = min(reduced_guess)
  for i in range(5):
    if i not in s:
      ch = reduced_guess[i]
      if ch in reduced_answer:
        s[i] = "y"
        reduced_answer.remove(ch)
      else:
        s[i] = "b"
  return f"{s[0]}{s[1]}{s[2]}{s[3]}{s[4]}"

