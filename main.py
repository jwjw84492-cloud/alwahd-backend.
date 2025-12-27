import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# تفعيل الربط مع الواجهة الأمامية (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class FLambdaCore:
    F_LAMBDA = 15.0725

    @staticmethod
    def encode(data: str):
        raw_bytes = data.encode('utf-8')
        signals = [float(f"{(b * FLambdaCore.F_LAMBDA + (i + 1)) % 1.0:.12f}") for i, b in enumerate(raw_bytes)]
        return signals

    @staticmethod
    def decode(signals):
        reconstructed = bytearray()
        for i, sig in enumerate(signals):
            for b in range(256):
                if abs(((b * FLambdaCore.F_LAMBDA + (i + 1)) % 1.0) - sig) < 1e-9:
                    reconstructed.append(b)
                    break
        return reconstructed.decode('utf-8', errors='ignore')

class DataInput(BaseModel):
    content: str

@app.get("/")
def status():
    return {"status": "Online", "engine": "F-Lambda v3.0"}

@app.post("/process")
def process(data: DataInput):
    start = time.time()
    sigs = FLambdaCore.encode(data.content)
    rec = FLambdaCore.decode(sigs)
    return {
        "success": True,
        "processing_time": f"{time.time() - start:.4f}s",
        "integrity": data.content == rec,
        "signatures": sigs[:5],
        "recovered_content": rec
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

