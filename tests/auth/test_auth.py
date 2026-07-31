from rest_framework.test import APITestCase, APIClient
from account.models.users import Users
from django.urls import reverse



class TestJWTAuthentication(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = 'test@test.com'
        self.phone = '12345'
        self.user = Users.objects.create_user(
            email=self.email,
            password="test",
            phone=self.phone,
        )

    #Проверка получения JWT токенов
    def test_get_jwt_tokens(self):

        body = {
            "email": self.email,
            "password": "test",
        }
        response = self.client.post(
            reverse("token_obtain_pair"),
            body,
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_password(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.email,
                "password": "wrong",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)



    def test_invalid_email(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "unknown@test.com",
                "password": "test",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_access_protected_endpoint_with_jwt_token(self):
        body = {
            "email": self.email,
            "password": "test",
        }
        response = self.client.post(
            reverse("token_obtain_pair"),
            body,
            format='json',
        )
        token = response.data["access"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"JWT {token}"
        )
        response = self.client.get(reverse("bookings-list"))

        self.assertEqual(response.status_code, 200)

    def test_access_protected_endpoint_without_jwt_token(self):
        response = self.client.get(reverse("bookings-list"))

        self.assertEqual(response.status_code, 401)

    def test_access_protected_endpoint_with_invalid_jwt_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"JWT invalid"
        )
        response = self.client.get(reverse("bookings-list"))

        self.assertEqual(response.status_code, 401)