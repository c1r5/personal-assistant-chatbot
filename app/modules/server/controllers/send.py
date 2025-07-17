from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from io import BytesIO

from pydantic import BaseModel

from modules.bot import send_file, send_message
from modules.server.rate_limiter import limiter

send_route = APIRouter(prefix="/send")

@send_route.post("/document")
@limiter.limit("5/minute")
async def upload(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        buffer = BytesIO(contents)
        await send_file(buffer, file.filename)
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class MessageBody(BaseModel):
    message: str

@send_route.post("/message")
@limiter.limit("5/minute")
async def message(request: Request, body: MessageBody) -> JSONResponse:
    try:
        if not body.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        await send_message(body.message)

        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
