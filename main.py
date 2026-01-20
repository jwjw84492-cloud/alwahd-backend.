import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import decimal
import time

# High precision
decimal.getcontext().prec = 80
FRACTAL_CONSTANT = decimal.Decimal("74899")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def encode_bytes(data_bytes):
    signals = []
    for i, b in enumerate(data_bytes):
        order = i + 1
        signal = (decimal.Decimal(b) * FRACTAL_CONSTANT + order) % 1
        signals.append(signal)
    return signals

def decode_bytes(signals):
    recovered = []
    for i, s in enumerate(signals):
        order = i + 1
        raw = (s - decimal.Decimal(order)) / FRACTAL_CONSTANT
        b = int(round(raw))
        if b < 0: b = 0
        if b > 255: b = 255
        recovered.append(b)
    return bytes(recovered)

@app.post("/transform")
async def transform_file(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        contents = await file.read()
        size_bytes = len(contents)

        signals = encode_bytes(contents)
        recovered = decode_bytes(signals)

        success = contents == recovered

        return {
            "success": success,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": size_bytes,
            "signals_count": len(signals),
            "processing_time": f"{time.time() - start_time:.4f}s",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "Fractal Kernel Online"}

# Render start point
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
