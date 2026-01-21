import time
import base64
import decimal
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

decimal.getcontext().prec = 100

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRACTAL_CONSTANT = decimal.Decimal("15.0725")

def transform_kernel(data, constant):
    signals = []
    for i, b in enumerate(data):
        order = i + 1
        signal = (decimal.Decimal(b) * constant + order) % 1
        signals.append(float(signal))
    return signals

def inverse_kernel(signals, constant):
    recovered = []
    for i, s in enumerate(signals):
        order = i + 1
        b = (decimal.Decimal(s) - order) / constant
        recovered.append(int(b) % 256)
    return bytes(recovered)

@app.post("/transform")
async def transform_file(file: UploadFile = File(...)):
    start = time.time()
    signals = []

    chunk_size = 1024 * 64  # 64KB

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        signals.extend(transform_kernel(list(chunk), FRACTAL_CONSTANT))

    recovered_bytes = inverse_kernel(signals, FRACTAL_CONSTANT)
    encoded = base64.b64encode(recovered_bytes).decode()

    return {
        "success": True,
        "filename": file.filename,
        "content_type": file.content_type,
        "signals_count": len(signals),
        "processing_time": f"{time.time()-start:.4f}s",
        "recovered_file": encoded
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
