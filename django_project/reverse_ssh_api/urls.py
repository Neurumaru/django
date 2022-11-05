from django.urls import include, path
from rest_framework import routers
from reverse_ssh_api.views import *

router = routers.DefaultRouter()
router.register(r'reserved-port', ReservedPortView)
router.register(r'used-port', UsedPortView)
router.register(r'free-port', FreePortView)
# router.register(r'cpu', CPUView)
# router.register(r'ram', RAMView)
# router.register(r'gpu', GPUView)

urlpatterns = [
   path('', include(router.urls)),
]