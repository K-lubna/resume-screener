from fastapi import APIRouter, UploadFile, File
from services.resume_parser import parse_resume_file
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    parsed = parse_resume_file(content, filename=file.filename)
    return JSONResponse(content=parsed)
