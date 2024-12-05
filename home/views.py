from rest_framework import viewsets, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Workspace, Board, Tag, Task, WorkspaceMembership, Notification
from rest_framework.exceptions import PermissionDenied
from .serializers import WorkspaceSerializer, BoardSerializer, TagSerializer, TaskSerializer,TaskWriteSerializer, WorkspaceMembershipSerializer, NotificationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from django.conf import settings
from .permissions import IsWorkspaceMember, IsWorkspaceCreator
from rest_framework.exceptions import ValidationError
from .filters import TaskFilter
from rest_framework.decorators import action



class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    queryset = Workspace.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsWorkspaceCreator()]
        return [IsAuthenticated()]


    def perform_create(self, serializer):
        workspace = serializer.save(created_by=self.request.user)

        WorkspaceMembership.objects.create(workspace=workspace, user=self.request.user, role='admin')



class WorkspaceMembershipViewSet(viewsets.ModelViewSet):
    queryset = WorkspaceMembership.objects.all()
    serializer_class = WorkspaceMembershipSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        workspace = serializer.validated_data['workspace']
        if workspace.created_by != self.request.user:
            raise serializers.ValidationError("You don't have permission to add members to this workspace.")

        serializer.save()


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_pk')
        workspace = get_object_or_404(Workspace, id=workspace_id)

        return Board.objects.filter(workspace=workspace)

    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_pk')
        workspace = Workspace.objects.get(id=workspace_id)

        serializer.save(workspace=workspace)



class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'deadline', 'status']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskWriteSerializer
        return TaskSerializer

    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_pk')
        board_id = self.kwargs.get('board_pk')

        workspace = get_object_or_404(Workspace, id=workspace_id)

        if not workspace.memberships.filter(user=self.request.user).exists():
            raise PermissionDenied("You do not have permission to view tasks in this workspace.")

        return Task.objects.filter(board__id=board_id, board__workspace=workspace)

    def perform_create(self, serializer):
        board_pk = self.kwargs['board_pk']
        board = get_object_or_404(Board, id=board_pk)

        assigned_users_data = serializer.validated_data.get('assigned_users', [])
        for user_id in assigned_users_data:
            if not WorkspaceMembership.objects.filter(workspace=board.workspace, user_id=user_id).exists():
                raise ValidationError({"detail": f"User with id {user_id} is not a member of the workspace."})

        serializer.save(board=board)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)






