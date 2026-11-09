from fastapi import FastAPI

app = FastAPI(title="NeuronixAI AI service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
