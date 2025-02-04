# import pandas as pd
import numpy as np
import re
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,

    Doc
)
import json

def remove_words(text):
    text = text.replace('[ФИО вырезано модератором]', ' ')
    text = text.replace('RT', ' ')
    
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', text) # Удаление ссылок
    text = re.sub('@[\S_]+', '', text) # Удаление username
    text = re.sub('".+"', '', text) # Удаление названий. Пример: "ООО ..."
    text = re.sub('«.+»', '', text) 
    text = re.sub('#[\S\d_]+', '', text) # Удаление хештегов
    text = text.replace("ё", "е")
    text = text.replace('\\n', ' . ')
    text = re.sub(r'(хаха)+', ' ха_ха ', text)   
    return text

duplicates = re.compile(r'(.)\1{2,}')

def remove_duplicates(text):
    dupl = duplicates.search(text)
    
    while dupl:
        span = dupl.span()
        text = text[: span[0]+1] + text[span[1]:]
        dupl = duplicates.search(text)
    del dupl
    return text


segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)
names_extractor = NamesExtractor(morph_vocab)

def create_doc(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)
    return doc, morph_vocab

def remove_names_organizations(text):
    doc, morph_vocab = create_doc(text)
    
    for span in doc.spans:
        span.normalize(morph_vocab)

    remove = [(word.text, word.start, word.stop) for word in doc.spans]
    result = ''
    start = 0
    
    for i in remove:
        result+=text[start: i[1]]
        start=i[2]
    else:
        result+=text[start:]
    
    if len(remove) == 0:
        result = text

    del doc, morph_vocab
    return result

def take_only_text(text):
    text = text.lower()
    for i in list('?!().-0123456789;:,#$%&\\/*+<=>@[') + ['...']: # !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
        text = text.replace(i, ' ')
    text = re.sub('[^\x00-\x7Fа-яА-Я]', ' ', text) # Удаляем эмоджи
    symbols = re.findall("[а-я\s_]", text) # Оставляем только буквы
    text = ''.join(symbols)
    text = re.sub(' +', ' ', text) # Оставляем между словами 1 пробел
    del symbols
    return text.strip()

def lemmatization(text):
    doc, morph_vocab = create_doc(text)
    
    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    result = [i.lemma for i in doc.tokens]
    del doc, morph_vocab
    return result

def clear(text):
    funcs = [remove_words, remove_duplicates, remove_names_organizations,
             take_only_text, lemmatization]
    for func in funcs:
        # print(text)
        if len(text.strip()) != 0:
            text = func(str(text))
    del funcs
    return text

def clear_text(text):
    return ' '.join(clear(text))

def text2numbers(text, dict_): 
    text = text.split(' ')
    sequence = []

    for i in text:
        if i in dict_.keys():
            sequence.append(dict_[i])

    return sequence

def texts2tokens(row):
    return [text2numbers(i, dict_=word_dict) for i in row]


if __name__ == '__main__':
    example = '''Анна Якубаб «Глорию Скотт»\n@VekshinaI 
    обожаю тебя и наши покатушки на машинке:*\nRT @make_me_strong_: @smille_Tommo
     пхаххаха:D Заипись\n06.12.2013 / Вечерний Маскарад:) http://t.co/oYSJpAawmX
     \nСанкт-Петербургская, 9:00 - 12:15 день, О центре развития Baby time, 
     .Спасибо Анхель и Хорхе, 7.10.2020 года, конкурс3\n)В. А. Рождественский  
     Школа №321 нам 3.3 года. \n\nМы уже не ждали и не надеялись...\nЗакончил 
     академию BARBER WANTED 15.02.2019 года'''
    norm_form = clear_text(example)
    print(norm_form)

    word_dict = {}
    with open('models/word_dict.json', 'r') as f:
        word_dict = json.loads(f.read())

    result = text2numbers(norm_form, word_dict)
    print(result)
