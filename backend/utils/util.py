from hashlib import sha256
from base64 import b64encode
from uuid import uuid1
from traceback import format_exception as tformat_exception
from typing import Union
from sys import version_info

import inspect
from pydantic import BaseModel


def text_encode(text: Union[str, bytes], path_safe=False) -> str:
    """
    將明文加密。
    """
    text = text.encode() if type(text) == str else text
    result = b64encode(sha256(text).digest()).decode()
    return result.replace("/", "$") if path_safe else result


def gen_session_id() -> str:
    """
    產生Session ID。
    """
    return text_encode(uuid1().bytes, path_safe=True)


def format_exception(exc: Exception) -> list[str]:
    if version_info.minor < 10:
        return tformat_exception(exc.__class__, exc, exc.__traceback__)
    return tformat_exception(exc)


def string_exception(exc: Exception) -> str:
    return "".join(format_exception(exc))


def optional(*fields):
    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
            if _cls.__fields__[field].default:
                _cls.__fields__[field].default = None
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)
    return dec
