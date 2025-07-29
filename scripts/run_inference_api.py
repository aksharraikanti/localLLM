#!/usr/bin/env python3
"""
Run a FastAPI server for inference using a fine-tuned Seq2Seq model.
"""
import argparse
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

app = FastAPI(title="QA Inference API")


class InferenceRequest(BaseModel):
    question: str
    max_length: int = 512


class InferenceResponse(BaseModel):
    answer: str


tokenizer = None
model = None

# optional API key enforcement (set via environment variable)
API_KEY = os.environ.get("API_KEY")


def verify_api_key(x_api_key: str = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def init_model(model_dir: str):
    """Load tokenizer and model from the specified directory."""
    global tokenizer, model
    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)


@app.post(
    "/predict",
    response_model=InferenceResponse,
    dependencies=[Depends(verify_api_key)],
)
def predict(req: InferenceRequest):
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=503,
            detail="Model not initialized. Please start server via script.",
        )
    inputs = tokenizer(
        req.question, return_tensors="pt", truncation=True, max_length=req.max_length
    )
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_length=req.max_length,
    )
    if not outputs:
        raise HTTPException(
            status_code=500,
            detail="Model failed to generate an output. Please try again or check the input."
        )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return InferenceResponse(answer=answer)


@app.get("/health", dependencies=[Depends(verify_api_key)])
def health():
    """Health check endpoint returning service status."""
    return {"status": "ok"}


from typing import List


class BatchRequest(BaseModel):
    questions: List[str]
    max_length: int = 512


class BatchResponse(BaseModel):
    answers: List[str]


@app.post(
    "/predict_batch",
    response_model=BatchResponse,
    dependencies=[Depends(verify_api_key)],
)
def predict_batch(req: BatchRequest):
    """Handle batch inference for a list of questions."""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not initialized.")
    answers: List[str] = []
    for question in req.questions:
        inputs = tokenizer(
            question, return_tensors="pt", truncation=True, max_length=req.max_length
        )
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=req.max_length,
        )
        answers.append(tokenizer.decode(outputs[0], skip_special_tokens=True))
    return BatchResponse(answers=answers)


def main():
    parser = argparse.ArgumentParser(description="Serve QA model via FastAPI")
    parser.add_argument(
        "--model-dir", required=True, help="Directory of the fine-tuned model to serve"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host/IP to bind the server")
    parser.add_argument("--port", type=int, default=8000, help="Port for the server")
    args = parser.parse_args()

    init_model(args.model_dir)
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
