#!/usr/bin/env sh 

# if running with conda envs, comment out if not
conda activate ffossils

echo python.__version__ = $(python -c 'import sys; print(sys.version)')
# ensure we're in the MetaExtractor root directory
echo "Current working directory: $(pwd)"

# set the location of the labelled data, ideally this is run from root of repo
export DATA_DIR="$(pwd)/data/entity-extraction/processed/2023-05-31_label-export_39-articles/"
export MODEL_PATH="$(pwd)/models/ner/roberta-finetuned/checkpoint-750"
export OUTPUT_DIR="$(pwd)/results/ner/test-results/"
export MODEL_NAME="roberta-finetuned"

# process the labelled files to prepare them for training
python src/entity_extraction/training/hf_token_classification/hf_evaluate.py \
    --data_path "$DATA_DIR" \
    --model_path "$MODEL_PATH" \
    --output_path "$OUTPUT_DIR" \
    --model_name "$MODEL_NAME" \
    --max_samples 1

# use this for local cpu testing
    # --max_samples 1