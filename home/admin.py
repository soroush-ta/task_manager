from django.contrib import admin
from .models import Workspace, Board, Tag, Task, WorkspaceMembership, Notification

admin.site.register(Workspace)
admin.site.register(Board)
admin.site.register(Tag)
admin.site.register(Task)
admin.site.register(WorkspaceMembership)
admin.site.register(Notification)

