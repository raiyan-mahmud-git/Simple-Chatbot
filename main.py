"""Chat with Rai:  python main.py

Options:
    --no-memory    don't save or load your name
    --log FILE     append the whole conversation to FILE
"""

import argparse
from contextlib import nullcontext
from pathlib import Path

from chatbot import RuleBot

MEMORY_FILE = Path(__file__).with_name("rai_memory.json")


def main():
    parser = argparse.ArgumentParser(description="Chat with Rai, a rule-based chatbot.")
    parser.add_argument("--no-memory", action="store_true", help="don't save or load your name")
    parser.add_argument("--log", metavar="FILE", help="append the conversation to FILE")
    args = parser.parse_args()

    bot = RuleBot(memory_file=None if args.no_memory else MEMORY_FILE)

    with (open(args.log, "a", encoding="utf-8") if args.log else nullcontext()) as log:

        def write(text):
            print(text)
            if log:
                log.write(text + "\n")

        def read(prompt):
            value = input(prompt)
            if log:
                log.write(f"{prompt}{value}\n")
            return value

        bot.chat(read=read, write=write)


if __name__ == "__main__":
    main()
