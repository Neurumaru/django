from typing import Type, List, TypeVar, Tuple, Callable, Dict

from django.forms import model_to_dict
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.test import APITestCase
from reverse_ssh_api.models import *
from django.db.models import Model
from parameterized import parameterized

from reverse_ssh_api.serializers import UsedPortAdminSerializer, UsedPortSerializer
from reverse_ssh_api.utils import map_dictionary_keys

T = TypeVar("T", bound=Type[Model])


# ==============================================================================
# Custom Test Case
# ==============================================================================
class ReverseSSHAPITestCase(APITestCase):
    # ==============================================================================
    # setUp
    def setUp(self):
        # Setup Users
        self.superuser1 = User.objects.create_superuser(username="superuser1", password="superuser")
        self.superuser2 = User.objects.create_superuser(username="superuser2", password="superuser")
        self.token_superuser1, _ = Token.objects.get_or_create(user=self.superuser1)
        self.token_superuser2, _ = Token.objects.get_or_create(user=self.superuser2)
        self.user1 = User.objects.create_user(username="user1", password="user")
        self.user2 = User.objects.create_user(username="user2", password="user")
        self.token_user1, _ = Token.objects.get_or_create(user=self.user1)
        self.token_user2, _ = Token.objects.get_or_create(user=self.user2)
        self.token = {
            "superuser1": self.token_superuser1,
            "superuser2": self.token_superuser2,
            "user1": self.token_user1,
            "user2": self.token_user2
        }

        # Setup Reserved Port
        data_list = [
            {"reserved_port": i}
            for i in [10000, 10001, 10002, 10003, 10004]
        ]
        self.reserved_port_objects = self.__create_objects_in_model(ReservedPort, data_list)

        # Setup Used Port
        data_list = [
                        {"used_port": self.reserved_port_objects[i], "user": self.superuser1}
                        for i in [0, 1]
                    ] + [
                        {"used_port": self.reserved_port_objects[i], "user": self.user1}
                        for i in [2, 3]
                    ]
        self.used_port_objects = self.__create_objects_in_model(UsedPort, data_list)

        # Setup CPU Spec
        data_list = [
            {
                "used_port": self.used_port_objects[0],
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000
            }, {
                "used_port": self.used_port_objects[2],
                "cpu_arch": "ARM_8",
                "cpu_bits": 64,
                "cpu_count": 4,
                "cpu_arch_string_raw": "aarch64",
                "cpu_vendor_id_raw": "ARM",
                "cpu_brand_raw": "Cortex-A72",
                "cpu_hz_actual_friendly": 1800000000
            },
        ]
        self.cpu_spec_objects = self.__create_objects_in_model(CPUSpec, data_list)

        # Setup CPU Stat
        data_list = [
            {"cpu_spec": self.cpu_spec_objects[i], "cpu_core": j, "cpu_percent": 0.0}
            for i in [0, 1] for j in range(self.cpu_spec_objects[i].cpu_count)
        ]
        self.cpu_stat_objects = self.__create_objects_in_model(CPUStat, data_list)

        # Setup Memory Spec
        data_list = [
            {
                "used_port": self.used_port_objects[0],
                "memory_total": 34282405888
            }, {
                "used_port": self.used_port_objects[2],
                "memory_total": 818716720
            }
        ]
        self.memory_spec_objects = self.__create_objects_in_model(MemorySpec, data_list)

        # Setup Memory Stat
        data_list = [
            {
                "memory_spec": self.memory_spec_objects[0],
                "memory_used": 9745108992,
                "memory_available": 24539418624,
                "memory_free": 24541990912,
                "swap_total": 5100273664,
                "swap_used": 2776940544,
                "swap_free": 2325467136
            }, {

                "memory_spec": self.memory_spec_objects[1],
                "memory_used": 1238990848,
                "memory_available": 6621032448,
                "memory_free": 5447192576,
                "swap_total": 0,
                "swap_used": 0,
                "swap_free": 0
            }
        ]
        self.memory_stat_objects = self.__create_objects_in_model(MemoryStat, data_list)

        # Setup GPU Spec
        data_list = [
            {
                "used_port": self.used_port_objects[0],
                "gpu_index": 0,
                "gpu_name": b"NVIDIA GeForce RTX 3080",
                "gpu_brand": b"Geforce",
                "gpu_nvml_version": b"11.515.766.02",
                "gpu_driver_version": b"517.48",
                "gpu_vbios_version": b"94.02.26.08.34",
                "gpu_multi_gpu_board": False,
                "gpu_display_mode": True,
                "gpu_display_active": True,
                "gpu_persistence_mode": True,
                "gpu_compute_mode": b"DEFAULT",
                "gpu_power_management_mode": True,
                "gpu_power_management_limit": 340000,
                "gpu_temperature_shutdown": 98,
                "gpu_temperature_slowdown": 95,
                "gpu_enforced_power_limit": 340000,
                "gpu_max_clock_info_graphics": 2100,
                "gpu_max_clock_info_sm": 2100,
                "gpu_max_clock_info_mem": 9501,
                "gpu_max_clock_info_video": 1950,
                "gpu_memory_info_total": 10737418240,
                "gpu_bar1_memory_info_total": 268435456
            }
        ]
        self.gpu_spec_objects = self.__create_objects_in_model(GPUSpec, data_list)

        # Setup GPU Stat
        data_list = [
            {
                "gpu_spec": self.gpu_spec_objects[0],
                "gpu_power_usage": 25696,
                "gpu_temperature": 31,
                "gpu_fan_speed": 0,
                "gpu_clock_info_graphics": 145,
                "gpu_clock_info_sm": 145,
                "gpu_clock_info_mem": 254,
                "gpu_clock_info_video": 555,
                "gpu_memory_info_free": 9507532800,
                "gpu_memory_info_used": 1229885440,
                "gpu_bar1_memory_info_free": 267386880,
                "gpu_bar1_memory_info_used": 1048576,
                "gpu_utilization_gpu": 5,
                "gpu_utilization_memory": 15,
                "gpu_utilization_encoder": 0,
                "gpu_utilization_decoder": 0,
            }
        ]
        self.gpu_stat_objects = self.__create_objects_in_model(GPUStat, data_list)

        # Setup database count
        self.reserved_port_count = ReservedPort.objects.count()
        self.used_port_count = UsedPort.objects.count()
        self.free_port_count = self.reserved_port_count - self.used_port_count
        self.cpu_spec_count = CPUSpec.objects.count()
        self.cpu_stat_count = CPUStat.objects.count()
        self.memory_spec_count = MemorySpec.objects.count()
        self.memory_stat_count = MemoryStat.objects.count()
        self.gpu_spec_objects = GPUSpec.objects.count()
        self.gpu_stat_objects = GPUStat.objects.count()

        # Setup urls
        self.reserved_port_url = "/api/reserved-port/"
        self.used_port_url = "/api/used-port/"
        self.free_port_url = "/api/free-port/"
        self.cpu_spec_url = "/api/cpu-spec/"
        self.cpu_stat_url = "/api/cpu-stat/"
        self.memory_spec_url = "/api/memory-spec/"
        self.memory_stat_url = "/api/memory-stat/"
        self.gpu_spec_url = "/api/gpu-spec/"
        self.gpu_stat_url = "/api/gpu-stat/"

        # Setup format
        self.format = "json"

        # Setup Data
        self.url = ""
        self.data = {
            "superuser1": [],
            "superuser2": [],
            "user1": [],
            "user2": []
        }
        self.model = Model
        self.count = 0

    # ==============================================================================
    # Methods
    @staticmethod
    def __create_objects_in_model(
            model: T,
            data_list: List[dict]
    ) -> List[T]:
        return list(map(lambda x: model.objects.create(**x), data_list))

    def _create_expected_data(
            self,
            data: dict
    ) -> dict:
        model = self.model
        expected_data = data.copy()
        if model._meta.pk.name == "id":
            expected_data["id"] = model.objects.count() + 1
        return expected_data

    # ==============================================================================
    # Client
    def _client_get(
            self,
            url: str = None,
            request_token: str = None,
            format: str = "json"
    ) -> Response:
        self.client.credentials(HTTP_AUTHORIZATION=request_token)
        response = self.client.get(
            path=url,
            format=format)
        return response

    def _client_post(
            self,
            url: str = None,
            request_data: dict = None,
            request_token: str = None,
            format: str = "json"
    ) -> Response:
        self.client.credentials(HTTP_AUTHORIZATION=request_token)
        response = self.client.post(
            path=url,
            data=request_data,
            format=format)
        return response

    def _client_delete(
            self,
            url: str = None,
            request_token: str = None,
            format: str = "json"
    ) -> Response:
        self.client.credentials(HTTP_AUTHORIZATION=request_token)
        response = self.client.delete(
            path=url,
            format=format)
        return response

    def _client_put(
            self,
            url: str = None,
            request_data: dict = None,
            request_token: str = None,
            format: str = "json"
    ) -> Response:
        self.client.credentials(HTTP_AUTHORIZATION=request_token)
        response = self.client.put(
            path=url,
            data=request_data,
            format=format)
        return response

    # ==============================================================================
    # Assert response
    def _assert_response(
            self,
            response: Response = None,
            expected_status_code: int = HTTP_200_OK,
            expected_data: dict = None,
            expected_error_code: dict = None,
            count_function: Callable = None,
            expected_count: int = None
    ) -> None:
        if expected_data is not None:
            self.assertEqual(response.data, expected_data)

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
    def __validate_parameter(
            self,
            url: str = None,
            request_id: int = None,
            request_token: str = None,
            request_data: dict = None,
            expected_status_code: int = None,
            expected_data: str = None,
            count_function: Callable = None,
            expected_count: int = None
    ) -> Tuple[str, str, dict, Callable, int]:
        if url is None:
            url = self.url

        if request_id is not None:
            url = f"{url}{request_id}/"

        tmp_request_token = request_token
        if request_token is not None:
            request_token = "Token " + self.token[request_token].key
        else:
            request_token = ""

        if expected_status_code == HTTP_200_OK:
            expected_data = self.data[tmp_request_token]
        elif expected_status_code == HTTP_201_CREATED \
                or expected_status_code == HTTP_202_ACCEPTED:
            expected_data = self._create_expected_data(request_data)

        if count_function is None:
            count_function = self.model.objects.count

        if expected_count is None:
            expected_count = self.count
            if expected_status_code == HTTP_201_CREATED:
                expected_count += 1
            elif expected_status_code == HTTP_204_NO_CONTENT:
                expected_count -= 1

        return url, request_token, expected_data, count_function, expected_count

    def _test_get(
            self,
            url: str = None,
            request_token: str = None,
            expected_status_code: int = HTTP_200_OK,
            expected_data: str = None,
            expected_error_code: dict = None
    ) -> None:
        (
            url,
            request_token,
            expected_data,
            count_function,
            expected_count
        ) = self.__validate_parameter(
            url=url,
            request_token=request_token,
            expected_status_code=expected_status_code,
            expected_data=expected_data
        )
        response = self._client_get(
            url=url,
            request_token=request_token
        )
        self._assert_response(
            response=response,
            expected_status_code=expected_status_code,
            expected_data=expected_data,
            expected_error_code=expected_error_code,
            count_function=count_function,
            expected_count=expected_count
        )

    def _test_post(
            self,
            url: str = None,
            request_data: dict = None,
            request_token: str = None,
            expected_status_code: int = HTTP_201_CREATED,
            expected_data: str = None,
            expected_error_code: dict = None
    ) -> None:
        (
            url,
            request_token,
            expected_data,
            count_function,
            expected_count
        ) = self.__validate_parameter(
            url=url,
            request_token=request_token,
            request_data=request_data,
            expected_status_code=expected_status_code,
            expected_data=expected_data
        )
        response = self._client_post(
            url=url,
            request_data=request_data,
            request_token=request_token
        )
        self._assert_response(
            response=response,
            expected_status_code=expected_status_code,
            expected_data=expected_data,
            expected_error_code=expected_error_code,
            count_function=count_function,
            expected_count=expected_count
        )

    def _test_delete(
            self, url: str = None,
            request_token: str = None,
            expected_status_code: int = HTTP_204_NO_CONTENT,
            expected_data: str = None,
            expected_error_code: dict = None,
            request_id: int = None
    ) -> None:
        (
            url,
            request_token,
            expected_data,
            count_function,
            expected_count
        ) = self.__validate_parameter(
            url=url,
            request_id=request_id,
            request_token=request_token,
            expected_status_code=expected_status_code,
            expected_data=expected_data
        )
        response = self._client_delete(
            url=url,
            request_token=request_token
        )
        self._assert_response(
            response=response,
            expected_status_code=expected_status_code,
            expected_data=expected_data,
            expected_error_code=expected_error_code,
            count_function=count_function,
            expected_count=expected_count
        )

    def _test_update(
            self,
            url: str = None,
            request_id: int = None,
            request_data: dict = None,
            request_token: str = None,
            expected_status_code: int = HTTP_200_OK,
            expected_data: str = None,
            expected_error_code: dict = None
    ) -> None:
        (
            url,
            request_token,
            expected_data,
            count_function,
            expected_count
        ) = self.__validate_parameter(
            url=url,
            request_id=request_id,
            request_token=request_token,
            request_data=request_data,
            expected_status_code=expected_status_code,
            expected_data=expected_data
        )
        response = self._client_put(
            url=url,
            request_data=request_data,
            request_token=request_token
        )
        self._assert_response(
            response=response,
            expected_status_code=expected_status_code,
            expected_data=expected_data,
            expected_error_code=expected_error_code,
            count_function=count_function,
            expected_count=expected_count
        )

    def _test(self, method: str, data: Dict[str, object]) -> None:
        if method == "GET":
            self._test_get(**data)
        elif method == "POST":
            self._test_post(**data)
        elif method == "DELETE":
            self._test_delete(**data)
        elif method == "UPDATE":
            self._test_update(**data)
        else:
            self.fail("테스트 케이스 오류")

    # ==============================================================================


