# Label Studio Setup & Usage

This is a guide to setting up and using Label Studio for the purpose of annotating data for the entity extraction model.

The finding fossils team setup a privately hosted version of LabelStudio using HuggingFace spaces. The main steps were:

**Table of Contents**

- [Label Studio Setup \& Usage](#label-studio-setup--usage)
  - [Create Azure Blob Storage](#create-azure-blob-storage)
  - [Setup Postgres Database](#setup-postgres-database)
  - [Setup Label Studio External Storage](#setup-label-studio-external-storage)

## Create Azure Blob Storage

1. Create an Azure blob storage container to house both the data to be labelled as well as the output labelled files.
   1. Use this guide: [Azure Quickstart Upload/Download Blobs](https://www.google.com/search?q=create+azure+blob+storage+container&rlz=1C1RXQR_enCA1013CA1013&oq=create+azure+blob+storage+container&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIICAEQABgWGB4yCAgCEAAYFhgeMggIAxAAGBYYHjIICAQQABgWGB4yCAgFEAAYFhgeMggIBhAAGBYYHjIICAcQABgWGB4yCAgIEAAYFhgeMggICRAAGBYYHtIBCDc0OTZqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8)
2. To create `raw` and `labelled` folders in the blob storage, create a blank TXT file and upload it.
   1. Under the advanced tab put the desired folder name in the `Upload to folder` field, the folder will be created then uploaded there.
3. Repeat step 3 for `labelled` folder

Update the "Resource Sharing (CORS)" settings of the blob storage following the LabelStudio "Prerequisites" section here: https://labelstud.io/guide/storage.html#Microsoft-Azure-Blob-storage

## Setup Postgres Database

Create a "Azure Database for PostgreSQL - Flexible Server" to take advantage of 750hrs free compute time and should be able to run the database free each month.

- **MAKE SURE YOU REMEMBER THE ADMIN ACCOUNT NAME AND PASSWORD**

Create a database once the postgres instance is up and running. e.g. `labelstudiodev`.

Install the Postgres Azure extensions required by LabelStudio:

1. Follow section "How to use PostgreSQL extensions" section from the Azure docs here: https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-extensions
   - `pg_trgm` - postgres trigram text extension
   - `btree_gin` - support for indexing common datatypes in GIN

In label studio, follow the instructions under section "Enable Configuration Persistance" and set the required environment variables under settings in label studio:
https://huggingface.co/docs/hub/spaces-sdks-docker-label-studio

- `DJANGO_DB`: Set this to `default`.
- `POSTGRE_NAME`: Set this to the name of the Postgres database.
- `POSTGRE_USER`: Set this to the Postgres username.
- `POSTGRE_PASSWORD`: Set this to the password for your Postgres user.
- `POSTGRE_HOST`: Set this to the host that your Postgres database is running on.
  - On Azure this is under Overview and is called "Server name", e.g. `findingfossilslabelstudio.postgres.database.azure.com`
- `POSTGRE_PORT`: Set this to the port that your Pogtgres database is running on. Defualt is 5432, use this.
- `STORAGE_PERSISTENCE`: Set this to `1` to remove the warning about ephemeral storage.

## Setup Label Studio External Storage

Inside the Label Studio instance

- **Storage title**: Chosen name to be displayed in LS
- **Container name**: the Azure blob container name
  - finding-fossils-labelling-dev
- **Container prefix**: folder path within the contatiner for which to load the data from
  - labelling-raw
- **File filter Regex**: pattern matching, .\* for all files
- **Accountname**: name of storage account
  - findingfossilsdev
- **Account key**: from Azure storage page --> Access keys
