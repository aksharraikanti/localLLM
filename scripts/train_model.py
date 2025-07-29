#!/usr/bin/env python3
"""
Fine-tune a pretrained model on a tokenized QA dataset using Hugging Face Trainer.
"""
import argparse

import yaml
from datasets import load_from_disk
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
)


def train_model(
    dataset_dir: str,
    model_name_or_path: str,
    output_dir: str,
    per_device_train_batch_size: int,
    num_train_epochs: int,
    learning_rate: float,
    evaluation_strategy: str = "no",
    eval_steps: int = None,
    save_strategy: str = "epoch",
    save_total_limit: int = None,
    load_best_model_at_end: bool = False,
    metric_for_best_model: str = "eval_loss",
    greater_is_better: bool = False,
    gradient_accumulation_steps: int = 1,
    fp16: bool = False,
    report_to: str = "tensorboard",
    wandb_project: str = None,
    early_stopping_patience: int = None,
):
    """
    Load tokenized dataset, fine-tune the model, and save the result.
    """
    ds = load_from_disk(dataset_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path)

    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=per_device_train_batch_size,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        evaluation_strategy=evaluation_strategy,
        eval_steps=eval_steps,
        save_strategy=save_strategy,
        save_total_limit=save_total_limit,
        load_best_model_at_end=load_best_model_at_end,
        metric_for_best_model=metric_for_best_model,
        greater_is_better=greater_is_better,
        gradient_accumulation_steps=gradient_accumulation_steps,
        fp16=fp16,
        report_to=report_to,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    # optionally add early stopping callback
    if load_best_model_at_end and early_stopping_patience is not None:
        try:
            from transformers import EarlyStoppingCallback

            trainer.add_callback(
                EarlyStoppingCallback(early_stopping_patience=early_stopping_patience)
            )
        except Exception:
            pass
    trainer.train()
    trainer.save_model(output_dir)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune model on QA dataset")
    parser.add_argument("--config", help="YAML config file for training parameters")
    parser.add_argument(
        "--dataset-dir",
        default="data/processed/dataset",
        help="Tokenized dataset directory",
    )
    parser.add_argument(
        "--model-name-or-path",
        required=True,
        help="Pretrained model for fine-tuning",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Where to store the fine-tuned model",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Per-device train batch size",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=5e-5,
        help="Learning rate",
    )
    args = parser.parse_args()
    # load config file overrides
    cfg = {}
    if args.config:
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f) or {}
    # override CLI args from config
    mapping = {
        "dataset_dir": "dataset_dir",
        "model_name_or_path": "model_name_or_path",
        "output_dir": "output_dir",
        "batch_size": "batch_size",
        "epochs": "epochs",
        "learning_rate": "lr",
    }
    for key, attr in mapping.items():
        if key in cfg:
            setattr(args, attr, cfg[key])
    # gather training kwargs
    train_kwargs = {
        "dataset_dir": args.dataset_dir,
        "model_name_or_path": args.model_name_or_path,
        "output_dir": args.output_dir,
        "per_device_train_batch_size": args.batch_size,
        "num_train_epochs": args.epochs,
        "learning_rate": args.lr,
        "evaluation_strategy": cfg.get("evaluation_strategy"),
        "eval_steps": cfg.get("eval_steps"),
        "save_strategy": cfg.get("save_strategy"),
        "save_total_limit": cfg.get("save_total_limit"),
        "load_best_model_at_end": cfg.get("load_best_model_at_end"),
        "metric_for_best_model": cfg.get("metric_for_best_model"),
        "greater_is_better": cfg.get("greater_is_better"),
        "gradient_accumulation_steps": cfg.get("gradient_accumulation_steps"),
        "fp16": cfg.get("fp16"),
        "report_to": cfg.get("report_to"),
        "wandb_project": cfg.get("wandb_project"),
        "early_stopping_patience": cfg.get("early_stopping_patience"),
    }
    # call training
    # filter out None values to rely on defaults
    train_model(**{k: v for k, v in train_kwargs.items() if v is not None})


if __name__ == "__main__":
    main()
