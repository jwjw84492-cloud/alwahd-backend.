import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import time

app = FastAPI()

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
        # تحويل البايتات إلى إشارات طيفية حتمية
        signals = [float(f"{(b * FLambdaCore.F_LAMBDA + (i + 1)) % 1.0:.12f}") for i, b in enumerate(data)]
        return signals[:100] # نرسل عينة فقط للعرض لتوفير الجهد

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        # قراءة محتوى الملف (سواء كان صورة أو فيديو أو غيره)
        contents = await file.read()
        file_size = len(contents)
        
        # معالجة البيانات
        signatures = FLambdaCore.process_bytes(contents)
        
        # تحويل الملف إلى Base64 لعرضه مرة أخرى في الواجهة (الاسترداد)
        encoded_content = base64.b64encode(contents).decode('utf-8')
        
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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

