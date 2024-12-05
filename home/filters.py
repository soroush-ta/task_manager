from django_filters import rest_framework as filters
from .models import Task

class TaskFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    assigned_user = filters.NumberFilter(field_name='assigned_users__id')

    class Meta:
        model = Task
        fields = ['status', 'title', 'assigned_user']
