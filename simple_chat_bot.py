import re
import random

class RuleBot:
    # responses to exit
    exit_commands = ("quit", "pause", "exit", "goodbye", "bye", "later")

    def __init__(self):
        # Defining the rules: {Pattern: [Responses]}
        self.rules = {
            r'hi|hello|hey': [
                "Hello! How can I help you today?", 
                "Hey there! What's on your mind?", 
                "Hi! I'm doing great, how are you?"
            ],
            r'how are you': [
                "I'm functioning within normal parameters!",
                "Doing well, just processing some data. You?",
            ],
            r'your name': [
                "I'm Rai, your friendly neighborhood rule-based bot.",
                "You can call me Rai.",
            ],
            r'weather': [
                "I don't have a window, but I hear the cloud storage is clear today.",
                "It's always 72 degrees inside this server rack."
            ],
            r'help|support': [
                "I can tell you about myself, the weather, or just chat.",
                "I'm here to help! Try asking about my name or how I'm doing."
            ],
            
    #  when confused
            r'.*': [
                "That's interesting! Tell me more.",
                "I'm not sure I follow, could you rephrase that?",
                "Interesting... go on."
            ]
        }

    def greet(self):
        print("Bot: Hi! I'm Rai. Type 'exit' to end our chat.")
        self.chat()

    def make_exit(self, user_input):
        for command in self.exit_commands:
            if command in user_input.lower():
                print("Bot: Goodbye! Have a great day.")
                return True
        return False
        

    def chat(self):
        while True:
            user_input = input("You: ").lower()
            if self.make_exit(user_input):
                break
            
            print(f"Bot: {self.match_reply(user_input)}")

    def match_reply(self, user_input):
        for pattern, responses in self.rules.items():
            
            if re.search(pattern, user_input):
                return random.choice(responses)
        return "I'm not sure what you mean."


if __name__ == "__main__":
    lex = RuleBot()
    lex.greet()
