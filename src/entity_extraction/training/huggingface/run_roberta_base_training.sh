#!/usr/bin/env sh 

# if running with conda envs, remove if not
conda activate ffossils

echo python.__version__ = $(python -c 'import sys; print(sys.version)')
# ensure we're in the MetaExtractor root directory
echo "Current working directory: $(pwd)"

# what base model should be used from the huggingface library
# see https://huggingface.co/models for options
export MODEL_NAME_OR_PATH="roberta-base"
# what the end model should be called, this is used for logging and saving
export FINAL_MODEL_NAME="metaextractor"

# set the location of the labelled data, ideally this is run from root of repo
# leave test_split at non_zero value to ensure test set is created for evaluation
export RAW_LABELLED_FILE_LOCATION="/data/entity-extraction/raw/sample-labelstudio-output/"
export PROCESSED_LABELS_LOCATION="/data/entity-extraction/processed/sample-processed-labelstudio/"
export MODEL_OUTPUT_DIR="/models/ner/test-finetuning/"
export MODEL_LOG_DIR="/models/ner/test-finetuning/logs/"

# comment the following in/out if MLflow server is available/.env file setup
# export MLFLOW_EXPERIMENT_NAME="test-hf-token-classification"
# whether to export and log model weights
# set to 0 if trialling tuning for metrics, set to 1 to log full model wieghts and files
export HF_MLFLOW_LOG_ARTIFACTS="0"
# general settings, don't change if using mlflow
export MLFLOW_FLATTEN_PARAMS="2" # azure mlflow has a limit of 200 params, leveing this nested gets around it
export AZUREML_ARTIFACTS_DEFAULT_TIMEOUT="3600" # large file upload times reuqire longer time out

# split up the labelled data by GDD ID and create train/val/test splits
python src/entity_extraction/preprocessing/labelling_data_split.py \
    --raw_label_path "$(pwd)$RAW_LABELLED_FILE_LOCATION" \
    --output_path "$(pwd)$PROCESSED_LABELS_LOCATION" \
    --train_split 0.7 \
    --val_split 0.15 \
    --test_split 0.15 

# split labelled files into training chunks
# max_seq_length - how many words are in each chunk, ensures once tokenized each is less than 512
# stride - how many words overlap between chunks, ensures context is maximized
python src/entity_extraction/preprocessing/huggingface_preprocess.py \
    --label_files "$(pwd)$PROCESSED_LABELS_LOCATION" \
    --max_seq_length 256 \
    --stride 196

# Kick off the training script. Use max_train_samples and max_eval_samples for local CPU testing
python src/entity_extraction/training/huggingface/ner_training.py \
    --seed 42 \
    --load_best_model_at_end True \
    --metric_for_best_model overall_f1 \
    --run_name finetuning-logging \
    --model_name_or_path "$MODEL_NAME_OR_PATH" \
    --output_dir "$(pwd)$MODEL_OUTPUT_DIR" \
    --logging_dir "$(pwd)$MODEL_LOG_DIR" \
    --train_file "$(pwd)$PROCESSED_LABELS_LOCATION/train.json" \
    --validation_file "$(pwd)$PROCESSED_LABELS_LOCATION/val.json" \
    --text_column_name tokens \
    --label_column_name ner_tags \
    --label_all_tokens True \
    --return_entity_level_metrics True \
    --do_train \
    --do_eval \
    --overwrite_output_dir \
    --save_strategy steps \
    --logging_strategy steps \
    --evaluation_strategy steps \
    --logging_steps 10 \
    --save_steps 100 \
    --eval_steps 25 \
    --learning_rate 2e-5 \
    --max_seq_length 512 \
    --num_train_epochs 2 \
    --per_device_train_batch_size 8 \
    --gradient_accumulation_steps 8 \
    --warmup_steps 100 \
    --max_train_samples 1 \
    --max_eval_samples 1 


