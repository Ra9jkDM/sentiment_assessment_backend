import pickle
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from services.ml import data_preprocessing
import numpy as np

model_NB = None

def load_model(path):
    global model_NB
    with open(path, 'rb') as f:
        model_NB = pickle.load(f)

def predict(text: str):
    clear_text = data_preprocessing.clear_text(text)
    in_text = np.array(clear_text.split())
    pred = model_NB.predict([text])

    return {'text': text,
                    'clear_text': clear_text,
                    'pred': str(pred[0]), 
                    'pred_word': 'positive' if pred[0]== 1 else 'negative'}



load_model('services/ml/models/MulNB_tfidf_classifier.pickle')