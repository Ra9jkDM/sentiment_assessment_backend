from Crypto.Cipher import AES
import datetime
from os import environ
from base64_random import gen_random_base64
import base64
import random
import string

key = environ.get('server_key')
nonce = environ.get('server_nonce')
all_symbols = string.ascii_uppercase + string.ascii_lowercase + string.digits
# print(len(nonce), len(base64.b64decode(nonce)))

def create_cipher():
    return AES.new(key.encode('utf-8'), AES.MODE_EAX, nonce=base64.b64decode(nonce.encode('utf-8')+b'=='))

def encode(username):
    cipher = create_cipher()
    ciphertext, tag = cipher.encrypt_and_digest(username.encode('utf-8'))
    return base64.b64encode(ciphertext).decode('utf-8')+'.'+ \
            ''.join(random.choices(all_symbols, k=random.randint(20, 40)))

def decode(data):
    cipher = create_cipher()
    username = data.split('.')[0]
    username = base64.b64decode(username)
    plaintext = cipher.decrypt(username)
    return plaintext.decode('utf-8')

def create_key_and_nonce():
    key = gen_random_base64(32)
    nonce = gen_random_base64(24)
    return key, nonce

if __name__ == '__main__':
    key, nonce = create_key_and_nonce()
    print('Key:', key)
    print('Nonce', nonce)
    
    text = encode('bob@c.ts')
    # text = encode('1'*100)
    print(text, len(text.split('.')[0]))
    text = decode(text)
    print(text)
    
    
    # for i in range(1000):
    #     c = create_cipher()
    #     ciphertext, tag = c.encrypt_and_digest('123'.encode('utf-8'))
    


# Структура: username.[(random_string)(date_time)(random_string)]
# закодировано с помощью криптографии (с ключем)

# вторую часть храним в DB и проверяем ее на возможность подмены
# 1 часть, чтобы быстрее находить
# завести таблицу в postgress и интегрировать redis