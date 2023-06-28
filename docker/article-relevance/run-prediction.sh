#!/bin/bash

python src/article_relevance/gdd_api_query.py \
  --doi_path="$DOI_PATH" \
  --parquet_path="$PARQUET_PATH" \
  --n_recent="$N_RECENT" \
  --term="$TERM" \
  --min_date="$MIN_DATE" \
  --max_date="$MAX_DATE" \
  --auto_min_date="$AUTO_MIN_DATE" \
  --auto_check_dup="$AUTO_CHECK_DUP"

python src/article_relevance/relevance_prediction_parquet.py \
  --doi_file_path="$DOI_FILE_PATH" \
  --output_path="$OUTPUT_PATH" \
  --send_xdd="$SEND_XDD"