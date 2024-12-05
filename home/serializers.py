from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Workspace, Board, Tag, Task, WorkspaceMembership, Notification

class WorkspaceSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'created_by', 'created_at']


class BoardSerializer(serializers.ModelSerializer):
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all())

    class Meta:
        model = Board
        fields = ['id', 'name', 'workspace','description' ,'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['workspace'] = {'id': instance.workspace.id,
        'name': instance.workspace.name,
        }
        return representation


class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMembership
        fields = ['id', 'user', 'workspace', 'role']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("Tags cannot be empty.")
        return value



class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    assigned_users = serializers.StringRelatedField(many=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date', 'deadline',
            'status', 'tags', 'board', 'assigned_users', 'created_at'
        ]

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            board = instance.board
            representation['board'] = {
                'id': board.id,
                'name': board.name,
                'workspace': {
                    'id': board.workspace.id,
                    'name': board.workspace.name,
                    }
                }
            return representation


class TaskWriteSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), write_only=True)
    assigned_users = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date', 'deadline',
            'status', 'tags', 'board', 'assigned_users'
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        assigned_users_data = validated_data.pop('assigned_users', [])
        task = Task.objects.create(**validated_data)

        # Add tags
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            task.tags.add(tag)

        # Assign users
        for user_id in assigned_users_data:
            user = get_user_model().objects.get(id=user_id)
            task.assigned_users.add(user)

        return task

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        assigned_users_data = validated_data.pop('assigned_users', [])
        instance = super().update(instance, validated_data)

        # Update tags
        instance.tags.clear()
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)

        # Update assigned users
        instance.assigned_users.clear()
        for user_id in assigned_users_data:
            user = get_user_model().objects.get(id=user_id)
            instance.assigned_users.add(user)

        return instance
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'is_read']

