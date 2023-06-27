# **Preprocessing**

This readme file provides an overview of the multiple scripts under the **preprocessing** directory. It contains various Python scripts that are used for various data preprocessing tasks, from labeling to training. Below, you will find information about the purpose of the scripts and instructions on how to use them.

**Table of Contents**
- [Setup](#setup)
- [Usage](#usage)
    - [Tagging](#labelling-preprocessing)
        - [Labelling Preprocessing](#labelling-preprocessing)
    - [Training](#)
        - [Labelling Data Splitting](#labelling-data-splitting)
        - [SpaCy Preprocessing](#spacy-preprocessing)

---

## **Setup**
Feel free to explore each script to understand their functionalities. These python scripts are part of bash scripts that execute a set of steps, and hence need not be executed independently. However, utilize them based on your specific preprocessing needs using the commands below. 

To use the preprocessing scripts, follow these steps:

1. Ensure that you have the environment enabled and dependencies installed.

2. Place your input data files in the folder and provide the appropriate paths as input arguments.

3. Specify other mandatory parameters (as defined below).

5. Run the script to execute the preprocessing tasks on your data.

---

## **Usage**
---

### **Labelling Preprocessing**
To use the `labelling_preprocessing.py` script, execute the command below and replace all the appropriate input arguments:

```bash
python3 labelling_preprocessing.py --model_version <model_version> --output_path <output_path> [--model_path <model_path>] [--data_path <--data_path>][--bib_path <bib_path>] [--sentences_path <sentences_path>] [--char_len <char_len>] [--min_len <min_len>]
```

#### **Description**

This script takes the original article text as input and generates labels resulting in JSON files that can be uploaded to LabelStudio for further annotation or analysis. It performs the following tasks:

1. Splits the article text into smaller chunks based on the specified character length.

2. Creates JSON files for each chunk, containing the required fields for LabelStudio.

3. Assigns a unique identifier to each chunk.

4. Adds metadata from the bibjson file, if provided.

5. Utilizes a specified model version, if provided, to generate labels.

#### **Options**

- `--model_version=<model_version>`: Specify the model version used to generate labels.

- `--output_path=<output_path>`: Specify the path to the output directory where the generated labels will be stored for uploading to LabelStudio.

- `--model_path=<model_path>` (optional): Specify the path to the model artifacts to use for label generation. If not specified, only chunking is performed.

- `--data_path=<--data_path>` (optional): Specify the path to a CSV file containing full text articles.

- `--bib_path=<bib_path>` (optional): Specify the path to the bibjson file containing article metadata.

- `--sentences_path=<sentences_path>` (optional): Specify the path to the sentences_nlp file that contains all sentences as returned by xDD.

- `--char_len=<char_len>` (optional): Specify the desired length (in characters) for each chunk when splitting a section of the article. Default value is 4000.

- `--min_len=<min_len>` (optional): Specify the minimum length (in characters) for a section. If a section is smaller than this value, it will be combined with the next section. Default value is 1500.

Note: Either `--data_path` or both `--bib_path` and `--sentences_path` must be specified to locate the input data to preprocess for labeling.

---

### **Labelling Data Splitting**

To use the `labelling_data_split.py` script, execute the command below and replace all the appropriate input arguments:

```bash
python3 labelling_data_split.py --raw_label_path=<raw_label_path> --output_path=<output_path> [--train_split=<train_split>] [--val_split=<val_split>] [--test_split=<test_split>]
```

#### **Description**
This script takes labelled dataset in JSONLines format as input and splits it into separate train, validation, and test sets. It performs the following tasks:

1. Reads the labelled text from the specified `raw_label_path` directory.

2. Randomly divides the data into train, validation, and test sets based on the provided split percentages.

3. Writes the divided datasets into separate folders as separate JSON files in the specified `output_path` directory.

The resulting train, validation, and test sets can be used for training and evaluating machine learning models.

#### **Options**
- `--raw_label_path=<raw_label_path>`: Specify the path to the directory where the raw label files are located.

- `--output_path=<output_path>`: Specify the path to the directory where the output files will be written.

- `--train_split=<train_split>` (optional): Specify the percentage of examples to dedicate to the train set. The default value is 0.7 (70%).

- `--val_split=<val_split>` (optional): Specify the percentage of examples to dedicate to the validation set. The default value is 0.15 (15%).

- `--test_split=<test_split>` (optional): Specify the percentage of examples to dedicate to the test set. The default value is 0.15 (15%).

---

### **SpaCy Preprocessing**

To use the `spacy_preprocess.py` script, execute the command below and replace all the appropriate input arguments:

```bash
python3 spacy_preprocess.py --data_path=<data_path>
```

#### **Description**
This script manages the creation of custom data artifacts required for training and fine-tuning spaCy models. It performs the following tasks:

1. Reads the dataset in JSONLines format from the specified `data_path`.

2. Creates spans of entities from the labelled files.

3. Converts the tagged data into spaCy-compatible format, such as converting it to Doc or DocBin objects.

4. Creates the custom data artifacts that can be used for training or fine-tuning spaCy models.

#### **Options**
- `--data_path=<data_path>`: Specify the path to the folder containing files in JSONLines format.