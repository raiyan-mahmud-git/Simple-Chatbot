import json
import random
import tempfile
from datetime import datetime
from pathlib import Path

from chatbot import RuleBot
from chatbot import responses as R

FIXED_TIME = datetime(2026, 10, 13, 15, 45)


def make_bot(**kwargs):
    """A bot with a fixed clock and a seeded random generator."""
    return RuleBot(clock=lambda: FIXED_TIME, rng=random.Random(0), **kwargs)


# matching
def test_greeting():
    assert make_bot().reply("hello") in R.GREETINGS
    assert make_bot().reply("Hey!!!") in R.GREETINGS


def test_patterns_match_whole_words_only():
    
    for message in ["this is nice", "which one", "I was thinking about it"]:
        assert make_bot().reply(message) in R.FALLBACKS


def test_bot_name_and_creator():
    assert "Rai" in make_bot().reply("What's your name?")
    assert make_bot().reply("who made you") in R.ABOUT_ME


def test_specific_rules_beat_the_greeting():
    assert make_bot().reply("hi, what is your name") in R.NAME_RESPONSES


def test_empty_input():
    assert "Say something" in make_bot().reply("   ")
    assert "Say something" in make_bot().reply("?!")


def test_no_immediate_repeats():
    bot = make_bot()
    replies = [bot.reply("hello") for _ in range(30)]
    assert all(a != b for a, b in zip(replies, replies[1:]))


# typos
def test_typos_in_keywords_are_understood():
    assert make_bot().reply("whats the wether") in R.WEATHER
    assert make_bot().reply("tell me a jokee") in R.JOKES
    assert make_bot().reply("thankss") in R.THANKS


def test_real_words_are_not_rewritten():
    bot = make_bot()
    for word in ["whether", "watcher", "water", "computer", "quite", "other"]:
        assert bot._fix_typos(word) == word
    
    assert make_bot().reply("I wonder whether it works") in R.FALLBACKS


# time and date
def test_time_and_date_use_the_clock():
    bot = make_bot()
    assert bot.reply("what time is it") == "It's 03:45 PM."
    assert bot.reply("what's the date?") == "Today is Tuesday, October 13, 2026."


# name memory
def test_remembers_name_within_a_chat():
    bot = make_bot()
    assert "Sam" in bot.reply("my name is sam")
    assert "Sam" in bot.reply("what is my name")
    assert "Sam" in bot.goodbye()


def test_unknown_name():
    assert "don't know" in make_bot().reply("who am i")


def test_name_survives_restart_and_can_be_forgotten():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "memory.json"
        make_bot(memory_file=path).reply("my name is sam")

        bot = make_bot(memory_file=path)
        assert bot.user_name == "Sam"
        assert "Welcome back, Sam" in bot.greeting()

        assert "forgotten" in bot.reply("forget my name")
        assert make_bot(memory_file=path).user_name is None


def test_corrupt_memory_file_is_ignored():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "memory.json"
        for junk in ["not json at all", "[1, 2, 3]", json.dumps({"user_name": 5})]:
            path.write_text(junk, encoding="utf-8")
            assert make_bot(memory_file=path).user_name is None


def test_no_memory_file_means_nothing_is_saved():
    bot = make_bot()
    bot.reply("my name is sam")
    assert make_bot().user_name is None


# math
def test_math_in_symbols_and_words():
    bot = make_bot()
    assert bot.reply("calculate 5 + 3 * 2") == "5 + 3 * 2 = 11"
    assert bot.reply("what is 2^10") == "2^10 = 1024"
    assert bot.reply("whats 10 divided by 4") == "10 / 4 = 2.5"
    assert bot.reply("what is 5 plus 3") == "5 + 3 = 8"
    assert bot.reply("7 times 6") == "7 * 6 = 42"


def test_math_errors_get_friendly_replies():
    bot = make_bot()
    assert bot.reply("what is 10 / 0") == "I can't divide by zero."
    assert "too big" in bot.reply("what is 9 ^ 9 ^ 9")
    assert "valid calculation" in bot.reply("calculate 2 +")


def test_numbers_alone_are_not_calculations():
    assert make_bot().reply("42") in R.FALLBACKS


# mood follow-up
def test_mood_follow_up():
    bot = make_bot()
    assert bot.reply("how are you") in R.HOW_ARE_YOU
    assert bot.reply("good thanks") in R.GOOD_MOOD

    bot.reply("how are you")
    assert bot.reply("I'm tired") in R.BAD_MOOD

    bot.reply("how are you")
    assert bot.reply("not good") in R.BAD_MOOD

    bot.reply("how are you")
    assert bot.reply("not bad") in R.GOOD_MOOD


def test_mood_answer_only_counts_right_after_the_question():
    assert make_bot().reply("good") in R.FALLBACKS

    bot = make_bot()
    bot.reply("how are you")
    assert bot.reply("what is the weather") in R.WEATHER
    assert bot.reply("good") in R.FALLBACKS


# fun and fallbacks
def test_coin_and_die():
    bot = make_bot()
    assert bot.reply("flip a coin") in ("It's heads!", "It's tails!")
    assert bot.reply("roll a die") in [f"You rolled a {n}." for n in range(1, 7)]


def test_suggests_help_when_stuck():
    bot = make_bot()
    replies = [bot.reply(message) for message in ["blah", "bleh", "blorp"]]
    assert replies[0] in R.FALLBACKS and replies[1] in R.FALLBACKS
    assert replies[2] in R.STUCK
    assert bot.reply("blip") in R.FALLBACKS


def test_understood_message_resets_the_stuck_counter():
    bot = make_bot()
    bot.reply("blah")
    bot.reply("bleh")
    bot.reply("hello")
    assert bot.reply("blorp") in R.FALLBACKS


# exiting
def test_exit_needs_whole_words_in_short_messages():
    bot = make_bot()
    for message in ["bye", "Goodbye!", "see you later", "quit", "I quit", "goodby"]:
        assert bot.is_exit(message), message
    for message in ["maybe", "that's quite nice", "I will tell you more about my plans later today", "", "hello"]:
        assert not bot.is_exit(message), message


# the chat loop
def run_chat(inputs, **kwargs):
    lines = iter(inputs)
    output = []
    make_bot(**kwargs).chat(read=lambda prompt: next(lines), write=output.append)
    return output


def test_chat_loop_ends_on_goodbye():
    output = run_chat(["hello", "my name is sam", "bye", "this is never read"])
    assert output[0].startswith("Bot: Hi! I'm Rai")
    assert output[-1] == "Bot: Goodbye, Sam! Have a great day."
    assert len(output) == 4


def test_chat_loop_survives_ctrl_c_and_end_of_input():
    for error in (EOFError, KeyboardInterrupt):
        output = []

        def read(prompt, error=error):
            raise error

        make_bot().chat(read=read, write=output.append)
        assert "Goodbye" in output[-1]
