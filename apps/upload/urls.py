from django.urls import path

from . import views
app_name = 'upload'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('<str:node_name>/', views.node_info, name = 'node_info'),
    path('questions', views.questions, name = 'questions'),
    path('next_step_process', views.next_step_process, name = 'next_step_process'),
    path('new_nodes', views.new_nodes, name = 'new_nodes'),
    path('delete_node', views.delete_node, name = 'delete_node'),
    path('delete_all', views.delete_all, name = 'delete_all')

]