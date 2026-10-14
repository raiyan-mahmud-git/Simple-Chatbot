"""Rai: a rule-based chatbot that understands messages with regular expressions."""

from __future__ import annotations

import difflib
import json
import random
import re
from datetime import datetime
from pathlib import Path

from . import responses as R
from .calculator import CalculatorError, calculate, format_number

EXIT_COMMANDS = {"quit", "pause", "exit", "goodbye", "bye", "later"}
MAX_EXIT_WORDS = 3  # only short messages count as goodbyes
MAX_NAME_LENGTH = 30
STUCK_AFTER = 3  # confusing messages in a row before suggesting 'help'


# words are never rewritten by accident.
KEYWORDS = ["weather", "thanks", "thank", "hello", "goodbye", "joke", "calculate", "support"]
MIN_TYPO_LENGTH = 5
TYPO_CUTOFF = 0.88 

MATH_WORDS = [
    ("to the power of", "^"),
    ("multiplied by", "*"),
    ("divided by", "/"),
    ("plus", "+"),
    ("minus", "-"),
    ("times", "*"),
]
MATH_PATTERN = re.compile(r"^(?:calculate|compute|solve|what(?:'s| is)|whats)?\s*([\d\s.+\-*/()^%]+)$")

_WORD = re.compile(r"[a-z']+")


