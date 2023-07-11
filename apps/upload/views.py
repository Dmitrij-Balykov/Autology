from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .analyzer import analyze
from .graph_app import App
from nltk.tokenize import sent_tokenize

app = App("neo4j connection")
def index(request):
    app = App("neo4j connection")
    quer = "MATCH(term:Term{occ:'объект'}) RETURN term, id(term)"
    nodes = app.query(quer)
    return render(request, 'index.html', {'nodes':nodes})

def questions(request):
    req = request.FILES["file_send"].read().decode()
    req = sent_tokenize(req)
    req[0] = req[0][1:]
    text = []
    question_pool = []
    question_id = 0
    for inds, sentence in enumerate(req):
        words = sentence.split()
        for index, word in enumerate(words):
            if word in ['он', 'она', 'оно', 'они', 'его', 'её', 'их', 'Он', 'Она', 'Оно', 'Они', 'Его', 'Её', 'Их']:
                question_id+=1
                sent = req[inds]
                question_pool.append([word, index, inds,question_id,sent])
        text.append(words)
    request.session['num_id'] = question_id
    request.session['text'] = text
    request.session['questions'] = question_pool
    return render(request, 'questions.html', {'questions':question_pool, 'text':text})

def next_step_process(request):
    text = request.session['text']
    questions = request.session['questions']
    for i in questions:
        text[i[2]][i[1]] = request.POST['text_to_repair'+str(i[3])]
    analyze(text)
    return HttpResponseRedirect(reverse('upload:index'))


def node_info(request, node_name):
    try:
        quer_node_name = "MATCH(term:Term{name:'"+node_name+"'})  RETURN term"
        one_node = app.query(quer_node_name)
        one_node = one_node[0]
        quer_connected_nodes_subj = "MATCH(subject:Term{name:'" + node_name + "'}) MATCH  \
        (subject)-[connection]->(object)  RETURN  object as obj,  type(connection) as type"
        quer_connection_type_subj= "MATCH(subject:Term{name:'" + node_name + "'}) MATCH  \
        (subject)-[connection]->(object) RETURN DISTINCT type(connection) as type"
        quer_connected_nodes_obj = "MATCH(object:Term{name:'" + node_name + "'}) MATCH \
        (subject)-[connection]->(object)  RETURN  subject as subj,  type(connection) as type"
        quer_connection_type_obj = "MATCH(object:Term{name:'" + node_name + "'}) MATCH \
        (subject)-[connection]->(object) RETURN DISTINCT type(connection) as type"
        con_connected_nodes_subj = app.query(quer_connected_nodes_subj)
        con_connection_type_subj = app.query(quer_connection_type_subj)
        con_connected_nodes_obj = app.query(quer_connected_nodes_obj)
        con_connection_type_obj = app.query(quer_connection_type_obj)
    except:
        raise Http404('Нет файла')
    return render(request, 'node_info.html', {'one_node':one_node, 'con_connected_nodes_subj':con_connected_nodes_subj,
                  'con_connection_type_subj':con_connection_type_subj,'con_connected_nodes_obj':con_connected_nodes_obj,
                                              'con_connection_type_obj': con_connection_type_obj})

def new_nodes(request):
    app = App("neo4j connection")
    subj = request.POST['subject']
    act = request.POST['act']
    obj = request.POST['object']
    quer = "MERGE(m:Term{name:" +"'" +subj + "'" +", occ:'объект'}) " \
                                                            "MERGE(s:Term{name:" + "'" + obj+ "'" +", occ:'объект'}) " \
                                                                                       "MERGE (m) - [:"+ act +"]-> (s) "
    app.query(str(quer))
    return HttpResponseRedirect(reverse('upload:index'))

def delete_node(request):
    node = request.POST['to_del']
    quer = "MATCH(term:Term{name:'" + node + "'})  DETACH DELETE term"
    app.query(str(quer))
    return HttpResponseRedirect(reverse('upload:index'))

def delete_all(request):
    quer = "MATCH (term) DETACH DELETE term"
    app.query(str(quer))
    return HttpResponseRedirect(reverse('upload:index'))
