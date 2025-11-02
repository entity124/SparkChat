from google import genai
from transformers import pipeline
import torch
import random

client = genai.Client(api_key="AIzaSyDsCagF6HiRBunoQg2hWR5JEBnIgtUJfPA")
device = 0 if torch.cuda.is_available() else -1

CONTEXT = "stupid"

LEVEL_PROMPTS = {
    1: "Your job is to choose an emoji to add to the end of the message. The emoji should fit the vibe: {context}. Respond with only the text followed by the emoji.",
    2: "Choose a word from the following message and edit it to make it as {context} as possible. Only respond with the changed sentence and nothing else.",
    3: "Change the following message to make it slightly {context}. Don't change it too much, just enough to hint at the vibe. Respond with only the changed message.",
    4: "Edit this message to make it {context}. Make it funny and very {context}, don't make it too long. Respond with only the changed message and nothing else.",
    5: "Change the following message to be as {context} as possible, I'm talking extreme levels. Make sure you don't make it too long though. Respond with only the edited message and nothing else.",
}


def gemini_call(prompt, message):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{prompt}\n Message: {message}"
    )
    return response.candidates[0].content.parts[0].text.strip()


def transform_at_level(message, context, level):
    prompt = LEVEL_PROMPTS[level].format(context=context)
    return gemini_call(prompt, message)


e_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1,
    device=device,
)

P_MESSAGE_COUNT = [0.16, 0.11, 0.06, 0.04, 0.03]
P_EMOTION = {'anger': 0.24, 'surprise': 0.03, 'fear': 0.12, 'disgust': 0.19, 'sadness': 0.15, 'joy': 0.10}


def compute_probabilities(message, message_count):
    p = [message_count * w for w in P_MESSAGE_COUNT]

    result = e_classifier(message)[0][0]
    label, score = result['label'].lower(), result['score']
    if label in P_EMOTION:
        boost = score * P_EMOTION[label]
        p = [x + boost for x in p]

    return p


def choose_level(p):
    none_weight = max(0.0, 5.0 - sum(p))
    weights = p + [none_weight]
    choices = list(range(1, 6)) + [None]
    return random.choices(choices, weights=weights, k=1)[0]


def transform(message, context=None, message_count=0):
    if context is None:
        context = CONTEXT
    p = compute_probabilities(message, message_count)
    level = choose_level(p)
    if level is None:
        return message
    return transform_at_level(message, context, level)
