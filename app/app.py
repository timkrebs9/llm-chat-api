from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="AKS Demo API")

@app.get("/")
async def root():
    return {"message": "Hello from AKS!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/info")
async def info():
    return {
        "app_name": "AKS Demo API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 