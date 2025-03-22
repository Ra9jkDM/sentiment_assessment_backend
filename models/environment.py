from os import environ

def get_postfix():
    postfix = ''
    app_mode = environ.get('app_mode') 
    if app_mode == 'test':
        postfix = '_test'

    return postfix