# localLLM

[![CI](https://github.com/your-org/localLLM/actions/workflows/ci.yml/badge.svg)]()
[![Python](https://img.shields.io/badge/python-3.10-blue.svg)]()

Install the SDK for inference client:
```bash
pip install .
# or once published: pip install localllm-client
```

## Local Environment Setup

To simplify local setup on macOS (Apple Silicon), run the provided script:

```bash
bash scripts/setup_local_env.sh
```

## Getting Started

Follow these steps to get the project running locally:

1. Copy the environment template and fill in your credentials:
   ```bash
   cp .env.template .env
   ```
2. Install Python dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Install and run pre-commit hooks:
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```
4. Run the test suite:
   ```bash
   pytest --maxfail=1 --disable-warnings -q
   ```

## Model Fine-Tuning

Once you have a processed dataset, you can fine-tune a pretrained model:

```bash
# Prepare the dataset (tokenized)
python scripts/prepare_dataset.py \
  --input data/clean/combined.jsonl \
  --output-dir data/processed/dataset \
  --model-name-or-path t5-small \
  --max-length 512

# Train the model
python scripts/train_model.py \
  --dataset-dir data/processed/dataset \
  --model-name-or-path t5-small \
  --output-dir models/t5-finetuned \
  --batch-size 8 \
  --epochs 3 \
  --lr 5e-5
```

Fill in hyperparameters in `configs/train_config.yaml` as needed.

## Hyperparameter Search

After a baseline fine-tuning run, you can run hyperparameter optimization:

```bash
python scripts/hyperparameter_search.py \
  --dataset-dir data/processed/dataset \
  --model-name-or-path t5-small \
  --output-dir models/t5-hpo \
  --hp-config configs/hyperparams.yaml \
  --trials 20
```

Defaults for search space, metric, and optimization direction are defined in `configs/hyperparams.yaml`. Tweak that file to adjust ranges, choices, or objective settings.

## Model Evaluation

After fine-tuning, evaluate your model on the cleaned QA dataset to compute ROUGE scores:

```bash
python scripts/evaluate_model.py \
  --input data/clean/combined.jsonl \
  --model-dir models/t5-finetuned \
  --output data/processed/eval_report.md \
  --batch-size 8 \
  --max-length 512
```

This will generate a markdown report with ROUGE metrics. Adjust batch size or `--max-length` as needed.

## Inference API

After fine-tuning, serve your model via a FastAPI inference endpoint:

```bash
# Start the API server (requires a fine-tuned model dir)
python scripts/run_inference_api.py \
  --model-dir models/t5-finetuned \
  --host 0.0.0.0 \
  --port 8000
```

The `/predict` endpoint accepts a JSON body:

```json
{ "question": "What is Kubernetes?", "max_length": 256 }
```

and returns:

```json
{ "answer": "Kubernetes is an open-source container orchestration system..." }
```

Optional features:
- **API Key**: set `API_KEY` environment variable and include header `X-API-Key` to secure endpoints.
- **Batch inference**: use `/predict_batch` with `{"questions": [...], "max_length": ...}` to get multiple answers.
- **Health check**: GET `/health` returns `{ "status": "ok" }`.
- After installation, use the `localllm-client` CLI (or import `localllm_client.client`) to run inference calls.

### Docker Deployment

Build and run the inference API in a Docker container:

```bash
docker build -t localllm-api .
docker run -e API_KEY=<your_key> -e MODEL_DIR=models/t5-finetuned \
  -p 8000:8000 localllm-api
```

Or using Docker Compose (set `API_KEY` and `MODEL_DIR` in `.env`):

```bash
docker-compose up --build
```
