# localLLM

[![CI](https://github.com/your-org/localLLM/actions/workflows/ci.yml/badge.svg)]()
[![Python](https://img.shields.io/badge/python-3.10-blue.svg)]()

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
