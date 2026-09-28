import re

STOP_WORDS = {
    "the","is","are","was","were","a","an","and","or","of","to","in","on",
    "for","with","by","from","this","that","has","have","had","be","been",
    "being","will","would","can","could","should","about","into","after",
    "before","than","their","they","them","its","it","as","at","he","she",
    "his","her","you","your","we","our","i","me","my","not","but","if",
    "then","there","here","what","which","who","whom","when","where","how"
}

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [
        word for word in text.split()
        if word not in STOP_WORDS and len(word) > 2
    ]
    return " ".join(tokens)
