def extract(data):
    return {
        "name": data["user"]["full_name"],
        "age": data["user"]["details"]["age"],
        "city": data["user"]["details"]["location"]
    }
