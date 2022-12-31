from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


# ====================================================================================================
# ValueInListValidator
# - Checks if the value is in the list
# ====================================================================================================
@deconstructible
class ValueInListValidator(BaseValidator):
    message = _("Ensure this value is in %(limit_value)s.")
    code = "value_not_in_list"

    def compare(self, a, b):
        return a not in b
