from collections import OrderedDict
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from todo.apps.todo.models import ToDo
from todo.apps.todo.serializers import ToDoSerializer


def get_document(request):
    """
    Returns the DocJSON document for the ToDo API.
    """
    queryparams = '?' + request.GET.urlencode() if request.GET else ''
    (title, notes) = get_todo_notes(request, queryparams)

    return OrderedDict([
        ('_type', 'document'),
        ('meta', {
            'url': request.build_absolute_uri('/') + queryparams,
            'title': title
        }),
        ('tabs', {
            'all': {'_type': 'link', 'url': '/'},
            'complete': {'_type': 'link', 'url': '/?completed=true'},
            'incomplete': {'_type': 'link', 'url': '/?completed=false'}
        }),
        ('create_note', {
            '_type': 'link',
            'url': '/' + queryparams,
            'method': 'POST',
            'fields': [
                {'name': 'text', 'required': True},
                {'name': 'completed'}
            ]
        }),
        ('notes', notes)
    ])

def get_todo_notes(request, queryparams):
    """
    Returns the current ToDo items.
    """
    queryset = ToDo.objects.all()

    # Apply any filtering to the notes that should be returned.
    if 'completed' in request.GET:
        if request.GET['completed'].lower() == 'true':
            queryset = queryset.filter(completed=True)
            count = queryset.count()
            plural = '' if count == 1 else 's'
            title = 'DocJSON ToDo API (%d complete note%s)' % (count, plural)
        else:
            queryset = queryset.exclude(completed=True)
            count = queryset.count()
            plural = '' if count == 1 else 's'
            title = 'DocJSON ToDo API (%d incomplete note%s)' % (count, plural)
    else:
        count = queryset.count()
        plural = '' if count == 1 else 's'
        title = 'DocJSON ToDo API (%d note%s)' % (count, plural)

    # Return the list of notes.
    notes = [
        OrderedDict([
            ('text', item.text),
            ('completed', item.completed),
            ('edit', {
                '_type': 'link',
                'url': reverse('todo-item', kwargs={'pk': item.pk}) + queryparams,
                'method': 'PATCH',
                'fields': [{'name': 'text'}, {'name': 'completed'}]
            }),
            ('delete', {
                '_type': 'link',
                'url': reverse('todo-item', kwargs={'pk': item.pk}) + queryparams,
                'method': 'DELETE'
            })
        ]) for item in queryset
    ]

    return (title, notes)

def get_error_document(error_dict):
    message = '\n'.join([
        '%s - %s' % (field_name, ', '.join(error_list))
        for field_name, error_list in error_dict.items()
    ])

    return {
        '_type': 'document',
        'meta': {
            'error': message
        }
    }


class ToDoList(APIView):
    def post(self, request):
        """
        Create a new ToDo note.
        """
        serializer = ToDoSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(get_error_document(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(get_document(request))

    def get(self, request):
        """
        Return the DocJSON document.
        """
        return Response(get_document(request))


class ToDoItem(APIView):
    def get_instance(self, pk):
        return get_object_or_404(ToDo, pk=pk)

    def delete(self, request, pk):
        """
        Delete an existing ToDo note.
        """
        instance = self.get_instance(pk)
        instance.delete()
        return Response(get_document(request))

    def patch(self, request, pk):
        """
        Update an existing ToDo note.
        """
        instance = self.get_instance(pk)
        serializer = ToDoSerializer(instance, data=request.DATA, partial=True)
        if not serializer.is_valid():
            return Response(get_error_document(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(get_document(request))
