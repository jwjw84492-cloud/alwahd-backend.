import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import time
import os # مكتبة مهمة لقراءة إعدادات النظام

app = FastAPI()

# تفعيل السماح لجميع الروابط بالاتصال (CORS) لضمان عمل الواجهة
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class FLambdaCore:
    F_LAMBDA = 15.0725

    @staticmethod
    def process_bytes(data: bytes):
        # محاكاة المعالجة الفيزيائية للبايتات
        signals = [float(f"{(b * FLambdaCore.F_LAMBDA + (i + 1)) % 1.0:.12f}") for i, b in enumerate(data[:100])]
        return signals

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        contents = await file.read()
        file_size = len(contents)
        
        # تحويل الملف بالكامل إلى Base64 ليتم عرضه في الواجهة
        encoded_content = base64.b64encode(contents).decode('utf-8')
        
        # معالجة العينة الفيزيائية
        signatures = FLambdaCore.process_bytes(contents)
        
        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": file_size,
            "processing_time": f"{time.time() - start_time:.4f}s",
            "signatures": signatures,
            "recovered_file": encoded_content
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="خطأ في معالجة الملف")

if __name__ == "__main__":
    # هذا التعديل يجعل الكود يقرأ المنفذ من Render تلقائياً أو يستخدم 10000 كافتراضي
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

