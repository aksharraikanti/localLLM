 # Model Card: LoRA Adapter for Llama-2-7b-chat

## Model Details
- **Base Model**: meta-llama/Llama-2-7b-chat-hf
- **Adapter Type**: LoRA (Low-Rank Adaptation)

### Adapter Configuration
- Rank (r): 16
- Alpha: 32
- Dropout: 0.05

### Training Data
- Fine-tuned on curated QA dataset (questions & answers pairs)
- Prototype run: first 500 samples (data/processed/train_small.jsonl)
- Full run: all training examples (data/processed/train.jsonl) with validation (data/processed/val.jsonl)

## Training Hyperparameters
| Parameter                      | Value           |
|--------------------------------|-----------------|
| Learning rate                  | 3e-4            |
| Batch size (per device)        | 8               |
| Gradient accumulation          | 4 (to 32 host)  |
| Epochs                         | 3               |
| Mixed precision                | FP16            |
| Logging                        | TensorBoard     |

## Results & Metrics
- Prototype loss start/end: *to be filled*
- Validation loss: *to be filled*

## Usage
Load the adapter and generate using the `transformers` pipeline:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

tokenizer = AutoTokenizer.from_pretrained("models/lora_adapter", use_fast=True)
model = AutoModelForCausalLM.from_pretrained("models/lora_adapter", device_map="auto")
chat = pipeline("text-generation", model=model, tokenizer=tokenizer)
print(chat("What is Kubernetes?", max_length=256))
```
