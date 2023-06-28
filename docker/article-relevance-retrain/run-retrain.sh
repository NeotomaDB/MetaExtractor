#!/bin/bash

python src/relevance_prediction_model_retrain.py \
  --use_reviewed_data="$USE_REVIEWED_DATA" \
  --train_data_path="$TRAIN_DATA_PATH" \
  --model_folder="$MODEL_FOLDER" \
  --result_dir="$RESULT_DIR"\
  --reviewed_folder_path="$REVIEWED_FOLDER_PATH"