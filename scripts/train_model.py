#!/usr/bin/env python3
"""
Fine-tune a pretrained model on a tokenized QA dataset using Hugging Face Trainer.
"""
import argparse

from datasets import load_from_disk
from transformers import (AutoModelForSeq2SeqLM, AutoTokenizer,
                          DataCollatorForSeq2Seq, Trainer, TrainingArguments)


def train_model(
    dataset_dir: str,
    model_name_or_path: str,
    output_dir: str,
    per_device_train_batch_size: int,
    num_train_epochs: int,
    learning_rate: float,
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
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    trainer.train()
    trainer.save_model(output_dir)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune model on QA dataset")
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
    train_model(
        args.dataset_dir,
        args.model_name_or_path,
        args.output_dir,
        args.batch_size,
        args.epochs,
        args.lr,
    )


if __name__ == "__main__":
    main()
