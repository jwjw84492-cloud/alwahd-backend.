‏from fastapi import FastAPI, UploadFile, File
‏from fastapi.responses import HTMLResponse
‏import base64
‏import time

‏F_LAMBDA = 15.0725

‏app = FastAPI(title="F-Lambda Transformer")

‏def encode_bytes(data: bytes):
‏    signals = []
‏    for i, b in enumerate(data):
‏        signal = (b * F_LAMBDA + (i + 1)) % 1.0
‏        signals.append(float(f"{signal:.12f}"))
‏    return signals

‏HTML_PAGE = """
‏<!DOCTYPE html>
‏<html lang="en">
‏<head>
‏    <meta charset="UTF-8">
‏    <title>F-Lambda Transformer</title>
‏</head>
‏<body>
‏    <h2>Upload File for F-Lambda Transformation</h2>
‏    <form action="/upload" method="post" enctype="multipart/form-data">
‏        <input type="file" name="file" required>
‏        <button type="submit">Transform</button>
‏    </form>
‏</body>
‏</html>
"""

‏@app.get("/", response_class=HTMLResponse)
‏async def root():
‏    return HTML_PAGE

‏@app.post("/upload")
‏async def upload_file(file: UploadFile = File(...)):
‏    start_time = time.time()
‏    contents = await file.read()
    
‏    signals = encode_bytes(contents)
‏    encoded_file = base64.b64encode(contents).decode('utf-8')
    
‏    return {
‏        "success": True,
‏        "filename": file.filename,
‏        "content_type": file.content_type,
‏        "size_bytes": len(contents),
‏        "signals_count": len(signals),
‏        "processing_time": f"{time.time() - start_time:.4f}s",
‏        "recovered_file": encoded_file
    }

‏if __name__ == "__main__":
‏    import uvicorn
‏    uvicorn.run(app, host="0.0.0.0", port=8000)
