from helpers import converters

def to_model(type_):
    def to_type(func):
        async def wrapper(*args, **kwargs):
            sql_obj = await func(*args, **kwargs)
            if sql_obj:
                model_obj = converters.to_model(type_, sql_obj)
                return model_obj
        return wrapper
    return to_type

def from_model(type_):
    def to_sql(func):
        async def wrapper(*args, **kwargs):
            if len(args) == 1:
                args = (converters.to_sql(type_, args[0]), )
            else:
                args = (converters.to_sql(type_, args[0]), args[1:])
            return await func(*args, **kwargs)
        return wrapper
    return to_sql
