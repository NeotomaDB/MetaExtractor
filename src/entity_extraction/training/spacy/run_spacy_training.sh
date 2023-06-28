#!/usr/bin/env sh 

# if running with conda envs, comment out if not
conda activate fossil_lit

echo python.__version__ = $(python -c 'import sys; print(sys.version)')
# ensure we're in the MetaExtractor root directory
echo "Current working directory: $(pwd)"

DATA_PATH="/path/to/sample input folder"
DATA_OUTPUT_PATH="/path/to/sample output folder"
MODEL_PATH="/path/to/model artifacts"
MODEL_OUTPUT_PATH="/path/to/new model artifacts"
VERSION="v1"
TRAIN_SPLIT=0.7
VAL_SPLIT=0.15
TEST_SPLIT=0.15


rm -f src/entity_extraction/training/spacy/spacy_transformer_$VERSION.cfg

python3 src/entity_extraction/preprocessing/labelling_data_split.py \
        --raw_label_path $DATA_PATH \
        --output_path $DATA_OUTPUT_PATH \
        --train_split $TRAIN_SPLIT \
        --val_split $VAL_SPLIT \
        --test_split $TEST_SPLIT

python3 src/preprocessing/spacy_preprocess.py --data_path $DATA_OUTPUT_PATH

if [ -z "$MODEL_PATH" ]; then
    # If the model path is null, then start training from scratch

    # Fill configuration with required fields
    python -m spacy init fill-config \
            src/entity_extraction/training/spacy/spacy_transformer_train.cfg \
            src/entity_extraction/training/spacy/spacy_transformer_$VERSION.cfg

    # Execute the training job by pointing to the new config file
    python -m spacy train \
        src/entity_extraction/training/spacy/spacy_transformer_$VERSION.cfg \
        --paths.train $DATA_OUTPUT_PATH/train.spacy \
        --paths.dev $DATA_OUTPUT_PATH/val.spacy \
        --output $MODEL_OUTPUT_PATH \
        --gpu-id -1

else
    # Else create a new config file to resume training
    python src/entity_extraction/training/spacy/create_config.py \
        --model_path $MODEL_PATH \
        --output_path src/entity_extraction/training/spacy/spacy_transformer_$VERSION.cfg

    python -m spacy train \
        src/entity_extraction/training/spacy/spacy_transformer_$VERSION.cfg \
        --paths.train $DATA_OUTPUT_PATH/train.spacy \
        --paths.dev $DATA_OUTPUT_PATH/val.spacy \
        --components.ner.source $MODEL_PATH \
        --components.transformer.source $MODEL_PATH \
        --output $MODEL_OUTPUT_PATH \
        --gpu-id -1
fi