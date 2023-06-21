[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

# **MetaExtractor: Finding Fossils in the Literature**

This project aims to identify research articles which are relevant to the [*Neotoma Paleoecological Database*](http://neotomadb.org) (Neotoma), extract data relevant to Neotoma from the article, and provide a mechanism for the data to be reviewed by Neotoma data stewards then submitted to Neotoma. It is being completed as part of the *University of British Columbia (UBC)* [*Masters of Data Science (MDS)*](https://masterdatascience.ubc.ca/)  program in partnership with the [*Neotoma Paleoecological Database*](http://neotomadb.org).

There are 3 primary components to this project:
1. **Article Relevance Prediction** - get the latest articles published, predict which ones are relevant to Neotoma and submit for processing.
2. **MetaData Extraction Pipeline** - extract relevant entities from the article including geographic locations, taxa, etc. 
3. **Data Review Tool** - this takes the extracted data and allows the user to review and correct it for submission to Neotoma.

![](assets/project-flow-diagram.png)

## **Article Relevance Prediction**

The goal of this component is to monitor and identify new articles that are relevant to Neotoma. This is done by using the public [xDD API](https://geodeepdive.org/) to regularly get recently published articles. Article metadata is queried from the [CrossRef API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) to obtain data such as journal name, title, abstract and more. The article metadata is then used to predict whether the article is relevant to Neotoma or not. The predicted articles are then submitted to the Data Extraction Pipeline for processing.

## **Data Extraction Pipeline**

The full text is provided by the xDD team for the articles that are deemed to be relevant and a custom trained **Named Entity Recognition (NER)** model is used to extract entities of interest from the article. 

The entities extracted by this model are:
- **SITE**: name of the excavation site
- **REGION**: more general regions names to provide context for where sites are located
- **TAXA**: plant or animal fossil names
- **AGE**: historical age of the fossils, eg. 1234 AD, 4567 BP
- **GEOG**: geographic coordinates indicating the location of the site, eg. 12'34"N 34'23"W
- **EMAIL**: researcher emails referenced in the articles
- **ALTI**: altitudes of sites, eg. 123 m a.s.l (above sea level)

The model was trained on ~40 existing Paleoecology articles manually annotated by the team consisting of **~60,000 tokens** with **~4,500 tagged entities**.

The trained model is available for inference and further development on huggingface.co [here](https://huggingface.co/finding-fossils/metaextractor).
![](assets/hugging-face-metaextractor.png)

## **Data Review Tool**

Finally, the extracted data is loaded into the Data Review Tool where members of the Neotoma community can review the data and make any corrections necessary before submitting to Neotoma. The Data Review Tool is a web application built using the [Plotly Dash](https://dash.plotly.com/) framework. The tool allows users to view the extracted data, make corrections, and submit the data to be entered into Neotoma.

![](assets/data-review-tool.png)

## How to use this repository

WIP


### Development Workflow Overview

WIP

### Analysis Workflow Overview

WIP

### System Requirements

WIP

### Data Requirements

WIP

### **Directory Structure and Description**

```
├── .github/                            <- Directory for GitHub files
│   ├── workflows/                      <- Directory for workflows
├── assets/                             <- Directory for assets
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
├── models/                             <- Directory for models
│   ├── entity-extraction/              <- Directory for named entity recognition models
│   ├── article-relevance/              <- Directory for article relevance prediction models
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
## **Contributors**

This project is an open project, and contributions are welcome from any individual.  All contributors to this project are bound by a [code of conduct](https://github.com/NeotomaDB/MetaExtractor/blob/main/CODE_OF_CONDUCT.md). Please review and follow this code of conduct as part of your contribution.

The UBC MDS project team consists of:

- **Ty Andrews**
- **Kelly Wu**
- **Jenit Jain**
- **Shaun Hutchinson**

Sponsors from Neotoma supporting the project are:
* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--7926--4935-brightgreen.svg)](https://orcid.org/0000-0002-7926-4935) [Socorro Dominguez Vidana](https://ht-data.com/)
* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605) [Simon Goring](http://www.goring.org)

### Tips for Contributing

Issues and bug reports are always welcome.  Code clean-up, and feature additions can be done either through pull requests to [project forks](https://github.com/NeotomaDB/MetaExtractor/network/members) or [project branches](https://github.com/NeotomaDB/MetaExtractor/branches).

All products of the Neotoma Paleoecology Database are licensed under an [MIT License](LICENSE) unless otherwise noted.

[contributors-shield]: https://img.shields.io/github/contributors/NeotomaDB/MetaExtractor.svg?style=for-the-badge
[contributors-url]: https://github.com/NeotomaDB/MetaExtractor/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/NeotomaDB/MetaExtractor.svg?style=for-the-badge
[forks-url]: https://github.com/NeotomaDB/MetaExtractor/network/members
[stars-shield]: https://img.shields.io/github/stars/NeotomaDB/MetaExtractor.svg?style=for-the-badge
[stars-url]: https://github.com/NeotomaDB/MetaExtractor/stargazers
[issues-shield]: https://img.shields.io/github/issues/NeotomaDB/MetaExtractor.svg?style=for-the-badge
[issues-url]: https://github.com/NeotomaDB/MetaExtractor/issues
[license-shield]: https://img.shields.io/github/license/NeotomaDB/MetaExtractor.svg?style=for-the-badge
[license-url]: https://github.com/NeotomaDB/MetaExtractor/blob/master/LICENSE.txt