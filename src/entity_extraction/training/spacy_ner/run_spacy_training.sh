#!/usr/bin/env sh 

# if running with conda envs, comment out if not
conda activate fossil_lit

echo python.__version__ = $(python -c 'import sys; print(sys.version)')
# ensure we're in the MetaExtractor root directory
echo "Current working directory: $(pwd)"

# set the location of the labelled data, ideally this is run from root of repo
DATA_DIR="sample_folder"
TRAIN_SPLIT=0.7
VAL_SPLIT=0.15
TEST_SPLIT=0.15
MODEL_PATH=""
VERSION="v1"

rm -f spacy_transformer_$VERSION.cfg

python3 spacy_preprocess.py \
        --data_path $DATA_DIR \
        --train_split 0.7 \
        --val_split 0.15 \
        --test_split 0.15

if [ -z "$MODEL_PATH" ]; then
    # If the model path is null, then start training from scratch
    python -m spacy init fill-config spacy_transformer_train.cfg spacy_transformer_$VERSION.cfg
    python -m spacy train spacy_transformer_$VERSION.cfg \
        --paths.train $DATA_DIR/train/train.spacy \
        --paths.dev $DATA_DIR/val/val.spacy \
        --output ./output

else
    # Else create a new config file to resume training
    python create_config.py \
        --model_path $MODEL_PATH \
        --output_path spacy_transformer_$VERSION.cfg
    python -m spacy train spacy_transformer_$VERSION.cfg \
        --paths.train $DATA_DIR/train/train.spacy \
        --paths.dev $DATA_DIR/val/val.spacy \
        --components.ner.source $MODEL_PATH \
        --components.transformer.source $MODEL_PATH \
        --output ./output 
fi