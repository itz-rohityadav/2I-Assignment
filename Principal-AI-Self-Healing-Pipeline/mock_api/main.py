from fastapi import FastAPI, Query

app = FastAPI(title="Changing Third-Party API")


@app.get("/users")
def get_user(version: int = Query(default=1, ge=1, le=2)):
    """Return one of the two API shapes used by the demonstration."""
    if version == 1:
        return {"name": "Rohit", "age": 22, "city": "Bangalore"}

    return {
        "user": {
            "full_name": "Rohit",
            "details": {"age": 22, "location": "Bangalore"},
        }
    }
