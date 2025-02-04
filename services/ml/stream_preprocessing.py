from multiprocessing import Process, Manager
import pandas as pd
# from services.ml import data_preprocessing
import data_preprocessing
import queue
import threading

manager = Manager()
lock = manager.Lock()
data_lock = manager.Lock()
preprocessed_data = manager.dict({'task_x':[]})
result_data = manager.dict()

main_thread = None

MAX_CORES = 4
CLEAR_TEXT = 'clear_text'
work_queue = queue.Queue()
# preprocessed_data = {'task_0':{'data': {1: '', 2: ''}, 'task_x': {1:'', 2:'', 3:'', 4:''}}}

class Task:
    def __init__(self, name, data):
        self.name = name
        self.data = data

def load_data(path, extension):
    df = None
    ext_func = {'csv': pd.read_csv, 'xlsx': pd.read_excel}
    df = ext_func[extension](path)
    return df

def devide_file(df, parts):
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

def _preprocess_text(column):
    def wrapper(row, *args, **kwargs):
        row[CLEAR_TEXT] = data_preprocessing.clear_text(str(row[column]))
        return row
    return wrapper

def preprocess_data_worker(data, task_name, part):
    text = data.apply(_preprocess_text(data.columns[0]), axis=1)
    global preprocessed_data
    # print(preprocessed_data, task_name, part)
    lock.acquire()
    preprocessed_data[f'{task_name}_{part}'] = text
    lock.release()

def run_data_preprocess():
    while not work_queue.empty():
        thread_list = []

        task = work_queue.get()
        data = devide_file(task.data, MAX_CORES)
        for i in range(MAX_CORES):
            thread_list.append(Process(target=preprocess_data_worker, args=(data[i], task.name, i)))
            thread_list[i].start()

        for i in range(MAX_CORES):
            print('MulT', i)
            thread_list[i].join()

        global result_data
        data = join_results(task.name, MAX_CORES)
        data_lock.acquire()
        result_data[task.name] = data
        # notify NN
        data_lock.release()
        

def join_results(name, parts):
    names = [f'{name}_{i}' for i in range(parts)]
    global preprocessed_data
    all_data = pd.concat([preprocessed_data[i] for i in names])
    for i in names:
        preprocessed_data[i] = ''
    return all_data

def create_and_start_main_process():
    global main_thread
    main_thread = threading.Thread(target=run_data_preprocess)
    main_thread.start()
    # main_thread.join()
    # print(main_thread.is_alive())

def add_task(task):
    global main_thread

    work_queue.put(task)

    if not main_thread.is_alive():
        print('Tread dead')
        create_and_start_main_process()


if __name__ == '__main__':
    data = [load_data(f'data/test_ml_{i}.xlsx', 'xlsx') for i in range(1, 4)]

    # devide_file(data[0], 4)

    task1 = Task(name='t1', data=data[0])
    task2 = Task(name='t2xyz', data=data[1])
    # work_queue.put(Task(name='t1', data=data[0]))
    # work_queue.put(Task(name='t2xyz', data=data[1]))

    create_and_start_main_process()
    add_task(task1)
    add_task(task2)
    # run_data_preprocess()
    # print(preprocessed_data)
    print(result_data)
    # 1. 4 ядра для обработки данных (приведения в нормальную форму и очистки текстов)
    # 2. 1 поток/ядро для загрузки данных на видеокарту и предсказания тональности 
    # (+ задать лимиты, чтобы на видеокарте хватило видеопамяти)
    pass

# ToDo: 
# завернуть в класс
# попробовать, как работает с FastApi
# (схема работы: добавляем задачу с уникальным идентификатором в 
# качестве имени и возвращаем, что задача добавлена работу
# (можно открыть websockets, чтобы отслеживать прогресс),
# так же эту инфу добавляем в БД psql. задача выполняется в background)
