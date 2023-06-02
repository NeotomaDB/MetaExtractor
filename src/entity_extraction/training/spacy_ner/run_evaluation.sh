#!/usr/bin/env sh 

# if running with conda envs, comment out if not
conda activate fossil_lit

echo python.__version__ = $(python -c 'import sys; print(sys.version)')
# ensure we're in the MetaExtractor root directory
echo "Current working directory: $(pwd)"

# set the location of the labelled data, ideally this is run from root of repo
export DATA_DIR="$(pwd)/data/entity-extraction/processed/2023-05-31_label-export_39-articles/val"
export MODEL_PATH="$(pwd)/models/ner/transformer-v3"
export OUTPUT_DIR="$(pwd)/results/ner/test-results/"
export MODEL_NAME="spacy-transformer-v3"
export GPU=False

# process the labelled files to prepare them for training
python src/entity_extraction/training/spacy_ner/spacy_evaluate.py \
    --data_path "$DATA_DIR" \
    --model_path "$MODEL_PATH" \
    --output_path "$OUTPUT_DIR" \
    --model_name "$MODEL_NAME" \
    --gpu "$GPU"
# use this for gpu testing