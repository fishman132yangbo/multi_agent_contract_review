from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.review import ApprovalRequest, ReviewRequest, ReviewResponse
from app.services.document_parser import (
    EmptyDocumentTextError,
    UnsupportedDocumentTypeError,
    extract_text_from_upload,
)
from app.services.review_service import (
    ReviewTaskConflictError,
    ReviewTaskNotFoundError,
    get_review_task,
    review_contract,
    submit_approval,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/contracts/review", response_model=ReviewResponse)
def review_contract_endpoint(payload: ReviewRequest) -> ReviewResponse:
    return review_contract(payload.contract_text)


@app.get("/contracts/review/{task_id}", response_model=ReviewResponse)
def get_review_endpoint(task_id: str) -> ReviewResponse:
    result = get_review_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Review task not found")
    return result


@app.post("/contracts/review/{task_id}/approval", response_model=ReviewResponse)
def approve_review_endpoint(task_id: str, payload: ApprovalRequest) -> ReviewResponse:
    try:
        result = submit_approval(task_id, payload)
    except ReviewTaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReviewTaskConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return result


@app.post("/contracts/review/upload", response_model=ReviewResponse)
async def review_contract_upload_endpoint(
    file: UploadFile = File(...),
) -> ReviewResponse:
    content = await file.read()

    try:
        contract_text = extract_text_from_upload(file.filename or "", content)
    except UnsupportedDocumentTypeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except EmptyDocumentTextError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return review_contract(contract_text)
