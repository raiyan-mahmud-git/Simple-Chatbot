# Simple-Chatbot
A rule-based Python chatbot using Regex for pattern matching. It recognizes user intent within sentences and selects randomized responses from a dictionary, balancing structured logic with a natural, conversational feel.


# Rai: A Rule-Based Python Chatbot

A lightweight, pattern-matching chatbot built with Python. Rai uses Regular Expressions (Regex) to understand user intent and provides randomized responses to simulate a more natural conversation.

## Features
* **Regex Pattern Matching:** Understands keywords within sentences rather than exact matches.
* **Varied Responses:** Uses a randomized response pool to keep the dialogue from feeling repetitive.
* **Graceful Exit:** Recognizes multiple "quit" commands like *bye*, *exit*, or *later*.
* **Fall-back Logic:** Includes a "catch-all" response to handle unrecognized inputs.

##  Getting Started

### Prerequisites
* Python 3.x installed on your machine.
* No external libraries are required (uses built-in `re` and `random` modules).

### Installation & Running
1. **Clone or Copy the code:**
   Save the Python script as `bot.py`.

2. **Run the script:**
   Open your terminal or command prompt and run:
   ```bash
   python bot.py
3. Interact:
Start typing! Try saying "Hello," "Who are you?" or "What's the weather like?"

##​ Customizing the Rules
​You can easily make the bot smarter by editing the self.rules dictionary in the code.
​Format:

r'your|pattern|here': [
    "Response Option 1",
    "Response Option 2" 
]
    
Example Dialogue
​Bot: Hi! I'm Rai. Type 'exit' to end our chat.
You: Hey there, how are you?
Bot: Doing well, just processing some data. You?
You: I'm good. What is your name?
Bot: You can call me Lex.
You: goodbye
Bot: Goodbye! Have a great day.
​
​## License
​This project is open-source and free to use for educational purposes.
