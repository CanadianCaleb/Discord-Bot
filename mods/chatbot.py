import random

def chatbot_response(msg):
    res = random.choice(["Ask Red", "Most likely.", "Yes.", "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "Yes.", "Signs point to yes.", "Ah I see it, yes.", "Don't count on it.", "My reply is no.", "My sources say no.", "Very doubtful.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now", "Cannot predict now.", "Concentrate and ask again.", "Uhhh."])
    return res
