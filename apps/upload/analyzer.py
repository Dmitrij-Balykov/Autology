import pymorphy2
morph = pymorphy2.MorphAnalyzer()
from natasha import ( NewsEmbedding, NewsSyntaxParser)
emb = NewsEmbedding()
syntax_parser = NewsSyntaxParser(emb)
from django.http import HttpRequest
request = HttpRequest()
from .graph_app import App

def node_search(tokens, target):
    if target == 'subject':
        stop = ['acl']
        word_check = ['nsubj']
        id_name = 'i.head_id'
    elif target == 'object':
        stop = ['none']
        word_check = ['obj']
        id_name = 'i.head_id'
    elif target == 'act':
        stop = ['obj', 'nsubj','nsubj:pass', 'obl']
        word_check = ['root' , 'acl']
        id_name = 'i.id'
    getting = dict()
    word = []
    ids = []
    multiple_check = False
    for i in tokens:
        if (multiple_check == True) and (i.rel in word_check):
            noun_check = False
            word = sorted(word, key = lambda one:one.id)
            word = [i.text for i in word]
            if target == 'act':
                word = '_'.join(word)
            else:
                word = ' '.join(word)
            if target == 'object' or target == 'subject':
                for wd in word:
                    if 'NOUN' in morph.parse(wd)[0].tag:
                        noun_check = True
            if noun_check == True or target == 'act':
                getting[word]=connection_id
            ids = []
            word = []
            connection_id = eval(id_name)
        if (i.rel in word_check or i.head_id in ids) and (not i.rel in stop):
            if i.rel in word_check:
                connection_id = eval(id_name)
            multiple_check = True
            if i not in word:
                ids.append(i.id)
                word.append(i)
            for y in tokens:
                if (y.head_id in ids) and (not y.rel in stop) :
                    if y not in word:
                        word.append(y)
                        ids.append(y.id)
    noun_check = False
    word = sorted(word, key = lambda one:one.id)
    word = [i.text for i in word]
    if target == 'act':
        word = '_'.join(word)
    else:
        word = ' '.join(word)
    if target == 'object' or target == 'subject':
        for wd in word:
            if 'NOUN' in morph.parse(wd)[0].tag:
                noun_check = True
    if noun_check == True or target == 'act':
        getting[word]=connection_id
    return(getting)

def analyze(file):
    app = App("neo4j connection")
    full_text = file
    for text in full_text:
        markup = syntax_parser(text)
        markup = markup.tokens
        for text in full_text:
            markup = syntax_parser(text)
            markup = markup.tokens
            tok_subj = 0
            tok_act = 0
            tok_obj = 0
            for tok in markup:
                if tok.rel in ['nsubj', 'obl']:
                    tok_subj = 1
                if tok.rel in ['root', 'acl']:
                    tok_act = 1
                if tok.rel in ['obj', 'nsubj:pass']:
                    tok_obj = 1
            if tok_subj == 0 or tok_act == 0 or tok_obj == 0:
                continue
            subjects_dict = node_search(markup, 'subject')
            objects_dict = node_search(markup, 'object')
            acts_dict = node_search(markup, 'act')
            if len(subjects_dict) > 1:
                for i in subjects_dict:
                    for y in acts_dict:
                        if subjects_dict[i] == acts_dict[y]:
                            for j in objects_dict:
                                if subjects_dict[i] == objects_dict[j]:
                                    query1 = "MERGE(m:Term{name:"+"'" +i+"'" +", occ:'объект'}) " \
                                                    "MERGE(s:Term{name:"+"'" +j+"'" +", occ:'объект'}) " \
                                                                                  "MERGE (m) - [:"+y +"]-> (s) "
                                    app.query(str(query1))
            else:
                subject = list(subjects_dict.keys())
                for y in acts_dict:
                    for j in objects_dict:
                        if acts_dict[y] == objects_dict[j]:
                            query1 = "MERGE(m:Term{name:" +"'" +subject[0] + "'" +", occ:'объект'}) " \
                                                                "MERGE(s:Term{name:" + "'" + j+ "'" +", occ:'объект'}) " \
                                                                                           "MERGE (m) - [:"+ y +"]-> (s) "
                            app.query(str(query1))