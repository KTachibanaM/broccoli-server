from typing import Tuple
from jsonschema import validate, ValidationError


def validate_schema_or_not(instance, schema) -> Tuple[bool, str]:
    try:
        validate(instance=instance, schema=schema)
        return True, ""
    except ValidationError as e:
        return False, str(e)
