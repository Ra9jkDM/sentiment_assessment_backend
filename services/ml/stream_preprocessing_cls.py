from multiprocessing import Process, Manager
import pandas as pd
from services.ml import data_preprocessing
# import data_preprocessing
import queue
import threading
import json


def load_data(path, extension):
    ext_func = {'csv': pd.read_csv, 'xlsx': pd.read_excel}
    df = ext_func[extension](path)
    return df

class Task:
    def __init__(self, name, data):
        self.name = name
        self.data = data

class BackgroundProcessing:
    MAX_CORES = 4
    CLEAR_TEXT = 'clear_text'
    TOKENS = 'tokens'
    main_thread = None

    work_queue = queue.Queue()
    manager = Manager()
    lock = manager.Lock()
    data_lock = manager.Lock()
    preprocessed_data = manager.dict()
    result_data = manager.dict()

    def __init__(self, word_dict, pred_func, max_cores = 4):
        self.word_dict = word_dict
        self.pred_func = pred_func
        self.MAX_CORES = max_cores
        
        self.create_and_start_main_process()

    def devide_file(self, df, parts):
        length = len(df)//parts
        data = []
        amount = 0
        
        for i in range(parts):
            if i + 1 == parts:
                data.append(df[i*length:-1])
            else:
                data.append(df[i*length:(i+1)*length])
                
            amount+=len(data[i])
        
        # print('Amount:', amount)
        # for i, value in enumerate(data, start = 1):
        #    print(f'Part {i}, data len: {len(value)}')

        return data

    def _preprocess_text(self, column):
        def wrapper(row, *args, **kwargs):
            row[self.CLEAR_TEXT] = data_preprocessing.clear_text(str(row[column]))
            row[self.TOKENS] = data_preprocessing.text2numbers(row[self.CLEAR_TEXT], self.word_dict)
            return row
        return wrapper
    
    def preprocess_simple_text(self, text):
        clear_text = data_preprocessing.clear_text(str(text))
        tokens = data_preprocessing.text2numbers(clear_text, self.word_dict)
        return clear_text, tokens

    def preprocess_data_worker(self, data, task_name, part):
        text = data.apply(self._preprocess_text(data.columns[0]), axis=1)
        self.lock.acquire()
        self.preprocessed_data[f'{task_name}_{part}'] = text
        self.lock.release()
        # print(self.preprocessed_data)

    def run_data_preprocess(self):
        while not self.work_queue.empty():
            thread_list = []

            task = self.work_queue.get()
            data = self.devide_file(task.data, self.MAX_CORES)
            for i in range(self.MAX_CORES):
                thread_list.append(Process(target=self.preprocess_data_worker, args=(data[i], task.name, i)))
                thread_list[i].start()

            for i in range(self.MAX_CORES):
                print('MulT', i)
                thread_list[i].join()

            data = self.join_results(task.name, self.MAX_CORES)
            self.data_lock.acquire()
            # self.result_data[task.name] = data
            # notify NN
            self.pred_func(data, row_name=self.TOKENS)
            self.data_lock.release()
        

    def join_results(self, name, parts):
        names = [f'{name}_{i}' for i in range(parts)]
        all_data = pd.concat([self.preprocessed_data[i] for i in names])
        for i in names:
            self.preprocessed_data.pop(i, None)
            # self.preprocessed_data[i] = ''
        return all_data

    def create_and_start_main_process(self):
        self.main_thread = threading.Thread(target=self.run_data_preprocess)
        self.main_thread.start()
        # main_thread.join()
        # print(main_thread.is_alive())

    def add_task(self, task):
        self.work_queue.put(task)

        if not self.main_thread.is_alive():
            print('Tread dead')
            self.create_and_start_main_process()


if __name__ == '__main__':
    data = [load_data(f'data/test_ml_{i}.xlsx', 'xlsx') for i in range(1, 4)]

    # devide_file(data[0], 4)

    task1 = Task(name='t1', data=data[0])
    task2 = Task(name='t2xyz', data=data[1])
    # work_queue.put(Task(name='t1', data=data[0]))
    # work_queue.put(Task(name='t2xyz', data=data[1]))

    # create_and_start_main_process()
    # add_task(task1)
    # add_task(task2)
        # run_data_preprocess()
        # print(preprocessed_data)
    # print(result_data)

    word_dict = {}
    with open('models/word_dict.json', 'r') as f:
        word_dict = json.loads(f.read())

    bg = BackgroundProcessing(word_dict)
    bg.create_and_start_main_process()
    bg.add_task(task1)
    bg.add_task(task2)
    print(bg.result_data)

    # 1. 4 ядра для обработки данных (приведения в нормальную форму и очистки текстов)
    # 2. 1 поток/ядро для загрузки данных на видеокарту и предсказания тональности 
    # (+ задать лимиты, чтобы на видеокарте хватило видеопамяти)

# ToDo: 
# завернуть в класс
# попробовать, как работает с FastApi
# (схема работы: добавляем задачу с уникальным идентификатором в 
# качестве имени и возвращаем, что задача добавлена работу
# (можно открыть websockets, чтобы отслеживать прогресс),
# так же эту инфу добавляем в БД psql. задача выполняется в background)
