from django.conf.urls import patterns, url
from todo.apps.todo import views

urlpatterns = patterns('',
    url(r'^$', views.ToDoRoot.as_view(), name='todo-root'),
    url(r'^(?P<pk>\d+)/$', views.ToDoItem.as_view(), name='todo-item'),
    url(r'^list/$', views.ToDoList.as_view(), name='todo-list'),
)
