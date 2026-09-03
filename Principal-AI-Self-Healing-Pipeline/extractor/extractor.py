def extract(data: dict) -> dict:
    return {
        "name": data.get("name"),
        "age": data.get("age"),
        "city": data.get("city"),
    }
#reference code only for v1