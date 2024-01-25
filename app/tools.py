from errors import HttpError
from pydantic import ValidationError
from scheme import SCHEME_CLASS


def validate(scheme_cls: SCHEME_CLASS, json_data: dict | list):
    try:
        return scheme_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as e:
        error = e.errors()[0]
        error.pop("ctx", None)
        raise HttpError(400, error)
