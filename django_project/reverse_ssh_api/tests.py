from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.status import *
from rest_framework.test import APITestCase
from reverse_ssh_api.models import *


# ====================================================================================================
# Reserved Port Tests
#  - GET /api/reserved_ports/
#  - POST /api/reserved_ports/
#  - DELETE /api/reserved_ports/<pk>/
# ====================================================================================================
class ReservedPortTestCase(APITestCase):
    def setUp(self):
        # Create user and superuser
        self.user = User.objects.create_user(username='user', password='user')
        self.token_user, _ = Token.objects.get_or_create(user=self.user)
        self.superuser = User.objects.create_superuser(username='superuser', password='superuser')
        self.token_superuser, _ = Token.objects.get_or_create(user=self.superuser)

        # url and format
        self.url = '/api/reserved-port/'
        self.format = 'json'

    # ====================================================================================================
    # Authentication Tests
    #  - Only superuser can access the reserved port API
    # ====================================================================================================
    def test_superuser_get_reservedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_superuser_post_reservedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 10000}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, [data])

    def test_superuser_delete_reservedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 10000}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

        response = self.client.delete(f'{self.url}10000/', format=self.format)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(ReservedPort.objects.count(), 0)

    def test_user_get_reservedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user.key)
        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'You do not have permission to perform this action.'})

    def test_user_post_reservedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user.key)
        data = {'reserved_port': 10000}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(ReservedPort.objects.count(), 0)

    def test_user_delete_reservedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 10000}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user.key)
        response = self.client.delete(self.url + '10000/', format=self.format)

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(ReservedPort.objects.count(), 1)

    def test_anonymous_get_reservedport(self):
        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_anonymous_post_reservedport(self):
        data = {'reserved_port': 10000}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(ReservedPort.objects.count(), 0)
        
    def test_anonymous_delete_reservedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 10000}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

        self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.delete(self.url + '10000/', format=self.format)

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(ReservedPort.objects.count(), 1)

    # ====================================================================================================
    # Boundary Tests
    # - reserved_port must be between 1024 and 65535
    # ====================================================================================================
    def test_post_reservedport_boundary_lower_than_min_value(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 1023}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(ReservedPort.objects.count(), 0)
    
    def test_post_reservedport_boundary_equal_to_min_value(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 1024}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

    def test_post_reservedport_boundary_greater_than_min_value(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 1025}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

    def test_post_reservedport_boundary_lower_than_max_value(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 65534}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

    def test_post_reservedport_boundary_equal_to_max_value(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 65535}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 1)

    def test_post_reservedport_boundary_greater_than_max_value(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser.key)
        data = {'reserved_port': 65536}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(ReservedPort.objects.count(), 0)

# ====================================================================================================
# Used Ports Tests
#  - GET /api/v1/used_ports/
#  - POST /api/v1/used_ports/
#  - DELETE /api/v1/used_ports/<int:used_port>/
#  - GET /api/v1/free_ports/
# ====================================================================================================
class UsedPortTestCase(APITestCase):
    def setUp(self):
        # Create user and superuser
        self.superuser1 = User.objects.create_superuser(username='superuser1', password='superuser')
        self.superuser2 = User.objects.create_superuser(username='superuser2', password='superuser')
        self.token_superuser1, _ = Token.objects.get_or_create(user=self.superuser1)
        self.user1 = User.objects.create_user(username='user1', password='user')
        self.user2 = User.objects.create_user(username='user2', password='user')
        self.token_user1, _ = Token.objects.get_or_create(user=self.user1)
        self.token_user2, _ = Token.objects.get_or_create(user=self.user2)

        # url and format
        self.url = '/api/used-port/'
        self.format = 'json'

        # Setup Used Ports database
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        data_list = [{'reserved_port': 10000}, {'reserved_port': 10001}, {'reserved_port': 10002}, {'reserved_port': 10003}]
        for data in data_list:
            response = self.client.post('/api/reserved-port/', data, format=self.format)
            self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(ReservedPort.objects.count(), 4)

        data = {'used_port': 10000}
        response = self.client.post(self.url, data, format=self.format)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(UsedPort.objects.count(), 1)

        data = {'used_port': 10001}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user1.key)
        response = self.client.post(self.url, data, format=self.format)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(UsedPort.objects.count(), 2)

        data = {'used_port': 10003}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user2.key)
        response = self.client.post(self.url, data, format=self.format)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(UsedPort.objects.count(), 3)

        self.reservedport_count = ReservedPort.objects.count()
        self.usedport_count = UsedPort.objects.count()


    # ====================================================================================================
    # Authentication Tests
    #  - User can get, post, and delete own used ports
    #  - Superuser can get, post, and delete any used port
    #  - User and superuser can get free ports
    # ====================================================================================================
    def test_superuser_get_usedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), self.usedport_count)

    def test_superuser_post_usedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        data = {'used_port': 10002}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(UsedPort.objects.count(), self.usedport_count + 1)

        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), self.usedport_count + 1)

    def test_superuser_delete_own_usedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        response = self.client.delete(self.url + '10000/', format=self.format)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(UsedPort.objects.count(), self.usedport_count - 1)

    def test_superuser_delete_other_user_usedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        response = self.client.delete(self.url + '10001/', format=self.format)

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(UsedPort.objects.count(), self.usedport_count - 1)

    def test_user_get_userport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user1.key)
        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_post_usedport(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user1.key)
        data = {'used_port': 10002}
        response = self.client.post(self.url, data, format=self.format)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(UsedPort.objects.count(), self.usedport_count + 1)

        response = self.client.get(self.url, format=self.format)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
