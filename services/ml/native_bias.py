import pickle
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from services.ml import data_preprocessing
import numpy as np
import pandas as pd
import io

from multiprocessing import Process

model_NB = None
CLEAR_TEXT = 'clear_text'

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


def _preprocess_text(column):
    def wrapper(row, *args, **kwargs):
        row[CLEAR_TEXT] = data_preprocessing.clear_text(str(row[column]))
        return row
    return wrapper

def predict_table(file, extension):
    df = None

    ext_func = {'csv': pd.read_csv, 'xlsx': pd.read_excel}
    df = ext_func[extension](file.file.read())
    df = df.apply(_preprocess_text(df.columns[0]), axis=1)
    
    df['pred'] = model_NB.predict(df[CLEAR_TEXT])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as f:
        df.to_excel(f)
    buffer.seek(0)
    
    return buffer, {
        'amount': int(df.pred.count()),
        'positive': int(df[(df['pred'] == 1)].pred.count())
    }

# load_model('services/ml/models/MulNB_tfidf_classifier.pickle')