class RuleBot:
    def __init__(self, memory_file=None, clock=datetime.now, rng=None):
        """
        memory_file: JSON file used to remember the user's name between runs.
                     None means nothing is saved.
        clock, rng:  can be replaced in tests to get predictable results.
        """
        self.name = "Rai"
        self.user_name = None
        self._memory_path = Path(memory_file) if memory_file else None
        self._clock = clock
        self._rng = rng or random.Random()
        self._last_reply = None
        self._pending = None 
        self._fallback_streak = 0
        self._load_memory()

        
        
        raw_rules = [
            (r"\bforget (?:me|my name)\b", self._forget_name),
            (r"\bmy name is (\w+)", self._remember_name),
            (r"\bwhat(?:'s| is) my name\b|\bwho am i\b", self._recall_name),
            (r"\byour name\b|\bwho are you\b", R.NAME_RESPONSES),
            (r"\bwho (?:made|created|built|wrote) you\b", R.ABOUT_ME),
            (r"\bhow are you\b|\bhow'?s it going\b", self._how_are_you),
            (r"\bwhat time is it\b|\bwhat(?:'s| is) the time\b|\bcurrent time\b", self._tell_time),
            (r"\bwhat(?:'s| is) (?:the |today'?s )?date\b|\bwhat day is it\b|\bwhat(?:'s| is) today\b", self._tell_date),
            (r"\bflip a coin\b|\bcoin flip\b|\btoss a coin\b", self._flip_coin),
            (r"\broll (?:a |an )?(?:die|dice)\b", self._roll_die),
            (r"\bweather\b", R.WEATHER),
            (r"\bjokes?\b", R.JOKES),
            (r"\b(?:thanks|thank you)\b", R.THANKS),
            (r"\b(?:good|great|nice|awesome) (?:bot|job)\b|\byou(?:'re| are) (?:smart|great|awesome|funny)\b", R.COMPLIMENTS),
            (r"\b(?:help|support)\b|\bwhat can you do\b", R.HELP),
            (r"\b(?:hi|hello|hey)\b", R.GREETINGS),
        ]
        # Compile once
        self.rules = [(re.compile(pattern), response) for pattern, response in raw_rules]

    #  memory
    def _load_memory(self):
        if not self._memory_path:
            return
        try:
            data = json.loads(self._memory_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return  
        if isinstance(data, dict) and isinstance(data.get("user_name"), str):
            self.user_name = data["user_name"]

    def _save_memory(self):
        if not self._memory_path:
            return
        try:
            self._memory_path.write_text(json.dumps({"user_name": self.user_name}), encoding="utf-8")
        except OSError:
            pass  

    # replies built from the match
    def _remember_name(self, match):
        self.user_name = match.group(1)[:MAX_NAME_LENGTH].capitalize()
        self._save_memory()
        return f"Nice to meet you, {self.user_name}!"

    def _recall_name(self, match):
        if self.user_name:
            return f"You're {self.user_name}, of course!"
        return "I don't know your name yet. Tell me with 'my name is ...'."

    def _forget_name(self, match):
        self.user_name = None
        self._save_memory()
        return "Okay, I've forgotten your name."

    def _how_are_you(self, match):
        self._pending = "mood"  
        return self._pick(R.HOW_ARE_YOU)

    def _tell_time(self, match):
        return f"It's {self._clock().strftime('%I:%M %p')}."

    def _tell_date(self, match):
        return f"Today is {self._clock().strftime('%A, %B %d, %Y')}."

    def _flip_coin(self, match):
        return f"It's {self._rng.choice(['heads', 'tails'])}!"

    def _roll_die(self, match):
        return f"You rolled a {self._rng.randint(1, 6)}."

    # understanding the message
    @staticmethod
    def _normalize(text):
        """Lowercase, drop punctuation (keeping apostrophes and math symbols), squash spaces."""
        text = re.sub(r"[^\w\s'+\-*/().^%]", " ", text.lower())
        return " ".join(text.split())

    @staticmethod
    def _fix_typos(text):
        """Correct near-misses of a few keywords ('wether' -> 'weather')."""
        def fix(match):
            word = match.group(0)
            if len(word) < MIN_TYPO_LENGTH or word in KEYWORDS:
                return word
            close = difflib.get_close_matches(word, KEYWORDS, n=1, cutoff=TYPO_CUTOFF)
            return close[0] if close else word

        return _WORD.sub(fix, text)

    def _prepare(self, user_input):
        return self._fix_typos(self._normalize(user_input))

    def is_exit(self, user_input):
        """True for short goodbyes. Whole words only, so 'maybe' or
        'I will tell you more later today' don't end the chat."""
        words = _WORD.findall(self._prepare(user_input))
        return 0 < len(words) <= MAX_EXIT_WORDS and any(word in EXIT_COMMANDS for word in words)

    def _try_math(self, text):
        if not re.search(r"\d", text):
            return None
        expression = text
        for word, symbol in MATH_WORDS:
            expression = re.sub(rf"\b{word}\b", f" {symbol} ", expression)
        match = MATH_PATTERN.match(" ".join(expression.split()))
        if not match:
            return None
        expression = match.group(1).strip()
        if not re.search(r"[+\-*/%^]", expression):
            return None
        try:
            return f"{expression} = {format_number(calculate(expression))}"
        except CalculatorError as error:
            return str(error)

    def _answer_mood(self, text):
        """Reply to 'good' / 'not good' after the bot asked how the user is."""
        words = set(_WORD.findall(text))
        positive = words & R.POSITIVE_WORDS
        negative = words & R.NEGATIVE_WORDS
        if not positive and not negative:
            return None
        is_good = bool(positive) and not negative
        if words & {"not", "never"} or any(word.endswith("n't") for word in words):
            is_good = not is_good
        return self._pick(R.GOOD_MOOD if is_good else R.BAD_MOOD)

    def _match_rules(self, text):
        for pattern, response in self.rules:
            match = pattern.search(text)
            if match:
                return response(match) if callable(response) else self._pick(response)
        return None

    # public API
    def _pick(self, options):
        """Choose a reply, avoiding the one just used when there is a choice."""
        choices = [option for option in options if option != self._last_reply] or list(options)
        return self._rng.choice(choices)

    def reply(self, user_input):
        text = self._prepare(user_input)
        if not text:
            return "Say something and I'll respond!"

        pending, self._pending = self._pending, None

        answer = self._answer_mood(text) if pending == "mood" else None
        if answer is None:
            answer = self._try_math(text)
        if answer is None:
            answer = self._match_rules(text)

        if answer is None:
            self._fallback_streak += 1
            if self._fallback_streak >= STUCK_AFTER:
                self._fallback_streak = 0
                answer = self._pick(R.STUCK)
            else:
                answer = self._pick(R.FALLBACKS)
        else:
            self._fallback_streak = 0

        self._last_reply = answer
        return answer

    def greeting(self):
        if self.user_name:
            return f"Welcome back, {self.user_name}! I'm {self.name}. Type 'exit' to end our chat."
        return f"Hi! I'm {self.name}. Type 'exit' to end our chat."

    def goodbye(self):
        who = f", {self.user_name}" if self.user_name else ""
        return f"Goodbye{who}! Have a great day."

    def chat(self, read=input, write=print):
        """Run the conversation loop. `read` and `write` can be swapped out in tests."""
        write(f"Bot: {self.greeting()}")
        while True:
            try:
                user_input = read("You: ")
            except (EOFError, KeyboardInterrupt):
                write(f"\nBot: {self.goodbye()}")
                break

            if self.is_exit(user_input):
                write(f"Bot: {self.goodbye()}")
                break
            write(f"Bot: {self.reply(user_input)}")
