import json
import random
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download necessary NLTK data
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("wordnet", quiet=True)

lemmatizer = WordNetLemmatizer()

user_memory = {
    "name": "Customer",
    "item": "drink",
    "size": "grande",
    "side": "croissant",
    "drink": "water",
    "quantity": "1",
}

is_awaiting_name = True

DISPLAY_NAMES = {
    "caramel macchiato": "Caramel Macchiato",
    "caffe latte": "Caffè Latte",
    "pink drink": "Pink Drink",
    "frappuccino": "Frappuccino",
    "cold brew": "Cold Brew",
    "latte": "Caffè Latte",
}

NAME_FILLER_WORDS = {
    "i",
    "im",
    "i'm",
    "am",
    "my",
    "name",
    "is",
    "the",
    "a",
    "its",
    "it's",
}


def load_files(filepath="intents.json"):
    with open(filepath, "r") as f:
        data = json.load(f)

    rgx2int = {}
    int2res = {}
    greeting_words = set()

    for intent in data.get("intents", []):
        tag = intent["tag"]
        patterns_list = intent["patterns"]
        regex_key = "|".join([rf"\b({p})\b" for p in patterns_list])
        rgx2int[regex_key] = tag
        int2res[tag] = intent["responses"]

        if tag == "greeting":
            for p in patterns_list:
                greeting_words.update(p.lower().split())

    synonym_rules = {}
    for base_word, synonym_list in data.get("synonyms", {}).items():
        for synonym in synonym_list:
            clean_syn = synonym.lower().replace("'", "")
            synonym_rules[clean_syn] = base_word.lower()

    return rgx2int, int2res, synonym_rules, greeting_words


def preprocess_input(user_input, synonym_rules):
    clean_text = user_input.lower().replace("'", "")

    if synonym_rules:
        sorted_synonyms = sorted(synonym_rules.keys(), key=len, reverse=True)
        synonym_regex = re.compile(
            r"\b(" + "|".join(map(re.escape, sorted_synonyms)) + r")\b"
        )
        clean_text = synonym_regex.sub(
            lambda match: synonym_rules[match.group(0)], clean_text
        )

    clean_text = re.sub(r"[^\w\s]", "", clean_text)
    tokens = word_tokenize(clean_text)
    lemmatized_tokens = [lemmatizer.lemmatize(word, pos="v") for word in tokens]

    return " ".join(lemmatized_tokens)


def extract_named_entities(
    raw_input, processed_input, matched_tag, greeting_words
):
    global user_memory, is_awaiting_name

    name_match = re.search(
        r"\b(name is|i am|i'm|call me)\s+([a-zA-Z]+)", raw_input, re.IGNORECASE
    )
    if name_match:
        user_memory["name"] = name_match.group(2).capitalize()
        is_awaiting_name = False
    elif matched_tag == "name_response":
        candidate_words = [
            w
            for w in re.findall(r"[a-zA-Z']+", raw_input)
            if w.lower() not in greeting_words
            and w.lower() not in NAME_FILLER_WORDS
        ]
        if candidate_words:
            user_memory["name"] = candidate_words[-1].capitalize()
            is_awaiting_name = False

    qty_match = re.search(
        r"\b(\d+|one|two|three|four|five)\s+(?:caramel macchiato|caffe latte|pink drink|frappuccino|cold brew|latte|coffee|drink|item)s?\b",
        processed_input,
    )
    if qty_match:
        user_memory["quantity"] = qty_match.group(1)

    item_match = re.search(
        r"\b(caramel macchiato|caffe latte|pink drink|frappuccino|cold brew|latte)\b",
        processed_input,
    )
    if item_match:
        matched_item_raw = item_match.group(1)
        user_memory["item"] = DISPLAY_NAMES.get(
            matched_item_raw, matched_item_raw.title()
        )

    size_match = re.search(
        r"\b(tall|grande|venti|small|medium|large|trenta)\b", processed_input
    )
    if size_match:
        user_memory["size"] = size_match.group(1)

    side_match = re.search(
        r"\b(croissant|cake pop|muffin|cookie|bagel)\b", processed_input
    )
    if side_match:
        user_memory["side"] = side_match.group(1)


def match_intent(processed_text, rgx2int, greeting_words):
    global is_awaiting_name

    if is_awaiting_name:
        tokens = processed_text.split()
        non_greeting_tokens = [t for t in tokens if t not in greeting_words]
        if non_greeting_tokens:
            return "name_response"
        return "greeting"

    for pattern, tag in rgx2int.items():
        if re.search(pattern, processed_text, re.IGNORECASE):
            return tag

    return None


def generate_response(
    user_input, rgx2int, int2res, synonym_rules, greeting_words
):
    processed_input = preprocess_input(user_input, synonym_rules)
    matched_tag = match_intent(processed_input, rgx2int, greeting_words)

    extract_named_entities(
        user_input, processed_input, matched_tag, greeting_words
    )

    if matched_tag and matched_tag in int2res:
        responses_list = int2res[matched_tag]
        selected_template = random.choice(responses_list)
        try:
            return selected_template.format(**user_memory)
        except KeyError:
            return selected_template

    return "I'm sorry, I couldn't understand your request. Could you please phrase that in a different way?"


def chatbot():
    global user_memory, is_awaiting_name
    user_memory = {
        "name": "Customer",
        "item": "drink",
        "size": "grande",
        "side": "croissant",
        "drink": "water",
        "quantity": "1",
    }
    is_awaiting_name = True

    rgx2int, int2res, synonym_rules, greeting_words = load_files()
    print("Starbucks Automated Order Assistant Activated")
    print("Bot: Type 'exit' or 'quit' anytime to complete your trip.")
    print("Bot: Welcome to Starbucks! Can I get a name for your order today?")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print(
                f"Bot: Thank you for visiting, {user_memory['name']}! Enjoy your {user_memory['quantity']} {user_memory['size']} {user_memory['item']} order!"
            )
            break

        if not user_input:
            continue

        reply = generate_response(
            user_input, rgx2int, int2res, synonym_rules, greeting_words
        )
        print(f"Bot: {reply}")


if __name__ == "__main__":
    chatbot()