from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.review import ReviewRequest, ReviewResponse
from app.services.review_service import review_contract

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
