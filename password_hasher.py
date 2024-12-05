import hashlib
import random
from os import environ
import string

server_salt = environ.get('server_salt')
all_symbols = string.ascii_uppercase + string.ascii_lowercase + string.digits+ string.punctuation

def generate_random_string(length=10):
    return ''.join(random.choices(all_symbols, k=length))

# server:password:salt
def create_new_hash(password):
    salt = generate_random_string(random.randint(5, 15))
    result = server_salt+password+salt
    hash_passwd = hashlib.sha256(result.encode('utf-8'))
    
    return hash_passwd.hexdigest(), salt
    
def compare_passwords(hash_passwd, current_password, salt):
    result = server_salt+current_password+salt
    new_hash_passwd = hashlib.sha256(result.encode('utf-8'))
    
    if new_hash_passwd.hexdigest() == hash_passwd:
        return True
    return False

if __name__ == '__main__':
    print(all_symbols)
    print(generate_random_string(13))
    
    print(create_new_hash('paswd1'))
    
    passwd = 'c4107fcfdf7546a2caa2464a4fbaeda4b60b11ece024c161e46a33b323ec95e2'
    print(compare_passwords(passwd, 'paswd1', 'zSC"vu|so-'))

# hash_object = hashlib.sha256(b'Hello World22')
# hex_dig = hash_object.hexdigest()
# print(len(hex_dig), hex_dig)

# username:password:salt
# server:password:salt
