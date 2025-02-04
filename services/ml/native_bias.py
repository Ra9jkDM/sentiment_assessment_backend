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

    # ToDo выделить в отделный поток и ограничить кол-во потоков
    # которые могут заниматься данной задачей + ограничить размер файла 
    # исходя из оперативной памяти

    # ** для ускорения работы можно выделить потоки, 
    #чтобы они вместе предобабатывали данные (Многоядерная обработка)

    # create queue
    # queue.addTask()
    # создать процесс глобально -> если не занят - начать обработку
    #                       если занят - добавить в очередь и ждать
    # после завершения работы процессом посмотреть остались ли задачи в очереди
    # можно передать callback функцию для сигнала, о том, что задача выполнена
    # ** предобработку текста и выполнения прогноза разбить на 2 независимые задачи
    # можно использовать веб-сокеты для ожидания окончания проверки и передачи результата
    # !!!вынести в отдельный файл!!!

    # def devide_texts(df, parts = 5):
    # l = len(df)//parts
    # data = []
    # amount = 0
    
    # for i in range(parts):
    #     if i + 1 == parts:
    #         data.append(df[i*l:-1])
    #     else:
    #         data.append(df[i*l:(i+1)*l])
            
    #     # print(len(data[i]), i*l, (i+1)*l)
    #     amount+=len(data[i])
    
    # print('Amount:', amount)
    # for i, value in enumerate(data, start = 1):
    #    print(f'Part {i}, data len: {len(value)}')

    # return data

load_model('services/ml/models/MulNB_tfidf_classifier.pickle')