from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import WorkspaceViewSet, BoardViewSet, TagViewSet, TaskViewSet, WorkspaceMembershipViewSet, NotificationViewSet

app_name = 'home'

router = DefaultRouter()
router.register('workspaces', WorkspaceViewSet, basename='workspace')

workspaces_router = routers.NestedDefaultRouter(router, r'workspaces', lookup='workspace')
workspaces_router.register(r'boards', BoardViewSet, basename='workspace-boards')

boards_router = routers.NestedDefaultRouter(workspaces_router, r'boards', lookup='board')
boards_router.register(r'tasks', TaskViewSet, basename='board-tasks')

router.register('notifications', NotificationViewSet, basename='notifications')

router.register('tags', TagViewSet, basename='tag')
#router.register(r'workspace-memberships', WorkspaceMembershipViewSet, basename='workspace-membership')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(workspaces_router.urls)),
    path('', include(boards_router.urls)),
]
