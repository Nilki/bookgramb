import re
import numpy as np
from keras.models import load_model
from nltk.tokenize import word_tokenize


def _removeNonAscii(s):
    return "".join(i for i in s if ord(i) < 128)


def clean_text(text):
    text = text.lower()
    text = re.sub(r"what's", "what is ", text)
    text = text.replace('(ap)', '')
    text = re.sub(r"\'s", " is ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r"\\", "", text)
    text = re.sub(r"\'", "", text)
    text = re.sub(r"\"", "", text)
    text = re.sub('[^a-zA-Z ?!]+', '', text)
    text = _removeNonAscii(text)
    text = text.strip()
    return text

def tokenizer(cleaned_text):
    tokens = word_tokenize(cleaned_text)
    return tokens



def get_genre(description):

    BookModel1 = load_model('models/BookModel1.h5')
    max_desc_length = 200

    labels = ['fiction', 'nonfiction']

    cleaned_text = clean_text(description)
    tokenized_text = tokenizer(cleaned_text)
    print(tokenized_text)
    input_data = np.reshape(tokenized_text, (1, max_desc_length))
    output = BookModel1.predict(input_data, batch_size=1)
    score = (output > 0.5) * 1
    pred = score.item()
    return labels[pred]
    # print(description)
