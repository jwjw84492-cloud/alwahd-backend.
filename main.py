import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time
app = FastAPI()
app.add_
middleware
CORSMiddleware,
" [,
allow
_origins=]" *
allow
_credentials=True,
" [,
allow
_methods=]" *
" [,
allow
_headers=]" *
(
class FLambdaCore :
F
LAMBDA = 15.0725
_
@staticmethod
def encode(data: str):
raw
_bytes = data.encode('utf-8')
signals = ][
_bytes):
for i, byte in enumerate(raw
signal = (byte * FLambdaCore.F_
LAMBDA + (i + 1)) % 1.0
signals.append(float(f"{signal:.12f}"))
return signals
@staticmethod
def decode(signals):
reconstructed = bytearray )(
for i, sig in enumerate(signals):
found = False
test
_sig = (byte_
val * FLambdaCore.F
for byte_val in range(256):
_
LAMBDA + (i + 1)) % 1.0
:if abs(test
_sig - sig) < 1e-9
reconstructed.append(byte_
val)
found = True
break
if not found: return None
return reconstructed.decode('utf-8', errors='ignore')
class DataInput(BaseModel):
content: str
return {"status": "Online"
,
"(
)" /
@app.get
)(:
async def root
"model": "F-Lambda v2.0"}
@app.post("/process")
data(data: DataInput):
async def process_
try :
)(
start
time = time×time
_
signatures = FLambdaCore.encode(data×content)
recovered = FLambdaCore×decode(signatures)
duration = time.time() - start
_
time
return }
success": True,
"
,
signature_
count": len(signatures)
"
signatures_sample": signatures[:10],
"
,
time": f"{duration:.4f}s"
processing_
"
integrity": data.content == recovered,
"
recovered
content": recovered
"
_
{
except Exception as e :
raise HTTPException(status
_code=400, detail=str(e))
":
if
"
name
==
main
_
__
__
__
uvicorn.run(app, host="0.0.0.0", port=8000)
