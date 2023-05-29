---
license: apache-2.0
tags:
- generated_from_trainer
model-index:
- name: specter2-finetuned-v2
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# specter2-finetuned-v2

This model is a fine-tuned version of [allenai/specter2](https://huggingface.co/allenai/specter2) on an unknown dataset.
It achieves the following results on the evaluation set:
- Loss: 0.9913
- Geog Precision: 0.0
- Geog Recall: 0.0
- Geog F1: 0.0
- Geog Number: 0
- Region Precision: 0.0
- Region Recall: 0.0
- Region F1: 0.0
- Region Number: 3
- Site Precision: 0.0
- Site Recall: 0.0
- Site F1: 0.0
- Site Number: 1
- Taxa Precision: 0.0
- Taxa Recall: 0.0
- Taxa F1: 0.0
- Taxa Number: 0
- Overall Precision: 0.0
- Overall Recall: 0.0
- Overall F1: 0.0
- Overall Accuracy: 0.9050

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 5e-05
- train_batch_size: 8
- eval_batch_size: 8
- seed: 42
- optimizer: Adam with betas=(0.9,0.999) and epsilon=1e-08
- lr_scheduler_type: linear
- num_epochs: 3.0

### Training results

| Training Loss | Epoch | Step | Validation Loss | Alti Precision | Alti Recall | Alti F1 | Alti Number | Geog Precision | Geog Recall | Geog F1 | Geog Number | Region Precision | Region Recall | Region F1 | Region Number | Site Precision | Site Recall | Site F1 | Site Number | Taxa Precision | Taxa Recall | Taxa F1 | Taxa Number | Overall Precision | Overall Recall | Overall F1 | Overall Accuracy |
|:-------------:|:-----:|:----:|:---------------:|:--------------:|:-----------:|:-------:|:-----------:|:--------------:|:-----------:|:-------:|:-----------:|:----------------:|:-------------:|:---------:|:-------------:|:--------------:|:-----------:|:-------:|:-----------:|:--------------:|:-----------:|:-------:|:-----------:|:-----------------:|:--------------:|:----------:|:----------------:|
| No log        | 1.0   | 1    | 1.6856          | 0.0            | 0.0         | 0.0     | 0           | 0.0            | 0.0         | 0.0     | 0           | 0.0              | 0.0           | 0.0       | 3             | 0.0            | 0.0         | 0.0     | 1           | 0.0            | 0.0         | 0.0     | 0           | 0.0               | 0.0            | 0.0        | 0.7828           |
| No log        | 2.0   | 2    | 1.1613          | 0.0            | 0.0         | 0.0     | 0           | 0.0            | 0.0         | 0.0     | 3           | 0.0              | 0.0           | 0.0       | 1             | 0.0            | 0.0         | 0.0     | 0           | 0.0            | 0.0         | 0.0     | 0.8733      |
| No log        | 3.0   | 3    | 0.9913          | 0.0            | 0.0         | 0.0     | 0           | 0.0            | 0.0         | 0.0     | 3           | 0.0              | 0.0           | 0.0       | 1             | 0.0            | 0.0         | 0.0     | 0           | 0.0            | 0.0         | 0.0     | 0.9050      |


### Framework versions

- Transformers 4.29.2
- Pytorch 1.12.1
- Datasets 2.12.0
- Tokenizers 0.13.3
