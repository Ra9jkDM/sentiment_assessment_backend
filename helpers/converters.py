from pydantic import BaseModel
from pydantic import parse_obj_as
from models import model
import datetime

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def to_model(target_cls: BaseModel, obj: list[model.Base] | model.Base):
    if isinstance(obj, list): 
        result = [parse_obj_as(target_cls, i.__dict__) for i in obj]
    else:
        result = parse_obj_as(target_cls, obj.__dict__)
    return result

def to_sql(target_cls: model.Base, obj):
    return target_cls(**obj.dict())


def date_to_str(date):
    return date.strftime(DATE_FORMAT)

def str_to_date(str_date):
    return datetime.datetime.strptime(str_date, DATE_FORMAT)