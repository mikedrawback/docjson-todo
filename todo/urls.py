from django.conf.urls import patterns, url
from todo.apps.todo import views

urlpatterns = patterns('',
    url(r'^$', views.ToDoList.as_view(), name='todo-list'),
    url(r'^(?P<pk>\d+)/$', views.ToDoItem.as_view(), name='todo-item'),
)