# ====================================================================================================
# Reserved Port Tests
# - GET /api/reserved-port/
# - POST /api/reserved-port/
# - DELETE /api/reserved-port/<pk>/
# ====================================================================================================
class ReservedPortTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        self.url = self.reserved_port_url
        for i in [0, 1, 2, 3, 4]:
            self.data["superuser1"].append(model_to_dict(self.reserved_port_objects[i]))
        self.model = ReservedPort
        self.count = self.reserved_port_count

    # ====================================================================================================
    # Authentication Tests and Method Tests
    # - Superuser can get, post, and delete ReservedPort
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # Superuser
        # - GET
        ("allow superuser to GET", "GET", {
            "request_token": "superuser1",
            "expected_status_code": HTTP_200_OK}),
        # - POST
        ("allow superuser to POST", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_201_CREATED}),
        # - DELETE
        ("allow superuser to DELETE", "DELETE", {
            "request_id": 10000,
            "request_token": "superuser1",
            "expected_status_code": HTTP_204_NO_CONTENT}),
        # - UPDATE
        ("deny superuser to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_token": "superuser1",
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # ====================================================================================================
        # User
        # - GET
        ("deny user to GET", "GET", {
            "request_token": "user1",
            "expected_status_code": HTTP_403_FORBIDDEN,
            "expected_error_code": {"detail": "permission_denied"}}),
        # - POST
        ("deny user to POST", "POST", {
            "request_token": "user1",
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_403_FORBIDDEN,
            "expected_error_code": {"detail": "permission_denied"}}),
        # - DELETE
        ("deny user to DELETE", "DELETE", {
            "request_id": 10000,
            "request_token": "user1",
            "expected_status_code": HTTP_403_FORBIDDEN,
            "expected_error_code": {"detail": "permission_denied"}}),
        # - UPDATE
        ("deny user to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_token": "user1",
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_403_FORBIDDEN,
            "expected_error_code": {"detail": "permission_denied"}}),
        # ====================================================================================================
        # Anonymous
        # - GET
        ("deny anonymous to GET", "GET", {
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - POST
        ("deny anonymous to POST", "POST", {
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - DELETE
        ("deny anonymous to DELETE", "DELETE", {
            "request_id": 10000,
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - UPDATE
        ("deny anonymous to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # ====================================================================================================
    ])
    def test_authentication(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

    # ====================================================================================================
    # Syntax Tests
    # - reserved_port
    #   - It's not already used
    #   - It's an integer (not string, float, none etc.)
    #   - It's not null
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # reserved_port
        # - already used
        ("deny superuser to POST with reserved_port already used", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 10000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"reserved_port": ["unique"]}}),
        # - string type
        ("deny superuser to POST with reserved_port of string type", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": "test"},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"reserved_port": ["invalid"]}}),
        # - float type
        ("deny superuser to POST with reserved_port of float type", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 1024.5},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"reserved_port": ["invalid"]}}),
        # - none
        ("deny superuser to POST with reserved_port of none", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": None},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"reserved_port": ["null"]}}),
        # - null
        ("deny superuser to POST without reserved_port", "POST", {
            "request_token": "superuser1",
            "request_data": {},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"reserved_port": ["required"]}}),
        # ====================================================================================================
    ])
    def test_syntax(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

    # ====================================================================================================
    # Boundary Tests
    # - reserved_port: between 1024 and 65535
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # reserved_port
        # - min_value
        ("deny superuser to POST with reserved_port less than min value, 1023", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 1023},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"reserved_port": ["min_value"]}}),
        ("allow superuser to POST with reserved_port equal to min value, 1024", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 1024},
            "expected_status_code": HTTP_201_CREATED}),
        ("allow superuser to POST with reserved_port greater than min value, 1025", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 1025},
            "expected_status_code": HTTP_201_CREATED}),
        # - max_value
        ("allow superuser to POST with reserved_port less than max value, 65534", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 65534},
            "expected_status_code": HTTP_201_CREATED}),
        ("allow superuser to POST with reserved_port equal to max value, 65535", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 65535},
            "expected_status_code": HTTP_201_CREATED}),
        ("deny superuser to POST with reserved_port greater than max value, 65536", "POST", {
            "request_token": "superuser1",
            "request_data": {"reserved_port": 65536},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"reserved_port": ["max_value"]}}),
        # ====================================================================================================
    ])
    def test_boundary(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

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

        self.url = self.used_port_url
        for i in [0, 1, 2, 3]:
            self.data["superuser1"].append(UsedPortAdminSerializer(self.used_port_objects[i]).data)
        for i in [2, 3]:
            self.data["user1"].append(UsedPortSerializer(self.used_port_objects[i]).data)
        self.model = UsedPort
        self.count = self.used_port_count

    # ====================================================================================================
    # Authentication Tests and Method Tests
    # - Superuser can get, post, and delete all UsedPort
    # - User can get, post, and delete own UsedPort
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # Superuser
        # - GET
        ("allow superuser to GET", "GET", {
            "request_token": "superuser1",
            "expected_status_code": HTTP_200_OK}),
        # - POST
        ("allow superuser to POST", "POST", {
            "request_token": "superuser1",
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_201_CREATED}),
        # - DELETE
        ("allow superuser to DELETE own", "DELETE", {
            "request_id": 10000,
            "request_token": "superuser1",
            "expected_status_code": HTTP_204_NO_CONTENT}),
        ("allow other superuser to DELETE other's", "DELETE", {
            "request_id": 10000,
            "request_token": "superuser2",
            "expected_status_code": HTTP_204_NO_CONTENT}),
        # - UPDATE
        ("deny superuser to UPDATE own", "UPDATE", {
            "request_id": 10000,
            "request_token": "superuser1",
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        ("deny other superuser to UPDATE other's", "UPDATE", {
            "request_id": 10000,
            "request_token": "superuser2",
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # ====================================================================================================
        # User
        # - GET
        ("allow user to GET", "GET", {
            "request_token": "user1",
            "expected_status_code": HTTP_200_OK}),
        # - POST
        ("allow user to POST", "POST", {
            "request_token": "superuser1",
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_201_CREATED}),
        # - DELETE
        ("allow user to DELETE own", "DELETE", {
            "request_id": 10002,
            "request_token": "user1",
            "expected_status_code": HTTP_204_NO_CONTENT}),
        ("deny other user to DELETE other's", "DELETE", {
            "request_id": 10002,
            "request_token": "user2",
            "expected_status_code": HTTP_403_FORBIDDEN,
            "expected_error_code": {"detail": "permission_denied"}}),
        # - UPDATE
        ("deny user to UPDATE own", "UPDATE", {
            "request_id": 10002,
            "request_token": "user1",
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        ("deny other user to UPDATE other's", "UPDATE", {
            "request_id": 10002,
            "request_token": "user2",
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_403_FORBIDDEN,
            "expected_error_code": {"detail": "permission_denied"}}),
        # ====================================================================================================
        # Anonymous
        # - GET
        ("deny anonymous to GET", "GET", {
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - POST
        ("deny anonymous to POST", "POST", {
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - DELETE
        ("deny anonymous to DELETE", "DELETE", {
            "request_id": 10000,
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - UPDATE
        ("deny anonymous to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_data": {"used_port": 10004},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # ====================================================================================================
    ])
    def test_authentication(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

    # ====================================================================================================
    # Syntax Tests
    # - used_port
    #   - It's in reserved_port
    #   - It's not used
    #   - It's an integer (not string, float, none etc.)
    #   - It's not null
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # used_port
        # - not in reserved_port
        ("deny user to POST with used_port not in reserved_port", "POST", {
            "request_token": "user1",
            "request_data": {"used_port": 9999},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["does_not_exist"]}}),
        # - already used
        ("deny user to POST with used_port already used", "POST", {
            "request_token": "user1",
            "request_data": {"used_port": 10000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["unique"]}}),
        # - string type
        ("deny user to POST with used_port of string type", "POST", {
            "request_token": "user1",
            "request_data": {"used_port": "test"},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["invalid"]}}),
        # - float type
        ("deny user to POST with used_port of float type", "POST", {
            "request_token": "user1",
            "request_data": {"used_port": 10004.1},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["invalid"]}}),
        # - none
        ("deny user to POST with used_port of none", "POST", {
            "request_token": "user1",
            "request_data": {"used_port": None},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["invalid"]}}),
        # null
        ("deny user to POST without used_port", "POST", {
            "request_token": "user1",
            "request_data": {},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["required"]}}),
        # ====================================================================================================
    ])
    def test_syntax(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

    # ====================================================================================================


# ====================================================================================================
# Free Port Tests
# - GET /api/v1/free-port/
# ====================================================================================================
class FreePortTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        self.url = self.free_port_url
        data = map_dictionary_keys(model_to_dict(self.reserved_port_objects[4]), {"reserved_port": "free_port"})
        self.data["superuser1"].append(data)
        self.data["user1"].append(data)
        self.model = ReservedPort
        self.count = self.reserved_port_count

    # ====================================================================================================
    # Authentication Tests and Method Tests
    # - Superuser can get free ports
    # - User can get free ports
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # Superuser
        # - GET
        ("allow superuser to GET", "GET", {
            "request_token": "superuser1",
            "expected_status_code": HTTP_200_OK}),
        # - POST
        ("deny superuser to POST", "POST", {
            "request_token": "superuser1",
            "request_data": {"free_port": 10005},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # - DELETE
        ("deny superuser to DELETE", "DELETE", {
            "request_id": 10000,
            "request_token": "superuser1",
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # - UPDATE
        ("deny superuser to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_token": "superuser1",
            "request_data": {"free_port": 10005},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # ====================================================================================================
        # User
        # - GET
        ("allow user to GET", "GET", {
            "request_token": "user1",
            "expected_status_code": HTTP_200_OK}),
        # - POST
        ("deny user to POST", "POST", {
            "request_token": "user1",
            "request_data": {"free_port": 10005},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # - DELETE
        ("deny user to DELETE", "DELETE", {
            "request_id": 10000,
            "request_token": "user1",
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # - UPDATE
        ("deny user to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_token": "user1",
            "request_data": {"free_port": 10005},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # ====================================================================================================
        # Anonymous
        # - GET
        ("deny anonymous to GET", "GET", {
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - POST
        ("deny anonymous to POST", "POST", {
            "request_data": {"free_port": 10005},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - DELETE
        ("deny anonymous to DELETE", "DELETE", {
            "request_id": 10000,
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - UPDATE
        ("deny anonymous to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_data": {"free_port": 10005},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # ====================================================================================================
    ])
    def test_authentication(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

    # ====================================================================================================


# ====================================================================================================
# CPU Spec Tests
# - GET /api/v1/cpu-spec/
# - POST /api/v1/cpu-spec/
# ====================================================================================================
class CPUSpecTestCase(ReverseSSHAPITestCase):
    def setUp(self):
        super().setUp()

        self.url = self.cpu_spec_url
        self.data["superuser1"].append(model_to_dict(self.cpu_spec_objects[0]))
        self.data["superuser1"].append(model_to_dict(self.cpu_spec_objects[1]))
        self.data["superuser2"].append(model_to_dict(self.cpu_spec_objects[0]))
        self.data["superuser2"].append(model_to_dict(self.cpu_spec_objects[1]))
        self.data["user1"].append(model_to_dict(self.cpu_spec_objects[1]))
        self.model = CPUSpec
        self.count = self.cpu_spec_count

    # ====================================================================================================
    # Authentication Tests and Methods Tests
    # - Superuser can get and post all cpu spec
    # - User can get and post their own cpu spec
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # Superuser
        # - GET
        ("allow superuser to GET all", "GET", {
            "request_token": "superuser1",
            "expected_status_code": HTTP_200_OK}),
        ("allow other superuser to GET all", "GET", {
            "request_token": "superuser2",
            "expected_status_code": HTTP_200_OK}),
        # - POST
        ("allow superuser to POST with own used_port", "POST", {
            "request_token": "superuser1",
            "request_data": {
                "used_port": 10001,
                "cpu_arch": "ARM_8",
                "cpu_bits": 64,
                "cpu_count": 4,
                "cpu_arch_string_raw": "aarch64",
                "cpu_vendor_id_raw": "ARM",
                "cpu_brand_raw": "Cortex-A72",
                "cpu_hz_actual_friendly": 1800000000},
            "expected_status_code": HTTP_201_CREATED}),
        ("allow other superuser to POST with any used_port", "POST", {
            "request_token": "superuser2",
            "request_data": {
                "used_port": 10001,
                "cpu_arch": "ARM_8",
                "cpu_bits": 64,
                "cpu_count": 4,
                "cpu_arch_string_raw": "aarch64",
                "cpu_vendor_id_raw": "ARM",
                "cpu_brand_raw": "Cortex-A72",
                "cpu_hz_actual_friendly": 1800000000},
            "expected_status_code": HTTP_201_CREATED}),
        # - DELETE
        ("deny superuser to DELETE", "DELETE", {
            "request_id": 1,
            "request_token": "superuser1",
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # - UPDATE
        ("allow superuser to UPDATE", "UPDATE", {
            "request_id": 1,
            "request_token": "superuser1",
            "request_data": {
                "used_port": 10000,
                "cpu_arch": "ARM_8",
                "cpu_bits": 64,
                "cpu_count": 4,
                "cpu_arch_string_raw": "aarch64",
                "cpu_vendor_id_raw": "ARM",
                "cpu_brand_raw": "Cortex-A72",
                "cpu_hz_actual_friendly": 1800000000},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # ====================================================================================================
        # User
        # - GET
        ("allow user to GET with own used_port", "GET", {
            "request_token": "user1",
            "expected_status_code": HTTP_200_OK}),
        ("deny other user to GET with other's used_port", "GET", {
            "request_token": "user2",
            "expected_status_code": HTTP_200_OK}),
        # - POST
        ("allow user to POST with own used_port", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_201_CREATED}),
        ("deny other user to POST with other's used_port", "POST", {
            "request_token": "user2",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_403_FORBIDDEN,
            "expected_error_code": {"detail": "permission_denied"}}),
        # - DELETE
        ("deny user to DELETE", "DELETE", {
            "request_id": 2,
            "request_token": "user1",
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # - UPDATE
        ("deny user to UPDATE", "UPDATE", {
            "request_id": 2,
            "request_token": "user1",
            "request_data": {
                "used_port": 10002,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_405_METHOD_NOT_ALLOWED,
            "expected_error_code": {"detail": "method_not_allowed"}}),
        # ====================================================================================================
        # Anonymous
        # - GET
        ("deny anonymous to GET", "GET", {
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - POST
        ("deny anonymous to POST", "POST", {
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - DELETE
        ("deny anonymous to DELETE", "DELETE", {
            "request_id": 10000,
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # - UPDATE
        ("deny anonymous to UPDATE", "UPDATE", {
            "request_id": 10000,
            "request_data": {"reserved_port": 10005},
            "expected_status_code": HTTP_401_UNAUTHORIZED,
            "expected_error_code": {"detail": "not_authenticated"}}),
        # ====================================================================================================
    ])
    def test_authentication(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

    # ====================================================================================================
    # Syntax Tests
    # - used_port
    #   - It's in UsedPort
    #   - It's not already used
    #   - It's an integer (not string, float, none and etc.)
    #   - It's not null
    # - cpu_bits
    #   - It's an integer (not string, float, none and etc.)
    #   - It's not null
    # - cpu_count
    #   - It's an integer (not string, float, none and etc.)
    #   - It's not null
    # - cpu_hz_actual_friendly
    #   - It's an integer (not string, float, none and etc.)
    #   - It's not null
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # used_port
        # - not in UsedPort
        ("deny user to POST with used_port not in UsedPort", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 9999,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["does_not_exist"]}}),
        # - already used
        ("deny user to POST with used_port already used", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10002,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["unique"]}}),
        # - string type
        ("deny user to POST with used_port of string type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": "test",
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["invalid"]}}),
        # - float type
        ("deny user to POST with used_port of float type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003.1,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["invalid"]}}),
        # - none
        ("deny user to POST with used_port of none", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": None,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["null"]}}),
        # - null
        ("deny user to POST without used_port", "POST", {
            "request_token": "user1",
            "request_data": {
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"used_port": ["required"]}}),
        # ====================================================================================================
        # cpu_bits
        # - string type
        ("deny user to POST with cpu_bits of string type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": "test",
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_bits": ["invalid"]}}),
        # - float type
        ("deny user to POST with cpu_bits of float type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64.1,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_bits": ["invalid"]}}),
        # - none
        ("deny user to POST with cpu_bits of none", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": None,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_bits": ["null"]}}),
        ("deny user to POST without cpu_bits", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_bits": ["required"]}}),
        # ====================================================================================================
        # cpu_count
        # - string type
        ("deny user to POST without cpu_count of string type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": "test",
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_count": ["invalid"]}}),
        # - float type
        ("deny user to POST without cpu_count of float type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16.1,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_count": ["invalid"]}}),
        # - none
        ("deny user to POST with cpu_count of none", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": None,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_count": ["null"]}}),
        # - null
        ("deny user to POST without cpu_count", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_count": ["required"]}}),
        # ====================================================================================================
        # cpu_hz_actual_friendly
        # - string type
        ("deny user to POST with cpu_count of string type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": "test"},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_hz_actual_friendly": ["invalid"]}}),
        # - float type
        ("deny user to POST with cpu_count of float type", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000.1},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_hz_actual_friendly": ["invalid"]}}),
        # - none
        ("deny user to POST with cpu_count of none", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": None},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_hz_actual_friendly": ["null"]}}),
        # - null
        ("deny user to POST with cpu_count of none", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz"},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_hz_actual_friendly": ["required"]}}),
        # ====================================================================================================
    ])
    def test_syntax(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

    # ====================================================================================================
    # Boundary Tests
    # - cpu_bits must be 32 or 64
    # - cpu_count must be between 1 and 128
    # - cpu_hz_actual_friendly must be equal to or greater than 0
    # ====================================================================================================
    @parameterized.expand([
        # ====================================================================================================
        # cpu_bits
        # - not in list
        ("deny user to POST with cpu_bits not in list, 128", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 128,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_bits": ["value_not_in_list"]}}),
        # ====================================================================================================
        # cpu_count
        # - min_value
        ("deny user to POST with cpu_bits less than min value, 0", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 0,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_count": ["min_value"]}}),
        ("deny user to POST with cpu_bits equal to min value, 1", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 1,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_201_CREATED}),
        ("deny user to POST with cpu_bits greater than min value, 2", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 2,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_201_CREATED}),
        # - max_value
        ("deny user to POST with cpu_bits less than max value, 127", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 127,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_201_CREATED}),
        ("deny user to POST with cpu_bits equal to max value, 128", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 128,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_201_CREATED}),
        ("deny user to POST with cpu_bits greater than max value, 129", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 129,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 2903998000},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_count": ["max_value"]}}),
        # ====================================================================================================
        # cpu_hz_actual_friendly
        # - min_value
        ("deny expected_error_code to POST with cpu_hz_actual_friendly less than min value, -1", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": -1},
            "expected_status_code": HTTP_400_BAD_REQUEST,
            "expected_error_code": {"cpu_hz_actual_friendly": ["min_value"]}}),
        ("deny user to POST with cpu_hz_actual_friendly equal to min value, 0", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 0},
            "expected_status_code": HTTP_201_CREATED}),
        ("deny user to POST with cpu_hz_actual_friendly greater than min value, 1", "POST", {
            "request_token": "user1",
            "request_data": {
                "used_port": 10003,
                "cpu_arch": "X86_64",
                "cpu_bits": 64,
                "cpu_count": 16,
                "cpu_arch_string_raw": "x86_64",
                "cpu_vendor_id_raw": "GenuineIntel",
                "cpu_brand_raw": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
                "cpu_hz_actual_friendly": 1},
            "expected_status_code": HTTP_201_CREATED}),
        # ====================================================================================================
    ])
    def test_boundary(self, _: str, method: str, data: Dict[str, object]) -> None:
        self._test(method=method, data=data)

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
# - User can"t update a CPUStat with a cpu_percent that is not a float
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
# - User can"t create a MemorySpec with a used_port that is already in use
# - User can"t create a MemorySpec with a used_port that is not a valid port number
# - User can"t create a MemorySpec with a memory_total that is not a big integer
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
