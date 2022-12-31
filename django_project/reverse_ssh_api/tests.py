from rest_framework.authtoken.models import Token
from rest_framework.status import *
from rest_framework.test import APITestCase
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
        self.cpu_spec_url = '/api/cpu-spec/'

        # format    
        self.format = 'json'

    # ==============================================================================
    # Client
    def _client_get(self, url: str, token: Token = None, format: str = 'json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.get(url, format=format)
        return response

    def _client_post(self, url: str, request_data, token: Token = None, format: str = 'json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.post(url, request_data, format=format)
        return response

    def _client_delete(self, url: str, token: Token = None, format: str = 'json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.delete(url, format=format)
        return response

    def _client_put(self, url: str, request_data, token: Token = None, format: str = 'json'):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.put(url, request_data, format=format)
        return response

    # ==============================================================================
    # Assert response
    def _assert_response(self, response, expected_status_code, expected_data=None, expected_data_len: int = None,
                         expected_error_code: dict = None, count_function=None, expected_count: int = None):
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
    def _test_get(self, url: str, token: Token = None, expected_status_code: int = HTTP_200_OK, expected_data=None,
                  expected_data_len: int = None, expected_error_code: dict = None, count_function=None,
                  expected_count: int = None):
        response = self._client_get(url, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code,
                              count_function, expected_count)

    def _test_post(self, url: str, request_data, token: Token = None, expected_status_code: int = HTTP_201_CREATED,
                   expected_data=None, expected_data_len: int = None, expected_error_code: dict = None,
                   count_function=None, expected_count: int = None):
        response = self._client_post(url, request_data, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code,
                              count_function, expected_count)

    def _test_delete(self, url: str, token: Token = None, expected_status_code: int = HTTP_204_NO_CONTENT,
                     expected_data=None, expected_data_len: int = None, expected_error_code: dict = None,
                     count_function=None, expected_count: int = None):
        response = self._client_delete(url, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code,
                              count_function, expected_count)

    def _test_update(self, url: str, request_data, token: Token = None, expected_status_code: int = HTTP_200_OK,
                     expected_data=None, expected_data_len: int = None, expected_error_code: dict = None,
                     count_function=None, expected_count: int = None):
        response = self._client_put(url, request_data, token)
        self._assert_response(response, expected_status_code, expected_data, expected_data_len, expected_error_code,
                              count_function, expected_count)


# ====================================================================================================
# Reserved Port Tests
# - GET /api/reserved-port/
# - POST /api/reserved-port/
# - DELETE /api/reserved-port/<pk>/
# ====================================================================================================
class ReservedPortTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        # Reserved port count
        self.reserved_port_count = ReservedPort.objects.count()

    # ====================================================================================================
    # Authentication Tests and Method Tests
    # - Only superuser can access the reserved port API
    # ====================================================================================================
    # 1. Superuser
    def test_superuser_get_reservedport(self):
        self._test_get(self.reserved_port_url, self.token_superuser1, HTTP_200_OK, [], 0, None,
                       ReservedPort.objects.count, 0)

    def test_superuser_post_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_get(self.reserved_port_url, self.token_superuser1, HTTP_200_OK, [data], 1, None,
                       ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_delete_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', self.token_superuser1, HTTP_204_NO_CONTENT, None, None,
                          None, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_update_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        data = {'reserved_port': 10001}
        self._test_update(self.reserved_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED,
                          None, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)

    # ====================================================================================================
    # 2. User
    def test_user_get_reservedport(self):
        self._test_get(self.reserved_port_url, self.token_user1, HTTP_403_FORBIDDEN, None, None,
                       {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_post_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_user1, HTTP_403_FORBIDDEN, None, None,
                        {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_delete_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', self.token_user1, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_user_update_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        data = {'reserved_port': 10001}
        self._test_update(self.reserved_port_url + '10000/', data, self.token_user1, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count + 1)

    # ====================================================================================================
    # 3. Anonymous
    def test_anonymous_get_reservedport(self):
        self._test_get(self.reserved_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'},
                       ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_post_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None,
                        {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_delete_reservedport(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count + 1)

    # ====================================================================================================
    # Syntax Tests
    # - User can't post a reserved port that is already reserved
    # - User can't post used port that is not an integer (char, float, etc.)
    # - User can't post used port that is not null
    # ====================================================================================================
    def test_superuser_post_reservedport_already_reserved(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['unique']}, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_post_reservedport_not_integer_char(self):
        data = {'reserved_port': 'test'}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['invalid']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_post_reservedport_not_integer_float(self):
        data = {'reserved_port': 1024.5}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['invalid']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_post_reservedport_not_integer_float(self):
        data = {}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['required']}, ReservedPort.objects.count, self.reserved_port_count)

    # ====================================================================================================
    # Boundary Tests
    # - reserved_port must be between 1024 and 65535
    # ====================================================================================================
    def test_post_reservedport_boundary_lower_than_min_value(self):
        data = {'reserved_port': 1023}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['min_value']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_post_reservedport_boundary_equal_to_min_value(self):
        data = {'reserved_port': 1024}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_greater_than_min_value(self):
        data = {'reserved_port': 1025}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_lower_than_max_value(self):
        data = {'reserved_port': 65534}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_equal_to_max_value(self):
        data = {'reserved_port': 65535}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_post_reservedport_boundary_greater_than_max_value(self):
        data = {'reserved_port': 65536}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['max_value']}, ReservedPort.objects.count, self.reserved_port_count)


# ====================================================================================================
# Used Port Tests
# - GET /api/v1/used-port/
# - POST /api/v1/used-port/
# - DELETE /api/v1/used-port/<pk>/
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
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 1)

        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 2)

        self.reserved_port_count = ReservedPort.objects.count()
        self.used_port_count = UsedPort.objects.count()

    # ====================================================================================================
    # Authentication Tests and Method Tests
    # - Superuser can get, post, and delete any used port
    # - User can get, post, and delete own used ports
    # - Anonymous user cannot get, post, or delete used ports
    # - All Users cannot update used ports
    # ====================================================================================================
    # 1. Superuser
    def test_superuser_get_usedport(self):
        self._test_get(self.used_port_url, self.token_superuser1, HTTP_200_OK, None, self.used_port_count, None,
                       UsedPort.objects.count, self.used_port_count)

    def test_superuser_post_usedport(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, self.used_port_count + 1)
        self._test_get(self.used_port_url, self.token_superuser1, HTTP_200_OK, None, self.used_port_count + 1, None,
                       UsedPort.objects.count, self.used_port_count + 1)

    def test_superuser_delete_own_usedport(self):
        self._test_delete(self.used_port_url + '10000/', self.token_superuser1, HTTP_204_NO_CONTENT, None, None, None,
                          UsedPort.objects.count, self.used_port_count - 1)

    def test_superuser_delete_other_user_usedport(self):
        self._test_delete(self.used_port_url + '10000/', self.token_superuser2, HTTP_204_NO_CONTENT, None, None, None,
                          UsedPort.objects.count, self.used_port_count - 1)

    def test_superuser_update_own_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    def test_superuser_update_other_user_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, self.token_superuser2, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    # ====================================================================================================
    # 2. User
    def test_user_get_userport(self):
        self._test_get(self.used_port_url, self.token_user1, HTTP_200_OK, None, 1, None, UsedPort.objects.count,
                       self.used_port_count)

    def test_user_post_usedport(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, self.used_port_count + 1)
        self._test_get(self.used_port_url, self.token_user1, HTTP_200_OK, None, 2, None, UsedPort.objects.count,
                       self.used_port_count + 1)

    def test_user_delete_own_userport(self):
        self._test_delete(self.used_port_url + '10001/', self.token_user1, HTTP_204_NO_CONTENT, None, None, None,
                          UsedPort.objects.count, self.used_port_count - 1)

    def test_user_delete_other_user_usedport(self):
        self._test_delete(self.used_port_url + '10001/', self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, UsedPort.objects.count, self.used_port_count)

    def test_user_update_own_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10001/', data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    def test_user_update_other_user_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10001/', data, self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, UsedPort.objects.count, self.used_port_count)

    # ====================================================================================================
    # 3. Anonymous
    def test_anonymous_get_usedport(self):
        self._test_get(self.used_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'},
                       UsedPort.objects.count, self.used_port_count)

    def test_anonymous_post_usedport(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None,
                        {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    def test_anonymous_delete_usedport(self):
        self._test_delete(self.used_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    def test_anonymous_update_usedport(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    # ====================================================================================================
    # Syntax Tests
    # - User can't post used port that is not reserved
    # - User can't post used port that is already used
    # - User can't post used port that is not an integer
    # - User can't post used port that is not null
    # ==================================================================================================== 
    def test_user_post_usedport_not_reserved(self):
        data = {'used_port': 10003}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['does_not_exist']}, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport_already_used(self):
        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['unique']}, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport_not_integer_char(self):
        data = {'used_port': 'test'}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['incorrect_type']}, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport_not_integer_float(self):
        data = {'used_port': 10001.5}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, UsedPort.objects.count, self.used_port_count)

    def test_user_post_usedport_not_integer_float(self):
        data = {}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['required']}, UsedPort.objects.count, self.used_port_count)


