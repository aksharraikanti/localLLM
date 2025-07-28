#!/usr/bin/env python3
"""
Run hyperparameter search with Optuna using Hugging Face Trainer.
"""
import argparse

import yaml
from datasets import load_from_disk
from transformers import (AutoModelForSeq2SeqLM, AutoTokenizer,
                          DataCollatorForSeq2Seq, Trainer, TrainingArguments)


def hp_space_fn(trial, hp_config):
    """Define the hyperparameter search space based on the YAML config."""
    search_space = {}
    if "learning_rate" in hp_config:
        params = hp_config["learning_rate"]
        search_space["learning_rate"] = trial.suggest_float(
            "learning_rate", params["min"], params["max"], log=params.get("log", False)
        )
    if "batch_size" in hp_config:
        params = hp_config["batch_size"]
        search_space["per_device_train_batch_size"] = trial.suggest_categorical(
            "per_device_train_batch_size", params["choices"]
        )
    if "epochs" in hp_config:
        params = hp_config["epochs"]
        search_space["num_train_epochs"] = trial.suggest_int(
            "num_train_epochs", params["min"], params["max"]
        )
    return search_space


def main():
    parser = argparse.ArgumentParser(
        description="Hyperparameter search with Optuna and Hugging Face Trainer"
    )
    parser.add_argument(
        "--dataset-dir", required=True, help="Tokenized dataset directory"
    )
    parser.add_argument(
        "--model-name-or-path", required=True, help="Pretrained model for fine-tuning"
    )
    parser.add_argument(
        "--output-dir", required=True, help="Directory to store HPO results"
    )
    parser.add_argument(
        "--hp-config",
        default="configs/hyperparams.yaml",
        help="Hyperparameter search space YAML file",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=10,
        help="Number of HPO trials",
    )
    args = parser.parse_args()

    hp_config = yaml.safe_load(open(args.hp_config, encoding="utf8"))
    metric = hp_config.get("metric", "eval_loss")
    direction = hp_config.get("direction", "minimize")
    # Remove non-search keys
    hp_config = {k: v for k, v in hp_config.items() if k not in ("metric", "direction")}

    # Load dataset and tokenizer
    ds = load_from_disk(args.dataset_dir)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name_or_path)
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    # Define Trainer with model_init for fresh model per trial
    def model_init():
        return AutoModelForSeq2SeqLM.from_pretrained(args.model_name_or_path)

    # Base training arguments, defaults from hp_config if provided
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=hp_config.get("batch_size", {}).get("default", 8),
        num_train_epochs=hp_config.get("epochs", {}).get("default", 3),
        learning_rate=hp_config.get("learning_rate", {}).get("default", 5e-5),
        logging_dir=f"{args.output_dir}/logs",
        logging_steps=hp_config.get("logging_steps", {}).get("default", 10),
    )

    trainer = Trainer(
        model_init=model_init,
        args=training_args,
        train_dataset=ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    best_run = trainer.hyperparameter_search(
        hp_space=lambda trial: hp_space_fn(trial, hp_config),
        direction=direction,
        backend="optuna",
        n_trials=args.trials,
    )
    print("Best hyperparameter set:", best_run)


if __name__ == "__main__":
    main()
