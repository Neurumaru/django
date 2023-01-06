from typing import Type, List, TypeVar

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.test import APITestCase
from reverse_ssh_api.models import *
from django.db.models import Model


T = TypeVar('T', bound=Type[Model])

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
    def _client_get(self, url: str, token: Token = None, format: str = 'json') -> Response:
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.get(url, format=format)
        return response

    def _client_post(self, url: str, request_data, token: Token = None, format: str = 'json') -> Response:
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.post(url, request_data, format=format)
        return response

    def _client_delete(self, url: str, token: Token = None, format: str = 'json') -> Response:
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.delete(url, format=format)
        return response

    def _client_put(self, url: str, request_data, token: Token = None, format: str = 'json') -> Response:
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.put(url, request_data, format=format)
        return response

    # ==============================================================================
    # Assert response
    def _assert_response(self, response, expected_status_code, expected_data=None, expected_data_len: int = None,
                         expected_error_code: dict = None, count_function=None, expected_count: int = None) -> None:
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
    # - Superuser can get, post, and delete ReservedPort
    # ====================================================================================================
    # Superuser
    def test_superuser_get_ReservedPort(self):
        self._test_get(self.reserved_port_url, self.token_superuser1, HTTP_200_OK, [], 0, None,
                       ReservedPort.objects.count, 0)

    def test_superuser_post_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_get(self.reserved_port_url, self.token_superuser1, HTTP_200_OK, [data], 1, None,
                       ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_delete_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', self.token_superuser1, HTTP_204_NO_CONTENT, None, None,
                          None, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_fail_to_update_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        data = {'reserved_port': 10001}
        self._test_update(self.reserved_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED,
                          None, None, None, ReservedPort.objects.count, self.reserved_port_count + 1)

    # ====================================================================================================
    # User
    def test_user_fail_to_get_ReservedPort(self):
        self._test_get(self.reserved_port_url, self.token_user1, HTTP_403_FORBIDDEN, None, None,
                       {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_fail_to_post_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_user1, HTTP_403_FORBIDDEN, None, None,
                        {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_fail_to_delete_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', self.token_user1, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_user_fail_to_update_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        data = {'reserved_port': 10001}
        self._test_update(self.reserved_port_url + '10000/', data, self.token_user1, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, ReservedPort.objects.count, self.reserved_port_count + 1)

    # ====================================================================================================
    # Anonymous
    def test_anonymous_fail_to_get_ReservedPort(self):
        self._test_get(self.reserved_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'},
                       ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_fail_to_post_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None,
                        {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_fail_to_delete_ReservedPort(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_delete(self.reserved_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count + 1)

    # ====================================================================================================
    # Syntax Tests
    # - reserved_port
    #   - It's not already used
    #   - It's an integer (not char, float, etc.)
    #   - It's not null
    # ====================================================================================================
    # reserved_port
    def test_superuser_fail_to_post_ReservedPort_with_reserved_port_already_used(self):
        data = {'reserved_port': 10000}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['unique']}, ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_fail_to_post_ReservedPort_with_reserved_port_string(self):
        data = {'reserved_port': 'test'}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['invalid']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_fail_to_post_ReservedPort_with_reserved_port_float(self):
        data = {'reserved_port': 1024.5}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['invalid']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_fail_to_post_ReservedPort_with_reserved_port_none(self):
        data = {}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['required']}, ReservedPort.objects.count, self.reserved_port_count)

    # ====================================================================================================
    # Boundary Tests
    # - reserved_port: between 1024 and 65535
    # ====================================================================================================
    # reserved_port
    def test_superuser_fail_to_post_ReservedPort_with_reserved_port_lower_than_min_value(self):
        data = {'reserved_port': 1023}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['min_value']}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_post_ReservedPort_with_reserved_port_equal_to_min_value(self):
        data = {'reserved_port': 1024}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_post_ReservedPort_with_reserved_port_greater_than_min_value(self):
        data = {'reserved_port': 1025}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_post_rReservedPort_with_reserved_port_lower_than_max_value(self):
        data = {'reserved_port': 65534}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_post_ReservedPort_with_reserved_port_equal_to_max_value(self):
        data = {'reserved_port': 65535}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        ReservedPort.objects.count, self.reserved_port_count + 1)

    def test_superuser_fail_to_post_ReservedPort_with_reserved_port_greater_than_max_value(self):
        data = {'reserved_port': 65536}
        self._test_post(self.reserved_port_url, data, self.token_superuser1, HTTP_400_BAD_REQUEST, None, None,
                        {'reserved_port': ['max_value']}, ReservedPort.objects.count, self.reserved_port_count)

    # ====================================================================================================


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
    # - Superuser can get, post, and delete all UsedPort
    # - User can get, post, and delete own UsedPort
    # ====================================================================================================
    # Superuser
    def test_superuser_get_UsedPort(self):
        self._test_get(self.used_port_url, self.token_superuser1, HTTP_200_OK, None, self.used_port_count, None,
                       UsedPort.objects.count, self.used_port_count)

    def test_superuser_post_UsedPort(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, self.token_superuser1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, self.used_port_count + 1)
        self._test_get(self.used_port_url, self.token_superuser1, HTTP_200_OK, None, self.used_port_count + 1, None,
                       UsedPort.objects.count, self.used_port_count + 1)

    def test_superuser_delete_own_UsedPort(self):
        self._test_delete(self.used_port_url + '10000/', self.token_superuser1, HTTP_204_NO_CONTENT, None, None, None,
                          UsedPort.objects.count, self.used_port_count - 1)

    def test_superuser_delete_other_user_UsedPort(self):
        self._test_delete(self.used_port_url + '10000/', self.token_superuser2, HTTP_204_NO_CONTENT, None, None, None,
                          UsedPort.objects.count, self.used_port_count - 1)

    def test_superuser_fail_to_update_own_UsedPort(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    def test_superuser_fail_to_update_other_user_UsedPort(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, self.token_superuser2, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    # ====================================================================================================
    # User
    def test_user_get_UsedPort(self):
        self._test_get(self.used_port_url, self.token_user1, HTTP_200_OK, None, 1, None, UsedPort.objects.count,
                       self.used_port_count)

    def test_user_post_UsedPort(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_201_CREATED, data, None, None,
                        UsedPort.objects.count, self.used_port_count + 1)
        self._test_get(self.used_port_url, self.token_user1, HTTP_200_OK, None, 2, None, UsedPort.objects.count,
                       self.used_port_count + 1)

    def test_user_delete_own_UsedPort(self):
        self._test_delete(self.used_port_url + '10001/', self.token_user1, HTTP_204_NO_CONTENT, None, None, None,
                          UsedPort.objects.count, self.used_port_count - 1)

    def test_user_fail_to_delete_other_UsedPort(self):
        self._test_delete(self.used_port_url + '10001/', self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, UsedPort.objects.count, self.used_port_count)

    def test_user_fail_to_update_own_UsedPort(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10001/', data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, UsedPort.objects.count, self.used_port_count)

    def test_user_fail_to_update_other_UsedPort(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10001/', data, self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, UsedPort.objects.count, self.used_port_count)

    # ====================================================================================================
    # Anonymous
    def test_anonymous_fail_to_get_UsedPort(self):
        self._test_get(self.used_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'},
                       UsedPort.objects.count, self.used_port_count)

    def test_anonymous_fail_to_post_UsedPort(self):
        data = {'used_port': 10002}
        self._test_post(self.used_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None,
                        {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    def test_anonymous_fail_to_delete_UsedPort(self):
        self._test_delete(self.used_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    def test_anonymous_fail_to_update_UsedPort(self):
        data = {'used_port': 10002}
        self._test_update(self.used_port_url + '10000/', data, None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, UsedPort.objects.count, self.used_port_count)

    # ====================================================================================================
    # Syntax Tests
    # - used_port
    #   - It's in reserved_port
    #   - It's not used
    #   - It's an integer (not char, float, etc.)
    #   - It's not null
    # ====================================================================================================
    # used_port
    def test_user_fail_to_post_UsedPort_with_used_port_not_in_ReservedPort(self):
        data = {'used_port': 10003}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['does_not_exist']}, UsedPort.objects.count, self.used_port_count)

    def test_user_fail_to_post_UsedPort_with_used_port_already_used(self):
        data = {'used_port': 10001}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['unique']}, UsedPort.objects.count, self.used_port_count)

    def test_user_fail_to_post_UsedPort_with_used_port_string(self):
        data = {'used_port': 'test'}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, UsedPort.objects.count, self.used_port_count)

    def test_user_fail_to_post_UsedPort_with_used_port_float(self):
        data = {'used_port': 10001.5}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, UsedPort.objects.count, self.used_port_count)

    def test_user_fail_to_post_UsedPort_with_used_port_none(self):
        data = {}
        self._test_post(self.used_port_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['required']}, UsedPort.objects.count, self.used_port_count)

    # ====================================================================================================


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
    # Superuser
    def test_superuser_get_FreePort(self):
        self._test_get(self.free_port_url, self.token_superuser1, HTTP_200_OK, None, self.free_port_count, None, None,
                       None)

    def test_superuser_fail_to_post_FreePort(self):
        data = {'free_port': 10003}
        self._test_post(self.free_port_url, data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                        {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_fail_to_delete_FreePort(self):
        self._test_delete(self.free_port_url + '10000/', self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_superuser_fail_to_update_FreePort(self):
        data = {'reserved_port': 10003}
        self._test_update(self.free_port_url + '10000/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    # ====================================================================================================
    # User
    def test_user_to_get_FreePort(self):
        self._test_get(self.free_port_url, self.token_user1, HTTP_200_OK, None, self.free_port_count, None, None, None)

    def test_user_fail_to_post_FreePort(self):
        data = {'reserved_port': 10003}
        self._test_post(self.free_port_url, data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                        {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_fail_to_delete_FreePort(self):
        self._test_delete(self.free_port_url + '10000/', self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_user_fail_to_update_FreePort(self):
        data = {'reserved_port': 10003}
        self._test_update(self.free_port_url + '10000/', data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, ReservedPort.objects.count, self.reserved_port_count)

    # ====================================================================================================
    # Anonymous
    def test_anonymous_fail_to_get_FreePort(self):
        self._test_get(self.free_port_url, None, HTTP_401_UNAUTHORIZED, None, None, {'detail': 'not_authenticated'},
                       None, None)

    def test_anonymous_fail_to_post_FreePort(self):
        data = {'reserved_port': 10003}
        self._test_post(self.free_port_url, data, None, HTTP_401_UNAUTHORIZED, None, None,
                        {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_fail_to_delete_FreePort(self):
        self._test_delete(self.free_port_url + '10000/', None, HTTP_401_UNAUTHORIZED, None, None,
                          {'detail': 'not_authenticated'}, ReservedPort.objects.count, self.reserved_port_count)

    def test_anonymous_fail_to_update_FreePort(self):
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
            'cpu_hz_actual_friendly': 2903998000}
        expected_data = data.copy()
        expected_data['id'] = 1
        self._test_post(self.cpu_spec_url, data, self.token_superuser1, HTTP_201_CREATED, expected_data, None, None,
                        CPUSpec.objects.count, 1)
        self.data['superuser'].append(expected_data)
        self.data['user1'] = []
        data = {
            'used_port': 10002, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
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
    # - Superuser can get and post all cpu spec
    # - User can get and post their own cpu spec
    # ====================================================================================================
    # Superuser
    def test_superuser_get_CPUSpec(self):
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_post_CPUSpec(self):
        data = {
            'used_port': 10001, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_superuser1, HTTP_201_CREATED, expected_data, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'] + [expected_data],
                       len(self.data['superuser']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_superuser_fail_to_delete_own_CPUSpec(self):
        self._test_delete(self.cpu_spec_url + '1/', self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_fail_to_delete_other_CPUSpec(self):
        self._test_delete(self.cpu_spec_url + '1/', self.token_superuser2, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_fail_to_update_own_CPUSpec(self):
        data = {
            'used_port': 10000, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_update(self.cpu_spec_url + '1/', data, self.token_superuser1, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_superuser_fail_to_update_other_CPUSpec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_update(self.cpu_spec_url + '1/', data, self.token_superuser2, HTTP_405_METHOD_NOT_ALLOWED, None,
                          None, {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_superuser1, HTTP_200_OK, self.data['superuser'],
                       len(self.data['superuser']), None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # User
    def test_user_get_CPUSpec(self):
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_post_CPUSpec(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actual_friendly': 2903998000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, expected_data, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_fail_to_delete_own_CPUSpec(self):
        self._test_delete(self.cpu_spec_url + '2/', self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_delete_other_CPUSpec(self):
        self._test_delete(self.cpu_spec_url + '2/', self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_update_own_CPUSpec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actual_friendly': 2903998000}
        self._test_update(self.cpu_spec_url + '2/', data, self.token_user1, HTTP_405_METHOD_NOT_ALLOWED, None, None,
                          {'detail': 'method_not_allowed'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_update_other_CPUSpec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actual_friendly': 2903998000}
        self._test_update(self.cpu_spec_url + '2/', data, self.token_user2, HTTP_403_FORBIDDEN, None, None,
                          {'detail': 'permission_denied'}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # Anonymous
    def test_anonymous_fail_to_get_CPUSpec(self):
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    def test_anonymous_fail_to_post_CPUSpec(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actual_friendly': 2903998000}
        self._test_post(self.cpu_spec_url, data, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                        self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    def test_anonymous_fail_to_delete_CPUSpec(self):
        self._test_delete(self.cpu_spec_url + '2/', None, HTTP_401_UNAUTHORIZED, None, None, None,
                          CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    def test_anonymous_fail_to_update_CPUSpec(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'X86_64', 'cpu_bits': 64, 'cpu_count': 16, 'cpu_arch_string_raw': 'x86_64',
            'cpu_vendor_id_raw': 'GenuineIntel', 'cpu_brand_raw': 'Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz',
            'cpu_hz_actual_friendly': 2903998000}
        self._test_update(self.cpu_spec_url + '2/', data, None, HTTP_401_UNAUTHORIZED, None, None, None,
                          CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, None, HTTP_401_UNAUTHORIZED, None, None, None, CPUSpec.objects.count,
                       self.cpu_spec_count)

    # ====================================================================================================
    # Syntax Tests
    # - used_port
    #   - It's in UsedPort
    #   - It's not used
    #   - It's an integer (not char, float, and etc.)
    # - cpu_bits
    #   - It's an integer (not char, float, and etc.)
    # - cpu_count
    #   - It's an integer (not char, float, and etc.)
    # - cpu_hz_actual_friendly
    #   - It's an integer (not char, float, and etc.)
    # ====================================================================================================
    # used_port
    def test_user_fail_to_create_CPUSpec_with_used_port_not_in_UsedPort(self):
        data = {
            'used_port': 9999, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_used_port_already_in_use(self):
        data = {
            'used_port': 10002, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['unique']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_used_port_string(self):
        data = {
            'used_port': 'test', 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_used_port_float(self):
        data = {
            'used_port': 10002.5, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_used_port_none(self):
        data = {
            'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'used_port': ['required']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # cpu_bits
    def test_user_fail_to_create_CPUSpec_with_cpu_bits_string(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 'test', 'cpu_count': 4,
            'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_bits': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_cpu_bits_float(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 32.5, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_bits': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_cpu_bits_none(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_bits': ['required']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # cpu_count
    def test_user_fail_to_create_CPUSpec_with_cpu_count_string(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 'test',
            'cpu_arch_string_raw': 'aarch64', 'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72',
            'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_cpu_count_float(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4.5,
            'cpu_arch_string_raw': 'aarch64', 'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72',
            'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_cpu_count_none(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64,
            'cpu_arch_string_raw': 'aarch64', 'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72',
            'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['required']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # cpu_hz_actual_friendly
    def test_user_fail_to_create_CPUSpec_with_cpu_hz_actual_friendly_string(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 'test'}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_hz_actual_friendly': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_cpu_hz_actual_friendly_float(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000.5}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_hz_actual_friendly': ['invalid']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_fail_to_create_CPUSpec_with_cpu_hz_actual_friendly_none(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72'}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_hz_actual_friendly': ['required']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # Boundary Tests
    # - cpu_bits must be 32 or 64
    # - cpu_count must be between 1 and 128
    # - cpu_hz_actual_friendly must be equal to or greater than 0
    # ====================================================================================================
    # cpu_bits
    def test_user_create_CPUSpec_with_cpu_bits_not_32_or_64(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 128, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_bits': ['value_not_in_list']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # cpu_count
    def test_user_fail_to_create_CPUSpec_with_cpu_count_less_than_1(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 0, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['min_value']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_CPUSpec_with_cpu_count_equal_to_1(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 1, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_CPUSpec_with_cpu_count_greater_than_1(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 2, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_CPUSpec_with_cpu_count_less_than_128(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 127, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_CPUSpec_with_cpu_count_equal_to_128(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 128, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_fail_to_create_CPUSpec_with_cpu_count_greater_than_128(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 129, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1800000000}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_count': ['max_value']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    # ====================================================================================================
    # cpu_hz_actual_friendly
    def test_user_fail_to_create_CPUSpec_with_cpu_hz_actual_friendly_less_than_0(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': -1}
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_400_BAD_REQUEST, None, None,
                        {'cpu_hz_actual_friendly': ['min_value']}, CPUSpec.objects.count, self.cpu_spec_count)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'], len(self.data['user1']),
                       None, CPUSpec.objects.count, self.cpu_spec_count)

    def test_user_create_CPUSpec_with_cpu_hz_actual_friendly_equal_to_0(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 0}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    def test_user_create_CPUSpec_with_cpu_hz_actual_friendly_greater_than_0(self):
        data = {
            'used_port': 10003, 'cpu_arch': 'ARM_8', 'cpu_bits': 64, 'cpu_count': 4, 'cpu_arch_string_raw': 'aarch64',
            'cpu_vendor_id_raw': 'ARM', 'cpu_brand_raw': 'Cortex-A72', 'cpu_hz_actual_friendly': 1}
        expected_data = data.copy()
        expected_data['id'] = 3
        self._test_post(self.cpu_spec_url, data, self.token_user1, HTTP_201_CREATED, None, None, None,
                        CPUSpec.objects.count, self.cpu_spec_count + 1)
        self._test_get(self.cpu_spec_url, self.token_user1, HTTP_200_OK, self.data['user1'] + [expected_data],
                       len(self.data['user1']) + 1, None, CPUSpec.objects.count, self.cpu_spec_count + 1)

    # ====================================================================================================


# ====================================================================================================
# CPU Stat Tests
# - GET /api/v1/cpu-stat/
# - PATCH /api/v1/cpu-stat/<pk>/
# ====================================================================================================
# ====================================================================================================
# Authentication Tests and Methods Tests
# - Superuser can get all cpu stat
# - User can get, update their own cpu stat
# - Anonymous can not get, post, update cpu stat
# - Any user can not delete cpu stat
# ====================================================================================================
# Superuser
# ====================================================================================================
# User
# ====================================================================================================
# Anonymous
# ====================================================================================================
# Syntax Tests
# - User can't update a CPUStat with a cpu_percent that is not a float
# ====================================================================================================
# Boundary Tests
# - cpu_percent must be between 0.0 and 100.0
# ====================================================================================================

# ====================================================================================================
# Memory Spec Tests
# - GET /api/v1/memory-spec/
# - POST /api/v1/cpu-spec/
# ====================================================================================================
# ====================================================================================================
# Authentication Tests and Methods Tests
# - Superuser can get, post all memory spec
# - User can get, post their own memory spec
# - Anonymous can not get, post memory spec
# - Any user can not update, delete memory spec
# ====================================================================================================
# Superuser
# ====================================================================================================
# User
# ====================================================================================================
# Anonymous
# ====================================================================================================
# Syntax Tests
# - User can't create a MemorySpec with a used_port that is already in use
# - User can't create a MemorySpec with a used_port that is not a valid port number
# - User can't create a MemorySpec with a memory_total that is not a big integer
# ====================================================================================================
# Boundary Tests
# ====================================================================================================


# ====================================================================================================
# Memory Stat Tests
# - GET /api/v1/memory-stat/
# - PATCH /api/v1/memory-stat/<pk>/
# ====================================================================================================
# ====================================================================================================
# Authentication Tests and Methods Tests
# ====================================================================================================
# Superuser
# ====================================================================================================
# User
# ====================================================================================================
# Anonymous
# ====================================================================================================
# Syntax Tests
# ====================================================================================================
# Boundary Tests
# ====================================================================================================


# ====================================================================================================
# GPU Spec Tests
# - GET /api/v1/gpu-spec/
# - POST /api/v1/gpu-spec/<pk>/
# ====================================================================================================
# ====================================================================================================
# Authentication Tests and Methods Tests
# ====================================================================================================
# 1. Superuser
# ====================================================================================================
# 1. User
# ====================================================================================================
# 3. Anonymous
# ====================================================================================================
# Syntax Tests
# ====================================================================================================
# Boundary Tests
# ====================================================================================================


# ====================================================================================================
# GPU Stat Tests
# - GET /api/v1/gpu-stat/
# - PATCH /api/v1/gpu-stat/<pk>/
# ====================================================================================================
# ====================================================================================================
# Authentication Tests and Methods Tests
# ====================================================================================================
# 1. Superuser
# ====================================================================================================
# 1. User
# ====================================================================================================
# 3. Anonymous
# ====================================================================================================
# Syntax Tests
# ====================================================================================================
# Boundary Tests
# ====================================================================================================
