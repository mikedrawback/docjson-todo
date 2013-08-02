from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from todo.apps.todo.models import ToDo
from todo.apps.todo.serializers import ToDoSerializer


PAGINATE_BY = 5


def get_document(request):
    """
    Returns the DocJSON document for the ToDo API.
    """
    return {
        'tabs': {
            'all': {'_type': 'link', 'href': '/'},
            'complete': {'_type': 'link', 'href': '/?complete=True'},
            'incomplete': {'_type': 'link', 'href': '/?complete=False'}
        },
        'search': {
            '_type': 'form',
            'href': '/',
            'method': 'GET',
            'fields': [
                {'name': 'term', 'required': True}
            ]
        },
        'add_note': {
            '_type': 'form',
            'href': '/',
            'method': 'POST',
            'fields': [
                {'name': 'text', 'required': True},
                {'name': 'completed'}
            ]
        },
        'notes': get_todo_list(request)
    }


def get_todo_list(request, page_index=1):
    """
    Returns the DocJSON list for the requested page.
    """
    queryset = ToDo.objects.all()

    # Apply any filtering to the notes that should be returned.
    filter_kwargs = {}
    exclude_kwargs = {}
    if 'term' in request.GET:
        filter_kwargs['text__icontains'] = request.GET['term']
    if 'complete' in request.GET:
        if request.GET['complete'].lower() == 'true':
            filter_kwargs['completed'] = True
        else:
            exclude_kwargs['completed'] = True

    # Paginate the queryset.
    queryset = queryset.filter(**filter_kwargs).exclude(**exclude_kwargs)
    page = Paginator(queryset, PAGINATE_BY).page(page_index)

    # Determine the link to the next page, if applicable.
    if page.has_next():
        next_url = reverse('todo-list') + '?page=%d' % (page_index + 1)
    else:
        next_url = None

    # Return a DocJSON list.
    return {
        '_type': 'list',
        'next': next_url,
        'items': [
            {
                'text': todo.text,
                'completed': todo.completed,
                'delete': {
                    '_type': 'form',
                    'method': 'DELETE',
                    'href': reverse('todo-item', kwargs={'pk': todo.pk})
                },
                'edit': {
                    '_type': 'form',
                    'method': 'PUT',
                    'href': reverse('todo-item', kwargs={'pk': todo.pk}),
                    'fields': [{'name': 'text'}, {'name': 'completed'}]
                }
            } for todo in page.object_list
        ]
    }


class ToDoList(APIView):
    def get(self, request):
        """
        Return a paginated list of all the ToDo notes.
        """
        try:
            page_index = int(request.QUERY_PARAMS.get('page', '1'))
        except ValueError:
            page_index = 1

        return Response(get_todo_list(request, page_index))


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

    def put(self, request, pk):
        """
        Update an existing ToDo note.
        """
        instance = self.get_instance(pk)
        serializer = ToDoSerializer(instance, data=request.DATA, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(get_document(request))


class ToDoRoot(APIView):
    def post(self, request):
        """
        Create a new ToDo note.
        """
        try:
            serializer = ToDoSerializer(data=request.DATA)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(get_document(request))
        except:
            import traceback
            traceback.print_exc()

    def get(self, request):
        """
        Return the DocJSON document.
        """
        return Response(get_document(request))
