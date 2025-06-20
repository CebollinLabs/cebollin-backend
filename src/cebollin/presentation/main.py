from fastapi import FastAPI
from .api.v1 import diagnosis_router, treatment_router, users_router, plots_router

app = FastAPI(title="Cebollin API", version="1.0.0")

app.include_router(diagnosis_router.router, prefix="/api/v1")
app.include_router(treatment_router.router, prefix="/api/v1")
app.include_router(users_router.router, prefix="/api/v1")
app.include_router(plots_router.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Cebollin API is running!"}
