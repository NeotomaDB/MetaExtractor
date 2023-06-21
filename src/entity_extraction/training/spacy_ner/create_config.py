# Author: Jenit Jain
# Date: 2023-06-21
# Inspired from https://github.com/explosion/projects/blob/v3/pipelines/ner_demo_update/scripts/create_config.py
"""This script create a config file when resuming training of a spacy model from a past checkpoint

Usage: create_config.py --model_path=<model_path> --output_path=<output_path>

Options:
    --model_path=<model_path>         The path to the model artifacts.
    --output_path=<output_path>       The path to the output config file.
"""

from pathlib import Path
from docopt import docopt
import spacy

opt = docopt(__doc__)

def create_config():
    
    spacy.require_cpu()
    nlp = spacy.load(opt["--model_path"])

    # create a new config as a copy of the loaded pipeline's config
    config = nlp.config.copy()

    # source all components from the loaded pipeline and freeze all except the
    # component to update; replace the listener for the component that is
    # being updated so that it can be updated independently
    config["components"]["ner"] = {
        "source": opt["--model_path"],
    }
    config["components"]["transformer"] = {
        "source": opt["--model_path"],
    }
    # save the config
    config.to_disk(opt["--output_path"])
    
if __name__ == "__main__":
    create_config()