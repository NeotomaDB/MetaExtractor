# MetaExtractor: Finding Fossils in the Literature

This project aims to identify research articles which are relevant to the [Neotoma Paleoecological Database](http://neotomadb.org) (Neotoma), extract data relevant to Neotoma from the article, and provide a mechanism for the data to be reviewed by Neotoma data stewards then submitted to Neotoma. It is being completed as part of the University of British Columbia (UBC) [Masters of Data Science (MDS) program](https://masterdatascience.ubc.ca/) in partnership with the [Neotoma Paleoecological Database](http://neotomadb.org).

## Contributors

This project is an open project, and contributions are welcome from any individual.  All contributors to this project are bound by a [code of conduct](https://github.com/NeotomaDB/MetaExtractor/blob/main/CODE_OF_CONDUCT.md).  Please review and follow this code of conduct as part of your contribution.

The UBC MDS project team consists of:
- Ty Andrews
- Kelly Wu
- Jenit Jain
- Shaun Hutchinson

Sponsors from Neotoma supporting the project are:
* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--7926--4935-brightgreen.svg)](https://orcid.org/0000-0002-7926-4935) [Socorro Dominguez Vidana](https://ht-data.com/)
* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605) [Simon Goring](http://www.goring.org)

### Tips for Contributing

Issues and bug reports are always welcome.  Code clean-up, and feature additions can be done either through pull requests to [project forks](https://github.com/NeotomaDB/MetaExtractor/network/members) or [project branches](https://github.com/NeotomaDB/MetaExtractor/branches).

All products of the Neotoma Paleoecology Database are licensed under an [MIT License](LICENSE) unless otherwise noted.

## How to use this repository

TBD


### Development Workflow Overview

TBD

### Analysis Workflow Overview

TBD

### System Requirements

TBD

### Data Requirements

TBD

### Directory Structure and Description

```
├── .github/                            <- Directory for GitHub files
│   ├── workflows/                      <- Directory for workflows
├── data/                               <- Directory for data
│   ├── entity-extraction/              <- Directory for named entity extraction data
│   │   ├── raw/                        <- Raw unprocessed data
│   │   ├── processed/                  <- Processed data
│   │   └── interim/                    <- Temporary data location
│   ├── article-relevance/              <- Directory for data related to article relevance prediction
│   │   ├── raw/                        <- Raw unprocessed data
│   │   ├── processed/                  <- Processed data
│   │   └── interim/                    <- Temporary data location
│   ├── data-review-tool/               <- Directory for data related to data review tool
│   │   ├── raw/                        <- Raw unprocessed data
│   │   ├── processed/                  <- Processed data
│   │   └── interim/                    <- Temporary data location
├── results/                            <- Directory for results
│   ├── article-relevance/              <- Directory for results related to article relevance prediction
│   ├── ner/                            <- Directory for results related to named entity recognition
│   └── data-review-tool/               <- Directory for results related to data review tool
├── notebooks/                          <- Directory for notebooks
├── src/                                <- Directory for source code
│   ├── entity_extraction/              <- Directory for named entity recognition code
│   ├── article_relevance/              <- Directory for article relevance prediction code
│   └── data_review_tool/               <- Directory for data review tool code             
├── reports/                            <- Directory for reports
├── tests/                              <- Directory for tests
├── Makefile                            <- Makefile with commands to perform analysis
└── README.md                           <- The top-level README for developers using this project.
```