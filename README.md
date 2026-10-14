# Simple Chatbot (Rai)

A rule-based chatbot in Python. It uses regular expressions to work out what you mean and replies with a randomly chosen response. No machine learning, no external libraries: the bot itself only uses the standard library.

## Features

- **Small talk:** greetings, "how are you" (and it reacts to your answer), "what's your name"
- **Remembers your name** between runs ("my name is Sam"), and forgets it on request ("forget my name")
- **Calculator:** "calculate 12 * (3 + 4)", "what is 100 divided by 8", "2 ^ 10". It parses the math safely and never uses `eval()`
- **Time and date**, jokes, coin flips and dice rolls
- **Tolerates typos** in keywords ("whats the wether" still gets a weather reply)
- **Notices when it's confused** and suggests typing "help" after a few misses in a row
- Never repeats the same reply twice in a row
- Exits on "bye", "exit", "quit", "goodbye", "pause" or "later", and handles Ctrl+C and Ctrl+Z cleanly
- Optional conversation log with `--log`

## Run it

Python 3.10 or newer.

```
python main.py
```

Options:

```
python main.py --no-memory      # don't save or load your name
python main.py --log chat.log   # also write the conversation to a file
```

Example chat:

```
Bot: Hi! I'm Rai. Type 'exit' to end our chat.
You: hello
Bot: Hello! How can I help you today?
You: my name is raiyan
Bot: Nice to meet you, Raiyan!
You: how are you
Bot: I'm functioning within normal parameters! How about you?
You: good
Bot: That's great to hear!
You: calculate 12 * (3 + 4)
Bot: 12 * (3 + 4) = 84
You: what is 100 divided by 8
Bot: 100 / 8 = 12.5
You: whats the wether
Bot: It's always 72 degrees inside this server rack.
You: flip a coin
Bot: It's heads!
You: bye
Bot: Goodbye, Raiyan! Have a great day.
```

## How it works

```
main.py              command-line entry point (--no-memory, --log)
chatbot/
    bot.py           the RuleBot class: rules, matching, memory, chat loop
    responses.py     every reply the bot can give (edit this to change its personality)
    calculator.py    the safe calculator
tests/               33 unit tests
```

**Rules.** Each rule pairs a regex with a response. The bot checks them from top to bottom and the first match wins, so specific rules (like "what's your name") come before general ones (like greetings). A response is either a list of replies to choose from, or a method that builds the reply from the regex match, which is how name memory and the clock work.

```python
(r"\bjokes?\b", R.JOKES),
(r"\bmy name is (\w+)", self._remember_name),
```

**Whole-word matching.** Patterns use `\b` word boundaries. Without them, `hi` also matches inside "this" and "which".

**Typo fixing.** Before matching, the bot corrects near-misses of a handful of keywords with `difflib`. The cutoff is deliberately strict, and a test checks that real words like "whether" aren't rewritten into "weather".

**Short-term memory.** After "how are you", the bot remembers it is waiting for an answer, so "good" and "not good" get different replies. Anything else clears that state.

**Safe calculator.** Math is parsed with Python's `ast` module and only numbers and basic operators are allowed. Division by zero, huge exponents and anything that isn't math get a friendly error instead of a crash.

**Testable by design.** The clock and the random generator can be replaced, and the chat loop takes its input and output functions as arguments. That is how the tests get predictable results.

## Add your own rule

1. Add a list of replies to `chatbot/responses.py`:

   ```python
   COFFEE = ["Coffee is just a bean-powered debugger.", "I run on electricity, but I respect the hustle."]
   ```

2. Add one line to `raw_rules` in `chatbot/bot.py`, above the greeting rule:

   ```python
   (r"\bcoffee\b", R.COFFEE),
   ```

## Tests

```
pip install -r requirements-dev.txt
pytest
```

The tests cover matching, typos, name memory (including corrupt files), the calculator and its safety limits, the mood follow-up, exit handling and the chat loop.

## Limitations

- It only understands what its patterns cover. Anything else gets a generic reply.
- Typo fixing only covers a few keywords, not whole sentences.
- It is English only and has no real understanding of meaning.
