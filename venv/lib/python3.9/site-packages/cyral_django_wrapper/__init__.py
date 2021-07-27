import json
from typing import Any, Dict, Optional

from django.db.backends import utils

from . import settings
from .errors import IdentityNotSetError

USER_IDENTITY: Dict[str, str] = {}
SERVICE_NAME: Optional[str] = None


def _annotate_query(sql: str) -> str:
    if USER_IDENTITY:
        email = USER_IDENTITY["email"]
        group = USER_IDENTITY["group"]
        identity = {
            "user": email,
            "userGroup": group,
        }
        if SERVICE_NAME is not None:
            identity["serviceName"] = SERVICE_NAME
        comment_data = json.dumps(identity)
    else:
        if settings.REQUIRE_IDENTITY:
            # if REQUIRE_IDENTITY is true, block the query and raise this exception
            raise IdentityNotSetError()
        else:
            # otherwise, let the query pass
            comment_data = "USER_IDENTITY_NOT_SET"
    return f"/*CyralContext {comment_data}*/ {sql}"


def _patch_wrapper(wrapper_class):
    original_execute = wrapper_class.execute
    original_executemany = wrapper_class.executemany

    def annotated_execute(self, sql: str, *args: Any, **kwargs: Any):
        sql = _annotate_query(sql)
        return original_execute(self, sql, *args, **kwargs)

    def annotated_executemany(self, sql: str, *args: Any, **kwargs: Any):
        sql = _annotate_query(sql)
        return original_executemany(self, sql, *args, **kwargs)

    wrapper_class.execute = annotated_execute
    wrapper_class.executemany = annotated_execute


def install_wrapper():
    _patch_wrapper(utils.CursorWrapper)
    _patch_wrapper(utils.CursorDebugWrapper)


def set_user_identity(email: str, group: str) -> None:
    USER_IDENTITY["email"] = email
    USER_IDENTITY["group"] = group


def set_service_name(name: str) -> None:
    global SERVICE_NAME
    SERVICE_NAME = name


__all__ = ["set_user_identity", "set_service_name"]

default_app_config = "cyral_django_wrapper.apps.CyralDjangoWrapperConfig"
