from google import genai
import numpy as np
from transformers import pipeline
import torch
import random

client = genai.Client(api_key="AIzaSyDsCagF6HiRBunoQg2hWR5JEBnIgtUJfPA")
device = 0 if torch.cuda.is_available() else -1

message = "" # temp


# Responses --------------------------------------------------------------------------------------------------------------------



def gemini_call(prompt, message):
    response =  client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{prompt}\n Message: {message}"
        )
    return response.candidates[0].content.parts[0].text.strip()


def level_1(message):
    prompt = "Your job is to choose an emoji to add to the end of message. The emoji should make the message as horny as possible. Respond to this with only the text followed by the emoji you think would be the best fit."
    return gemini_call(prompt, message)

def level_2(message):
    prompt = "I want you to choose a word from the folllowing message and edit to make is horny/funny as possible. Only respond with the changed sentence and nothing else." 
    return gemini_call(prompt, message)

def level_3(message):
    prompt = "I want you to change to following message to make it slightly horny, dont change it too much, just enough to be kind of horny. Repond with only the changed message"
    return gemini_call(prompt, message)

def level_4(message):
    prompt = "I want you to edit this message to make it horny, make it funny and very horny, dont make it too long. Respond with only the changed message and nothing else."
    return gemini_call(prompt, message)

def level_5(message):
    prompt = "I want you to change the following message to be as horny as possible, im talking about generational levels of horny. Make sure you dont make it too long tho. respond with only the edited message and nothing else."
    return gemini_call(prompt, message)

# stat model --------------------------------------------------------------------------------------------------------------------

message_count = 0 # temp while waitiing for the actuale function

p = [0,0,0,0,0] # probability for levels

p_val = {'message count p': [0.12,0.09,0.06,0.04,0.03],
         'emotion p': [0.01,0.01,0.01,0.01]} # probability values []

e_classifier = pipeline(
        "text-classification", 
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=1,
        device = device
    )


def p_mod_n(): # probability augmented by message count
    global p
    for i in range(len(p)):
        p[i] = message_count * p_val['message count p'][i]

def emotion_classifier(message):
    text = message
    return e_classifier(text)[0][0]


def p_emotion(message):
    """Adjust p based on emotion classification."""
    global p
    emotion_value = emotion_classifier(message)
    label = emotion_value['label'].lower()
    score = emotion_value['score']

    emotion_map = {
        'anger': 0,
        'surprise': 1,
        'fear': 2,
        'disgust': 3
    }

    if label in emotion_map:
        idx = emotion_map[label]
        for i in range(len(p)):
            p[i] += score * p_val['emotion p'][idx]
    return


def choose_level():
    """
    Randomly choose a level (1–5) based on probabilities p.
    The function may also choose 'none' if the total probability is small.
    """
    total_p = sum(p)
    
    # Define the chance of choosing "no level"
    # When total_p is small, "none" is more likely.
    # You can tune this curve — this one keeps probabilities in [0, 1].
    none_weight = max(0.0, 5.0 - total_p) #NONE WEIGHT

    # Normalize everything, including "none"
    weights = p + [none_weight]
    total = sum(weights)
    weights = [x / total for x in weights]

    # Include "none" as the last option
    choices = list(range(1, len(p) + 1)) + ["none"]

    choice = random.choices(choices, weights=weights, k=1)[0]
    return choice


# main --------------------------------------------------------------------------------------------------------------------

def main(message):
    p_mod_n()
    p_emotion(message)
    level = choose_level()
    if level == 1:
        return level_1(message)
    elif level == 2:
        return level_2(message)
    elif level == 3:
        return level_3(message)
    elif level == 4:
        return level_4(message)
    elif level == 5:
        return level_5(message)
    return message

    


# Testing --------------------------------------------------------------------------------------------------------------------

def level_test():
    print(level_1("hey, how are you doing?"))
    print(level_2("hey, how are you doing?"))
    print(level_3("hey, how are you doing?"))
    print(level_4("hey, how are you doing?"))
    print(level_4("hey, how are you doing?"))
# level_test()

message_count = 10
message = "heyyyy, how are you doing??"
print(main(message))