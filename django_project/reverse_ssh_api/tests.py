from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.status import *
from rest_framework.test import APITestCase, APIClient
from reverse_ssh_api.models import *

# ==============================================================================
# Custom Test Case
# ==============================================================================
class ReverseSSHAPITestCase(APITestCase):
    # ==============================================================================
    # Default setUp
    def setUp(self):
        # Create user and superuser
        self.superuser1 = User.objects.create_superuser(username='superuser1', password='superuser')
        self.superuser2 = User.objects.create_superuser(username='superuser2', password='superuser')
        self.token_superuser1, _ = Token.objects.get_or_create(user=self.superuser1)
        self.token_superuser2, _ = Token.objects.get_or_create(user=self.superuser2)
        self.user1 = User.objects.create_user(username='user1', password='user')
        self.user2 = User.objects.create_user(username='user2', password='user')
        self.token_user1, _ = Token.objects.get_or_create(user=self.user1)
        self.token_user2, _ = Token.objects.get_or_create(user=self.user2)

        # urls
        self.reserved_port_url = '/api/reserved-port/'
        self.used_port_url = '/api/used-port/'
        self.free_port_url = '/api/free-port/'

        # format    
        self.format = 'json'
    # ==============================================================================
    # Client
    def _client_get(self, url:str, token:Token=None, format:str='json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.get(url, format=format)
        return response

    def _client_post(self, url:str, request_data, token:Token=None, format:str='json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.post(url, request_data, format=format)
        return response

    def _client_delete(self, url:str, token:Token=None, format:str='json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.delete(url, format=format)
        return response

    def _client_put(self, url:str, request_data, token:Token=None, format:str='json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.put(url, request_data, format=format)
        return response
    # ==============================================================================
    # Assert response
    def _assert_response(self, response, expected_status_code, expected_data=None, expected_data_len:int=None, expected_error_code:dict=None, count_function=None, expected_count:int=None):
        if expected_data is not None:
            self.assertEqual(response.data, expected_data)
        if expected_data_len is not None:
            self.assertEqual(len(response.data), expected_data_len)
        if expected_status_code is not None:
            self.assertEqual(response.status_code, expected_status_code)
        if expected_error_code is not None:
            for key in expected_error_code:
                self.assertIn(key, response.data)
                if type(expected_error_code[key]) is list:
                    self.assertEqual(type(response.data[key]), list)
                    response_error_code = set([data.code for data in response.data[key]])
                    expected_error_code_set = set(expected_error_code[key])
                    self.assertSetEqual(response_error_code, expected_error_code_set)
                elif type(expected_error_code[key]) is str:
                    self.assertEqual(type(response.data[key].code), str)
                    self.assertEqual(response.data[key].code, expected_error_code[key])
        if count_function is not None and expected_count is not None:
            self.assertEqual(count_function(), expected_count)
    # ==============================================================================
    # Test
    def _test_get(self, url:str, token:Token=None, expected_status_code:int=HTTP_200_OK, expected_data=None, expected_data_len:int=None, expected_error_code:dict=None, count_function=None, expected_count:int=None):
        response = self._client_get(url, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code, count_function, expected_count)

    def _test_post(self, url:str, request_data, token:Token=None, expected_status_code:int=HTTP_201_CREATED, expected_data=None, expected_data_len:int=None, expected_error_code:dict=None, count_function=None, expected_count:int=None):
        response = self._client_post(url, request_data, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code, count_function, expected_count)

    def _test_delete(self, url:str, token:Token=None, expected_status_code:int=HTTP_204_NO_CONTENT, expected_data=None, expected_data_len:int=None, expected_error_code:dict=None, count_function=None, expected_count:int=None):
        response = self._client_delete(url, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code, count_function, expected_count)

    def _test_update(self, url:str, request_data, token:Token=None, expected_status_code:int=HTTP_200_OK, expected_data=None, expected_data_len:int=None, expected_error_code:dict=None, count_function=None, expected_count:int=None):
        response = self._client_put(url, request_data, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code, count_function, expected_count)
# ====================================================================================================
# Reserved Port Tests
# - GET /api/reserved-ports/
# - POST /api/reserved-ports/
# - DELETE /api/reserved-ports/<pk>/
# ====================================================================================================
class ReservedPortTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        # Reserved port count
        self.reserved_port_count = ReservedPort.objects.count()

    # ====================================================================================================
    # Authentication Tests
    # - Only superuser can access the reserved port API
    # ====================================================================================================
    # 1. Superuser
    def test_superuser_get_reservedport(self):
        self._test_get(self.reserved_port_url, self.token_superuser1, HTTP_200_OK, [], 0, None, ReservedPort.objects.count, 0)

    def test_superuser_post_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_get(self.reserved_port_url, self.token_superuser1, HTTP_200_OK, [data], 1, None, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_delete_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', self.token_superuser1, HTTP_204_NO_CONTENT, None, None, None, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_update_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
        data = {'reserved_port': 10001}
        self._test_update(self.reserved_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
    # ====================================================================================================
    # 2. User
    def test_user_get_reservedport(self):
        self._test_get(self.reserved_port_url, self.token_user1, HTTP_403_FORBIDDEN, None, None, {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count)   

    def test_user_post_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_user1, HTTP_403_FORBIDDEN, None, None, {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_delete_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', self.token_user1, HTTP_403_FORBIDDEN, None, None, {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_user_update_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
        data = {'reserved_port': 10001}
        self._test_update(self.reserved_port_url + '10000/', data, self.token_user1, HTTP_403_FORBIDDEN, None, None, {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count + 1)
    # ====================================================================================================
    # 3. Anonymous
    def test_anonymous_get_reservedport(self):
        self._test_get(self.reserved_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_post_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)
        
    def test_anonymous_delete_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count + 1)
    # ====================================================================================================
    # Syntax Tests
    # - User can't post a reserved port that is already reserved
    # - User can't post used port that is not an integer (char, float, etc.)
    # - User can't post used port that is not null
    # ====================================================================================================
    def test_superuser_post_reservedport_already_reserved(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None, {'reserved_port': ['unique']}, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_post_reservedport_not_integer_char(self):
        data = {'reserved_port': 'test'}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None, {'reserved_port': ['invalid']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_post_reservedport_not_integer_float(self):
        data = {'reserved_port': 1024.5}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None, {'reserved_port': ['invalid']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_post_reservedport_not_integer_float(self):
        data = {}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None, {'reserved_port': ['required']}, ReservedPort.objects.count, self.reserved_port_count)
    # ====================================================================================================
    # Boundary Tests
    # - reserved_port must be between 1024 and 65535
    # ====================================================================================================
    def test_post_reservedport_boundary_lower_than_min_value(self):
        data = {'reserved_port': 1023}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None, {'reserved_port': ['min_value']}, ReservedPort.objects.count, self.reserved_port_count)
    
    def test_post_reservedport_boundary_equal_to_min_value(self):
        data = {'reserved_port': 1024}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_greater_than_min_value(self):
        data = {'reserved_port': 1025}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_lower_than_max_value(self):
        data = {'reserved_port': 65534}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_equal_to_max_value(self):
        data = {'reserved_port': 65535}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_greater_than_max_value(self):
        data = {'reserved_port': 65536}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None, {'reserved_port': ['max_value']}, ReservedPort.objects.count, self.reserved_port_count)
# ====================================================================================================
# Used Ports Tests
# - GET /api/v1/used-ports/
# - POST /api/v1/used-ports/
# - DELETE /api/v1/used-ports/<pk>/
# ====================================================================================================
class UsedPortTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        # Setup Used Ports database
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        self.data_list = [{'reserved_port': 10000}, {'reserved_port': 10001}, {'reserved_port': 10002}]
        for data in self.data_list:
            self._client_post(self.reserved_port_url, data, self.token_superuser1)
        self.assertEqual(ReservedPort.objects.count(), len(self.data_list))

        data = {'used_port': 10000}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, UsedPort.objects.count, 1)

        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None, UsedPort.objects.count, 2)

        self.reserved_port_count = ReservedPort.objects.count()
        self.used_port_count = UsedPort.objects.count()
    # ====================================================================================================
    # Authentication Tests
    # - Superuser can get, post, and delete any used port
    # - User can get, post, and delete own used ports
    # - Anonymous user cannot get, post, or delete used ports
    # - All Users cannot update used ports
    # ====================================================================================================
    # 1. Superuser
    def test_superuser_get_usedport(self):
        self._test_get(self.used_port_url, self.token_superuser1, HTTP_200_OK, None, self.used_port_count, None, UsedPort.objects.count, self.used_port_count)

    def test_superuser_post_usedport(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, UsedPort.objects.count, self.used_port_count + 1)
        self._test_get(self.used_port_url, self.token_superuser1, HTTP_200_OK, None, self.used_port_count + 1, None, UsedPort.objects.count, self.used_port_count + 1)

    def test_superuser_delete_own_usedport(self):
        self._test_delete(self.used_port_url + '10000/', self.token_superuser1, HTTP_204_NO_CONTENT, None, None, None, UsedPort.objects.count, self.used_port_count - 1)

    def test_superuser_delete_other_user_usedport(self):
        self._test_delete(self.used_port_url + '10000/', self.token_superuser2, HTTP_204_NO_CONTENT, None, None, None, UsedPort.objects.count, self.used_port_count - 1)

    def test_superuser_update_own_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    def test_superuser_update_other_user_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, self.token_superuser2, HTTP_405_METHOD_NOT_ALLOWED, None, None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)
    # ====================================================================================================
    # 2. User
    def test_user_get_userport(self):
        self._test_get(self.used_port_url, self.token_user1, HTTP_200_OK, None, 1, None, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None, UsedPort.objects.count, self.used_port_count + 1)
        self._test_get(self.used_port_url, self.token_user1, HTTP_200_OK, None, 2, None, UsedPort.objects.count, self.used_port_count + 1)

    def test_user_delete_own_userport(self):
        self._test_delete(self.used_port_url + '10001/', self.token_user1, HTTP_204_NO_CONTENT, None, None, None, UsedPort.objects.count, self.used_port_count - 1)

    def test_user_delete_other_user_usedport(self):
        self._test_delete(self.used_port_url + '10001/', self.token_user2, HTTP_403_FORBIDDEN, None, None, {'detail': 'permission_denied'}, UsedPort.objects.count, self.used_port_count)

    def test_user_update_own_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10001/', data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    def test_user_update_other_user_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10001/', data, self.token_user2, HTTP_403_FORBIDDEN, None, None, {'detail': 'permission_denied'}, UsedPort.objects.count, self.used_port_count)
    # ====================================================================================================
    # 3. Anonymous
    def test_anonymous_get_usedport(self):
        self._test_get(self.used_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    def test_anonymous_post_usedport(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    def test_anonymous_delete_usedport(self):
        self._test_delete(self.used_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    def test_anonymous_update_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)
    # ====================================================================================================
    # Syntax Tests
    # - User can't post used port that is not reserved
    # - User can't post used port that is already used
    # - User can't post used port that is not an integer
    # - User can't post used port that is not null
    # ==================================================================================================== 
    def test_user_post_usedport_not_reserved(self):
        data = {'used_port': 10003}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None, {'used_port': ['does_not_exist']}, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport_already_used(self):
        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None, {'used_port': ['unique']}, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport_not_integer_char(self):
        data = {'used_port': 'test'}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None, {'used_port': ['incorrect_type']}, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport_not_integer_float(self):
        data = {'used_port': 10001.5}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None, {'used_port': ['invalid']}, UsedPort.objects.count, self.used_port_count)
    
    def test_user_post_usedport_not_integer_float(self):
        data = {}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None, {'used_port': ['required']}, UsedPort.objects.count, self.used_port_count)
# ====================================================================================================
# Free Ports Tests
# - GET /api/v1/free-ports/
# ====================================================================================================
class FreePortTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        # Setup Used Ports database
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        self.data_list = [{'reserved_port': 10000}, {'reserved_port': 10001}, {'reserved_port': 10002}]
        for data in self.data_list:
            self._client_post(self.reserved_port_url, data, self.token_superuser1)
        self.assertEqual(ReservedPort.objects.count(), len(self.data_list))

        data = {'used_port': 10000}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None, UsedPort.objects.count, 1)

        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None, UsedPort.objects.count, 2)

        self.reserved_port_count = ReservedPort.objects.count()
        self.used_port_count = UsedPort.objects.count()
        self.free_port_count = self.reserved_port_count - self.used_port_count

    # ====================================================================================================
    # Authentication Tests
    # - Superuser can get free ports
    # - User can get free ports
    # ====================================================================================================
    # 1. Superuser
    def test_superuser_get_freeport(self):
        self._test_get(self.free_port_url, self.token_superuser1, HTTP_200_OK, None, self.free_port_count, None, None, None)
    def test_superuser_post_freeport(self):
        data = {'reserved_port': 10003}
        self._test_post(self.free_port_url, data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None, {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)
    def test_superuser_delete_freeport(self):
        self._test_delete(self.free_port_url + '10000/', self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None, {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)
    # ====================================================================================================
    # 2. User
    def test_user_get_freeport(self):
        self._test_get(self.free_port_url, self.token_user1, HTTP_200_OK, None, self.free_port_count, None, None, None)
    # ====================================================================================================
    # 3. Anonymous
    def test_anonymous_get_freeport(self):
        self._test_get(self.free_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'}, None, None)