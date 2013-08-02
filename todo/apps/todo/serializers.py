from rest_framework import serializers
from todo.apps.todo.models import ToDo


class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = ('text', 'completed')
