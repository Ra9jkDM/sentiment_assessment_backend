import numpy as np
import pandas as pd
import torch
# from stream_preprocessing_cls import BackgroundProcessing, Task, load_data
from services.ml.stream_preprocessing_cls import BackgroundProcessing, Task, load_data
import json
# from lstm_model_structure import LSTM
from services.ml.lstm_model_structure import LSTM
from torch.utils.data import Dataset


device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

# model = LSTM(65892, 64, 128, 2, 5165)
# model.load_state_dict(torch.load('services/ml/models/e5_lstm_web.pt'))
# model structure in file 'lstm_model_structure.py'
import __main__
setattr(__main__, "LSTM", LSTM)
model = torch.load('services/ml/models/e5_lstm_web.pt', weights_only=False)
model.eval()
model = model.to(device)

word_dict = {}
with open('services/ml/models/word_dict.json', 'r') as f:
    word_dict = json.loads(f.read())

TEXT_LEN = 10
MAX_BATCH_SIZE = 5
MAX_TEXT_LEN = -1 # ToDo

class LenOrderDataset(Dataset):
    def __init__(self, inputs, targets):
        self.data = zip(inputs, targets)
        self.data = sorted(self.data, key=lambda x: len(x[0]))
        
        padding = 0 # если после очистки текста от отзыва ничего не осталось
        for i in self.data:
            if len(i[0]) == 0:
                padding += 1

        self.data = self.data[padding:]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx][0], self.data[idx][1]

class OrderedDataLoader:
    def __init__(self, dataset, batch_size, shuffle=False):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        
        self.idx = 0
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if len(self.dataset) >= self.idx:
            self.idx+=self.batch_size
            last = min(self.idx, len(self.dataset))
            
            batch_range = range(self.idx - self.batch_size, last)
            data = [self.dataset[i] for i in batch_range]

            if self.shuffle:
                random.shuffle(data)

            
            x = [i[0] for i in data]
            index = [i[1] for i in data]
            x = self._make_data_same_len(x)
            
            return torch.IntTensor(x), index
        else:
            raise StopIteration


    def _make_data_same_len(self, batch):
        return set_text_len(batch, len(batch[-1]))

def predict(text):
    clear_text, tokens = bg.preprocess_simple_text(text)

    with torch.no_grad():
        X = torch.IntTensor([tokens]).to(device)
        output = model(X)
        output = output.argmax().cpu()

    return {'text': text,
            'clear_text': clear_text,
            'pred': int(output), 
            'pred_word': 'positive' if output == 1 else 'negative'}


def predict_table(data):
    # ToDo: сохранить имя в БД
    task = Task(name='xyz', data=data)
    bg.add_task(task)

def _predict(df, row_name):
    # ToDo: do it in thread (with multithreading lib)
        # print(data)
        
        # data = set_text_len(data[row_name], TEXT_LEN)
        # tensor = torch.IntTensor(data).to(device) # ToDo: use DataLoader to split big data on batches 

        # print(tensor)
        # with torch.no_grad():
        #     result = model(tensor)
        #     print(result)
    data_ds = LenOrderDataset(df[row_name], df.index)
    data_loader = OrderedDataLoader(data_ds,  batch_size=MAX_BATCH_SIZE)

    with torch.no_grad():
        for X, index in data_loader:
            X = X.to(device)
            outputs = model(X)
            outputs = [i.argmax().cpu() for i in outputs]

            for idx, pred in zip(index, outputs):
                df.at[idx, 'pred'] = int(pred)
    print(df)
    return df

def set_text_len(texts, max_len):
    array = np.zeros([len(texts), max_len])

    i = 0
    for value in texts:
        tmp = max_len-len(value)
        tmp = tmp if tmp > 0 else 0

        text = np.concatenate((value[:max_len], np.zeros(tmp)))
        array[i] = text
        i+=1

    return array 




bg = BackgroundProcessing(word_dict, _predict)

if __name__ == '__main__':
    print(torch.__version__)

    data = load_data(f'data/test_ml_3.xlsx', 'xlsx')
    predict(data)


# ToDo jupyter notebook
# интегрировать алгоритм DataLoader in order
# http://localhost:8888/notebooks/%D0%94%D0%B8%D0%BF%D0%BB%D0%BE%D0%BC/Projects/preprocess_data_git/ML_LSTM_2_val_loss_for_web-app.ipynb
# попробовать поменять параметор смешивания в
# class OrderedDataLoader: self.dataset.get_idx(20) и self.range = 20
# для улучшения обучения, self.range-кол-во записей