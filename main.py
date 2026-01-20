import time
import base64
import decimal
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# === إعداد الدقة العالية للكسور ===
decimal.getcontext().prec = 100

app = FastAPI()

# === تمكين CORS للوصول من أي فرونت اند ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ثابت افتراضي ===
FRACTAL_CONSTANT = decimal.Decimal("15.0725")

# === النواة الكسريّة لتحويل البيانات ===
def general_transform_kernel(data: List[int], constant: decimal.Decimal):
    signals = []
    for i, b in enumerate(data):
        order = i + 1
        signal = (decimal.Decimal(b) * constant + order) % 1
        signals.append(float(signal))
    return signals

# === النواة العكسية لاسترجاع البيانات ===
def inverse_transform_kernel(signals: List[float], constant: decimal.Decimal):
    recovered_data = []
    for i, s in enumerate(signals):
        order = i + 1
        b = (decimal.Decimal(s) - order) / constant
        recovered_data.append(int(b) % 256)  # ضمان بايت صالح
    return bytes(recovered_data)

# === نقطة النهاية /transform ===
@app.post("/transform")
async def transform_file(file: UploadFile = File(...)):
    start_time = time.time()
    signals = []

    try:
        chunk_size = 1024 * 64  # 64KB per chunk

        # قراءة الملف chunk by chunk ومعالجة الإشارات مباشرة
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            signals.extend(general_transform_kernel(list(chunk), FRACTAL_CONSTANT))

        # استرجاع البيانات الأصلية
        recovered_bytes = inverse_transform_kernel(signals, FRACTAL_CONSTANT)

        # ترميز Base64 للواجهة الأمامية
        encoded_file = base64.b64encode(recovered_bytes).decode('utf-8')

        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": file.spool_max_size if hasattr(file, "spool_max_size") else len(recovered_bytes),
            "signals_count": len(signals),
            "processing_time": f"{time.time() - start_time:.4f}s",
            "recovered_file": encoded_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# === للتشغيل المحلي مع uvicorn ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
