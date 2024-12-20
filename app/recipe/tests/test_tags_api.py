from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """Return the url for the tag detail view."""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email = 'user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        user2 = create_user(email='other@example.com')

        Tag.objects.create(user=user2, name='Fruity')
        tags = Tag.objects.create(user=self.user, name='Comfort food')
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        self.assertEqual(res.data[0]['name'], tags.name)
        self.assertEqual(res.data[0]['id'], tags.id)

    def test_update_tag(self):
        """Test that the authenticated user can update a tag."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        payload = {'name': 'Veggie'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test that the authenticated user can delete a tag."""
        tag = Tag.objects.create(user=self.user, name='Vegan')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())