# all options, see here for huggingface description of all arguments: https://huggingface.co/docs/transformers/main_classes/trainer#transformers.TrainingArguments
# usage: run_ner.py [-h] 
#                   --model_name_or_path MODEL_NAME_OR_PATH 
#                   [--config_name CONFIG_NAME] 
#                   [--tokenizer_name TOKENIZER_NAME] 
#                   [--cache_dir CACHE_DIR] 
#                   [--model_revision MODEL_REVISION]
#                   [--use_auth_token [USE_AUTH_TOKEN]] 
#                   [--ignore_mismatched_sizes [IGNORE_MISMATCHED_SIZES]] 
#                   [--task_name TASK_NAME] 
#                   [--dataset_name DATASET_NAME] 
#                   [--dataset_config_name DATASET_CONFIG_NAME]    
#                   [--train_file TRAIN_FILE] 
#                   [--validation_file VALIDATION_FILE] 
#                   [--test_file TEST_FILE] 
#                   [--text_column_name TEXT_COLUMN_NAME] 
#                   [--label_column_name LABEL_COLUMN_NAME]
#                   [--overwrite_cache [OVERWRITE_CACHE]] 
#                   [--preprocessing_num_workers PREPROCESSING_NUM_WORKERS] 
#                   [--max_seq_length MAX_SEQ_LENGTH] 
#                   [--pad_to_max_length [PAD_TO_MAX_LENGTH]]
#                   [--max_train_samples MAX_TRAIN_SAMPLES] 
#                   [--max_eval_samples MAX_EVAL_SAMPLES] 
#                   [--max_predict_samples MAX_PREDICT_SAMPLES] 
#                   [--label_all_tokens [LABEL_ALL_TOKENS]]
#                   [--return_entity_level_metrics [RETURN_ENTITY_LEVEL_METRICS]] 
#                   [--num_epochs NUM_EPOCHS] 
#                   [--batch_size BATCH_SIZE] --output_dir OUTPUT_DIR [--overwrite_output_dir [OVERWRITE_OUTPUT_DIR]]      
#                   [--do_train [DO_TRAIN]] 
#                   [--do_eval [DO_EVAL]] 
#                   [--do_predict [DO_PREDICT]] 
#                   [--evaluation_strategy {no,steps,epoch}] 
#                   [--prediction_loss_only [PREDICTION_LOSS_ONLY]]
#                   [--per_device_train_batch_size PER_DEVICE_TRAIN_BATCH_SIZE] 
#                   [--per_device_eval_batch_size PER_DEVICE_EVAL_BATCH_SIZE] 
#                   [--per_gpu_train_batch_size PER_GPU_TRAIN_BATCH_SIZE]
#                   [--per_gpu_eval_batch_size PER_GPU_EVAL_BATCH_SIZE] 
#                   [--gradient_accumulation_steps GRADIENT_ACCUMULATION_STEPS] 
#                   [--eval_accumulation_steps EVAL_ACCUMULATION_STEPS] 
#                   [--eval_delay EVAL_DELAY]  
#                   [--learning_rate LEARNING_RATE] 
#                   [--weight_decay WEIGHT_DECAY] 
#                   [--adam_beta1 ADAM_BETA1] 
#                   [--adam_beta2 ADAM_BETA2] 
#                   [--adam_epsilon ADAM_EPSILON] 
#                   [--max_grad_norm MAX_GRAD_NORM]
#                   [--num_train_epochs NUM_TRAIN_EPOCHS] 
#                   [--max_steps MAX_STEPS]
#                   [--lr_scheduler_type {linear,cosine,cosine_with_restarts,polynomial,constant,constant_with_warmup,inverse_sqrt,reduce_lr_on_plateau}] 
#                   [--warmup_ratio WARMUP_RATIO]
#                   [--warmup_steps WARMUP_STEPS] 
#                   [--log_level {debug,info,warning,error,critical,passive}] 
#                   [--log_level_replica {debug,info,warning,error,critical,passive}]
#                   [--log_on_each_node [LOG_ON_EACH_NODE]] 
#                   [--no_log_on_each_node] 
#                   [--logging_dir LOGGING_DIR] 
#                   [--logging_strategy {no,steps,epoch}] 
#                   [--logging_first_step [LOGGING_FIRST_STEP]]
#                   [--logging_steps LOGGING_STEPS] 
#                   [--logging_nan_inf_filter [LOGGING_NAN_INF_FILTER]] 
#                   [--no_logging_nan_inf_filter] 
#                   [--save_strategy {no,steps,epoch}] 
#                   [--save_steps SAVE_STEPS]
#                   [--save_total_limit SAVE_TOTAL_LIMIT] 
#                   [--save_safetensors [SAVE_SAFETENSORS]] 
#                   [--save_on_each_node [SAVE_ON_EACH_NODE]] 
#                   [--no_cuda [NO_CUDA]] 
#                   [--use_mps_device [USE_MPS_DEVICE]]
#                   [--seed SEED] 
#                   [--data_seed DATA_SEED] 
#                   [--jit_mode_eval [JIT_MODE_EVAL]] 
#                   [--use_ipex [USE_IPEX]] 
#                   [--bf16 [BF16]] 
#                   [--fp16 [FP16]] 
#                   [--fp16_opt_level FP16_OPT_LEVEL]
#                   [--half_precision_backend {auto,cuda_amp,apex,cpu_amp}] 
#                   [--bf16_full_eval [BF16_FULL_EVAL]] 
#                   [--fp16_full_eval [FP16_FULL_EVAL]] 
#                   [--tf32 TF32] 
#                   [--local_rank LOCAL_RANK]
#                   [--ddp_backend {nccl,gloo,mpi,ccl}] 
#                   [--tpu_num_cores TPU_NUM_CORES] 
#                   [--tpu_metrics_debug [TPU_METRICS_DEBUG]] 
#                   [--debug DEBUG] 
#                   [--dataloader_drop_last [DATALOADER_DROP_LAST]]
#                   [--eval_steps EVAL_STEPS] 
#                   [--dataloader_num_workers DATALOADER_NUM_WORKERS] 
#                   [--past_index PAST_INDEX] 
#                   [--run_name RUN_NAME] 
#                   [--disable_tqdm DISABLE_TQDM]
#                   [--remove_unused_columns [REMOVE_UNUSED_COLUMNS]] 
#                   [--no_remove_unused_columns] 
#                   [--label_names LABEL_NAMES [LABEL_NAMES ...]] 
#                   [--load_best_model_at_end [LOAD_BEST_MODEL_AT_END]]
#                   [--metric_for_best_model METRIC_FOR_BEST_MODEL] 
#                   [--greater_is_better GREATER_IS_BETTER] 
#                   [--ignore_data_skip [IGNORE_DATA_SKIP]] 
#                   [--sharded_ddp SHARDED_DDP] 
#                   [--fsdp FSDP]
#                   [--fsdp_min_num_params FSDP_MIN_NUM_PARAMS] 
#                   [--fsdp_config FSDP_CONFIG] 
#                   [--fsdp_transformer_layer_cls_to_wrap FSDP_TRANSFORMER_LAYER_CLS_TO_WRAP] 
#                   [--deepspeed DEEPSPEED]
#                   [--label_smoothing_factor LABEL_SMOOTHING_FACTOR] 
#                   [--optim {adamw_hf,adamw_torch,adamw_torch_fused,adamw_torch_xla,adamw_apex_fused,adafactor,adamw_bnb_8bit,adamw_anyprecision,sgd,adagrad}]  
#                   [--optim_args OPTIM_ARGS] 
#                   [--adafactor [ADAFACTOR]] 
#                   [--group_by_length [GROUP_BY_LENGTH]] 
#                   [--length_column_name LENGTH_COLUMN_NAME] 
#                   [--report_to REPORT_TO [REPORT_TO ...]]
#                   [--ddp_find_unused_parameters DDP_FIND_UNUSED_PARAMETERS] 
#                   [--ddp_bucket_cap_mb DDP_BUCKET_CAP_MB] 
#                   [--dataloader_pin_memory [DATALOADER_PIN_MEMORY]] 
#                   [--no_dataloader_pin_memory]
#                   [--skip_memory_metrics [SKIP_MEMORY_METRICS]] 
#                   [--no_skip_memory_metrics] 
#                   [--use_legacy_prediction_loop [USE_LEGACY_PREDICTION_LOOP]] 
#                   [--push_to_hub [PUSH_TO_HUB]]
#                   [--resume_from_checkpoint RESUME_FROM_CHECKPOINT] 
#                   [--hub_model_id HUB_MODEL_ID] 
#                   [--hub_strategy {end,every_save,checkpoint,all_checkpoints}] 
#                   [--hub_token HUB_TOKEN]
#                   [--hub_private_repo [HUB_PRIVATE_REPO]] 
#                   [--gradient_checkpointing [GRADIENT_CHECKPOINTING]] 
#                   [--include_inputs_for_metrics [INCLUDE_INPUTS_FOR_METRICS]]
#                   [--fp16_backend {auto,cuda_amp,apex,cpu_amp}] 
#                   [--push_to_hub_model_id PUSH_TO_HUB_MODEL_ID] 
#                   [--push_to_hub_organization PUSH_TO_HUB_ORGANIZATION] 
#                   [--push_to_hub_token PUSH_TO_HUB_TOKEN]      
#                   [--mp_parameters MP_PARAMETERS] 
#                   [--auto_find_batch_size [AUTO_FIND_BATCH_SIZE]] 
#                   [--full_determinism [FULL_DETERMINISM]] 
#                   [--torchdynamo TORCHDYNAMO] 
#                   [--ray_scope RAY_SCOPE]
#                   [--ddp_timeout DDP_TIMEOUT] 
#                   [--torch_compile [TORCH_COMPILE]] 
#                   [--torch_compile_backend TORCH_COMPILE_BACKEND] 
#                   [--torch_compile_mode TORCH_COMPILE_MODE] 
#                   [--xpu_backend {mpi,ccl,gloo}]

