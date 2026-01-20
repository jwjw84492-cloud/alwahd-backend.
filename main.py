import time
import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import decimal

# --- إعداد الدقة العالية للكسور ---
decimal.getcontext().prec = 100

app = FastAPI()

# تمكين CORS للوصول من أي فرونت اند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ثابت افتراضي
FRACTAL_CONSTANT = decimal.Decimal("15.0725")

# --- نواة التحويل الكسري ---
def general_transform_kernel(data: List[int], constant: decimal.Decimal):
    signals = []
    for i, b in enumerate(data):
        order = i + 1
        signal = (decimal.Decimal(b) * constant + order) % 1
        signals.append(float(signal))
    return signals

# --- النواة العكسية لاسترجاع البيانات الأصلية ---
def inverse_transform_kernel(signals: List[float], constant: decimal.Decimal):
    recovered_data = []
    for i, s in enumerate(signals):
        order = i + 1
        # المعادلة العكسية: b = (s - order) / constant
        b = (decimal.Decimal(s) - order) / constant
        recovered_data.append(int(b) % 256)  # ضمان بايت صالح
    return bytes(recovered_data)

# --- نقطة النهاية /transform ---
@app.post("/transform")
async def transform_file(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        # قراءة الملف
        contents = await file.read()
        size_bytes = len(contents)

        # تحويل الكسور
        signals = general_transform_kernel(list(contents), FRACTAL_CONSTANT)

        # استرجاع البيانات
        recovered_bytes = inverse_transform_kernel(signals, FRACTAL_CONSTANT)

        # تحويل الملف المسترجع إلى Base64
        encoded_file = base64.b64encode(recovered_bytes).decode('utf-8')

        # النتيجة النهائية
        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": size_bytes,
            "signals_count": len(signals),
            "processing_time": f"{time.time() - start_time:.4f}s",
            "recovered_file": encoded_file
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# --- اختبار سريع عند التشغيل ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
