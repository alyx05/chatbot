# Conversational Order Assistant (Starbucks Barista Engine)

A rule-based conversational agent and domain-specific Natural Language Understanding (NLU) dialogue system built in Python[cite: 2]. The system processes customer beverage and pastry orders through multi-turn state tracking, synonym resolution, regular expression entity extraction, and lemmatized intent matching[cite: 2].

---

## Key Features

- **Multi-Stage NLU Pipeline:** Normalizes domain synonyms, strips punctuation, tokenizes input, and lemmatizes verb tokens to root forms via NLTK's `WordNetLemmatizer`[cite: 2].
- **Slot-Filling & Entity Extraction:** Dynamically parses customer order details—including item types, standard cup sizes (Tall, Grande, Venti), bakery sides, quantities, and customer names[cite: 2].
- **Contextual State Management:** Tracks conversational state via an in-memory session dictionary (`user_memory`) to populate dynamic template strings[cite: 2].
- **Intent Disambiguation Guards:** Features targeted guards against premature slot hijacking (e.g., distinguishing when a user introduces themselves vs. orders a menu item)[cite: 2].

---

## Tech Stack

- **Language:** Python 3.10+[cite: 2]
- **NLP & Text Processing:** NLTK (`word_tokenize`, `WordNetLemmatizer`), Regular Expressions (`re`)[cite: 2]
- **Data Configuration:** JSON (`intents.json`)[cite: 1, 2]

---

## Architecture Flow