import json


def dict_to_bytes(d: dict) -> bytes:
    s = json.dumps(d)
    return s.encode("utf-8")


def fake_read(offset: int, size: int):
    return dict_to_bytes({
        "offset": offset,
        "size": size,
    })
