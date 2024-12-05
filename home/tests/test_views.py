from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from home.models import Workspace
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class TestWorkspaceView(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.url = reverse("home:workspace-list")

    def test_create_workspace(self):
        data = {"name": "Test Workspace"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Workspace")

    def test_retrieve_workspace_list(self):
        workspace1 = Workspace.objects.create(name="Workspace 1", created_by=self.user)
        workspace2 = Workspace.objects.create(name="Workspace 2", created_by=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]["name"], workspace1.name)
        self.assertEqual(response_data[1]["name"], workspace2.name)


    def test_retrieve_workspace_detail(self):

        workspace = Workspace.objects.create(name="Test Workspace", created_by=self.user)

        retrieve_url = reverse("home:workspace-detail", kwargs={"pk": workspace.id})

        response = self.client.get(retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], workspace.id)
        self.assertEqual(response.data["name"], workspace.name)
        self.assertEqual(response.data["created_by"], self.user.username)


    def test_update_workspace(self):

        workspace = Workspace.objects.create(name="Original Workspace", created_by=self.user)

        update_url = reverse("home:workspace-detail", kwargs={"pk": workspace.id})

        updated_data = {"name": "Updated Workspace"}

        response = self.client.patch(update_url, updated_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], updated_data["name"])

        workspace.refresh_from_db()
        self.assertEqual(workspace.name, updated_data["name"])

    
    def test_delete_workspace(self):

        workspace = Workspace.objects.create(name="Workspace to Delete", created_by=self.user)
        delete_url = reverse("home:workspace-detail", kwargs={"pk": workspace.id})

        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Workspace.objects.filter(id=workspace.id).exists())