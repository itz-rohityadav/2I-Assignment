def extract(data: dict) -> dict:
    return {
        "name": data["name"],
        "age": data["age"],
        "city": data["city"],
    }