# ====================================================================================================
# Free Port Tests
# - GET /api/v1/free-port/
# ====================================================================================================
class FreePortTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        # Setup Reserved Port
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        self.data_list = [{'reserved_port': 10000}, {'reserved_port': 10001}, {'reserved_port': 10002}]
        for data in self.data_list:
            self._client_post(self.reserved_port_url, data, self.token_superuser1)
        self.assertEqual(ReservedPort.objects.count(), len(self.data_list))

        # Setup Used Port
        data = {'used_port': 10000}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 1)
        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 2)

        # Setup database count
        self.reserved_port_count = ReservedPort.objects.count()
        self.used_port_count = UsedPort.objects.count()
        self.free_port_count = self.reserved_port_count - self.used_port_count

    # ====================================================================================================
    # Authentication Tests and Method Tests
    # - Superuser can get free ports
    # - User can get free ports
    # ====================================================================================================
    # 1. Superuser
    def test_superuser_get_freeport(self):
        self._test_get(self.free_port_url, self.token_superuser1, HTTP_200_OK, None, self.free_port_count, None, None,
                       None)

    def test_superuser_post_freeport(self):
        data = {'reserved_port': 10003}
        self._test_post(self.free_port_url, data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                        {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_delete_freeport(self):
        self._test_delete(self.free_port_url + '10000/', self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_update_freeport(self):
        data = {'reserved_port': 10003}
        self._test_update(self.free_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    # ====================================================================================================
    # 2. User
    def test_user_get_freeport(self):
        self._test_get(self.free_port_url, self.token_user1, HTTP_200_OK, None, self.free_port_count, None, None, None)

    def test_user_post_freeport(self):
        data = {'reserved_port': 10003}
        self._test_post(self.free_port_url, data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                        {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_delete_freeport(self):
        self._test_delete(self.free_port_url + '10000/', self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_update_freeport(self):
        data = {'reserved_port': 10003}
        self._test_update(self.free_port_url + '10000/', data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    # ====================================================================================================
    # 3. Anonymous
    def test_anonymous_get_freeport(self):
        self._test_get(self.free_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'},
                       None, None)

    def test_anonymous_post_freeport(self):
        data = {'reserved_port': 10003}
        self._test_post(self.free_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None,
                        {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_delete_freeport(self):
        self._test_delete(self.free_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_update_freeport(self):
        data = {'reserved_port': 10003}
        self._test_update(self.free_port_url + '10000/', data, None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)


# ====================================================================================================
# CPU Spec Tests
# - GET /api/v1/cpu-spec/
# - POST /api/v1/cpu-spec/
# ====================================================================================================
class CPUSpecTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        # Setup Reserved Port
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_superuser1.key)
        self.data_list = [{'reserved_port': 10000}, {'reserved_port': 10001}, {'reserved_port': 10002},
                          {'reserved_port': 10003}, {'reserved_port': 10004}]
        for data in self.data_list:
            self._client_post(self.reserved_port_url, data, self.token_superuser1)
        self.assertEqual(ReservedPort.objects.count(), len(self.data_list))

        # Setup Used Port
        data = {'used_port': 10000}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 1)
        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 2)
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 3)
        data = {'used_port': 10003}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, 4)

        # Setup CPU Stat
        self.data = {}
        self.data['superuser'] = []
        data = {
            'used_port': 10000, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actural_friendly': 2903998000}
        expected_data = data.copy()
        expected_data['id'] = 1
        self._test_post(self.cpu_spec_url, data, self.token_superuser1, HTTP_201_CREATED, expected_data, None, None,
                        CPUSpec.objects.count, 1)
        self.data['superuser'].append(expected_data)
        self.data['user1'] = []
        data = {
            'used_port': 10002, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 2
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, expected_data, None, None,
                        CPUSpec.objects.count, 2)
        self.data['user1'].append(expected_data)
        self.data['superuser'].append(expected_data)

        # Setup database count
        self.reserved_port_count = ReservedPort.objects.count()
        self.used_port_count = UsedPort.objects.count()
        self.free_port_count = self.reserved_port_count - self.used_port_count
        self.cpu_spec_count = CPUSpec.objects.count()

    # ====================================================================================================
    # Authentication Tests and Methods Tests
    # - Superuser can get, post all cpu spec
    # - User can get, post their own cpu spec
    # - Anonymous can not get, post cpu spec
    # - Any user can not update, delete cpu spec
    # ====================================================================================================
    # 1. Superuser
    def test_superuser_get_cpuspec(self):
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_post_cpuspec(self):
        data = {
            'used_port': 10001, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_superuser1, HTTP_201_CREATED, expected_data, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'] + [expected_data],
                       len(self.data['superuser']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_superuser_delete_own_cpuspec(self):
        self._test_delete(self.cpu_spec_url + '1/', self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_delete_other_cpuspec(self):
        self._test_delete(self.cpu_spec_url + '1/', self.token_superuser2, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_update_own_cpuspec(self):
        data = {
            'used_port': 10000, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_update(self.cpu_spec_url + '1/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_update_other_cpuspec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_update(self.cpu_spec_url + '1/', data, self.token_superuser2, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # 2. User
    def test_user_get_cpuspec(self):
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_post_cpuspec(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actural_friendly': 2903998000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, expected_data, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_delete_own_cpuspec(self):
        self._test_delete(self.cpu_spec_url + '2/', self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_delete_other_cpuspec(self):
        self._test_delete(self.cpu_spec_url + '2/', self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_update_own_cpuspec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actural_friendly': 2903998000}
        self._test_update(self.cpu_spec_url + '2/', data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_update_other_cpuspec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actural_friendly': 2903998000}
        self._test_update(self.cpu_spec_url + '2/', data, self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # 3. Anonymous
    def test_anonymous_get_cpuspec(self):
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    def test_anonymous_post_cpuspec(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actural_friendly': 2903998000}
        self._test_post(self.cpu_spec_url, data, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                        self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    def test_anonymous_delete_cpuspec(self):
        self._test_delete(self.cpu_spec_url + '2/', None, HTTP_401_UNAUTHORIZED, None, None, None,
                          CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    def test_anonymous_update_cpuspec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actural_friendly': 2903998000}
        self._test_update(self.cpu_spec_url + '2/', data, None, HTTP_401_UNAUTHORIZED, None, None, None,
                          CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    # ====================================================================================================
    # Syntax Tests
    # - User can't create a CPUSpec with a used_port that is already in use
    # - User can't create a CPUSpec with a used_port that is not a valid port number
    # - User can't create a CPUSpec with a cpu_bits that is not a integer
    # - User can't create a CPUSpec with a cpu_count that is not a integer
    # - User can't create a CPUSpec with a cpu_hz_actural_friendly that is not a integer
    # ====================================================================================================
    def test_user_create_cpuspec_with_used_port_already_in_use(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['unique']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_used_port_not_valid_0(self):
        data = {
            'used_port': 9999, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_used_port_not_valid_1(self):
        data = {
            'used_port': 65536, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_cpu_bits_float(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 32.5, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_bits': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_cpu_count_not_integer(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 'test',
            'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_cpu_hz_actural_friendly_not_integer(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 'test'}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_hz_actural_friendly': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # Boundary Tests
    # - cpu_bits must be 32 or 64
    # - cpu_count must be between 1 and 129
    # - cpu_hz_actural_friendly must be equal to or greater than 0
    # ====================================================================================================
    def test_user_create_cpuspec_with_cpu_bits_not_32_or_64(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 128, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_bits': ['value_not_in_list']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_cpu_count_less_than_1(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 0, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['min_value']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_cpu_count_equal_to_1(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 1, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_cpuspec_with_cpu_count_greater_than_1(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 2, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_cpuspec_with_cpu_count_less_than_128(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 127, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_cpuspec_with_cpu_count_equal_to_128(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 128, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_cpuspec_with_cpu_count_greater_than_128(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 129, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['max_value']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_cpuspec_with_cpu_hz_actural_friendly_less_than_0(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actural_friendly': -1}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_hz_actural_friendly': ['min_value']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)
