import uuid


def generate_uuid_from_string(string: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_OID, str(string).strip().lower())
