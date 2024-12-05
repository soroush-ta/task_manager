from rest_framework.permissions import BasePermission
from .models import Workspace
from django.shortcuts import get_object_or_404

class IsWorkspaceMember(BasePermission):

    message = "You do not have permission to access this workspace."
    def has_permission(self, request, view):
        workspace_pk = view.kwargs.get('workspace_pk')
        if not workspace_pk:
            return False
        
        workspace = get_object_or_404(Workspace, id=workspace_pk)
        return workspace.memberships.filter(user=request.user).exists()
    

class IsWorkspaceCreator(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
