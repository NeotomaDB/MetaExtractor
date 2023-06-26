# Label Studio Setup & Usage

This is a guide to setting up and using Label Studio for the purpose of annotating data for the entity extraction model.

The finding fossils team setup a privately hosted version of LabelStudio using HuggingFace spaces. The main steps were:

**Table of Contents**

- [Label Studio Setup](#label-studio-setup--usage)
  - [Create Azure Blob Storage](#create-azure-blob-storage)
  - [Setup Postgres Database](#setup-postgres-database)
  - [Setup Label Studio External Storage](#setup-label-studio-external-storage)
- [Label Studio Usage](#labeling-instructions)
  - [Account creation](#create-account)
  - [Navigation](#navigation)
  - [Labeling](#labeling)
---
## **Label Studio Setup**
---
### **Create Azure Blob Storage**

1. Create an Azure blob storage container to house both the data to be labelled as well as the output labelled files.
   1. Use this guide: [Azure Quickstart Upload/Download Blobs](https://www.google.com/search?q=create+azure+blob+storage+container&rlz=1C1RXQR_enCA1013CA1013&oq=create+azure+blob+storage+container&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIICAEQABgWGB4yCAgCEAAYFhgeMggIAxAAGBYYHjIICAQQABgWGB4yCAgFEAAYFhgeMggIBhAAGBYYHjIICAcQABgWGB4yCAgIEAAYFhgeMggICRAAGBYYHtIBCDc0OTZqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8)
2. Create a `raw` folder in the blob storage by specifying the folder name in the `Upload to folder` field under the advanced tab, and upload a blank TXT file to it (as a placeholder).
3. Repeat step 3 for `labelled` folder

To allow LabelStudio to access the objects stored in the bucket, update the `Resource Sharing (CORS)` settings of the blob storage following the LabelStudio *Prerequisites* section [here](https://labelstud.io/guide/storage.html#Microsoft-Azure-Blob-storage).

---

### **Setup PostgreSQL Database**

1. Create a **Azure Database for PostgreSQL - Flexible Server** to take advantage of 750 hours of free compute time, which should be able to run the database free each month. \
**MAKE SURE YOU REMEMBER THE ADMIN ACCOUNT NAME AND PASSWORD** 

2. Create a database once the postgres instance is up and running. e.g. `labelstudiodev`.

3. Install the Postgres Azure extensions required by LabelStudio. \
Follow section **How to use PostgreSQL extensions** section from the Azure docs [here](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-extensions)
   - `pg_trgm` - postgres trigram text extension
   - `btree_gin` - support for indexing common datatypes in GIN

In Label Studio, follow the instructions under section **Enable Configuration Persistance** and set the required [environment variables](https://huggingface.co/docs/hub/spaces-sdks-docker-label-studio) under settings in label studio.

- `DJANGO_DB`: Set this to `default`.
- `POSTGRE_NAME`: Set this to the name of the Postgres database.
- `POSTGRE_USER`: Set this to the Postgres username.
- `POSTGRE_PASSWORD`: Set this to the password for your Postgres user.
- `POSTGRE_HOST`: Set this to the host that your Postgres database is running on.
  - On Azure this is under Overview and is called **Server name**, e.g. `findingfossilslabelstudio.postgres.database.azure.com`
- `POSTGRE_PORT`: Set this to the port that your Pogtgres database is running on. Default is 5432 (**recommended**).
- `STORAGE_PERSISTENCE`: Set this to `1` to remove the warning about ephemeral storage.

---

### **Setup Label Studio External Storage**

Inside the Label Studio instance

- **Storage title**: Chosen name to be displayed in LS
- **Container name**: the Azure blob container name
  - `finding-fossils-labelling-dev`
- **Container prefix**: folder path within the contatiner for which to load the data from
  - `labelling-raw`
- **File filter Regex**: pattern matching, `.\*` for all files
- **Accountname**: name of storage account
  - `findingfossilsdev`
- **Account key**: from Azure storage page --> Access keys

---

## **Label Studio Usage**
---
### **Account creation**

1. Create a Hugging Face hub account: https://huggingface.co/join
2. Send your profile name to *Ty Andrews* to be added to the **Finding Fossils organization** on Hugging Face
Email: ty.elgin.andrews@gmail.com, or create a new organization for a different project to work collaboratively with teammates.
3. Once in the organization, navigate to the organization page from your profile.
![Organization navigation](../../assets/org_nav.png)

4. In the organization page, click the space 
**LabelStudio**.
![LabelStudio tab](../../assets/labelstudio_tab.png)

5. Create a LabelStudio account and record your password in your password manager.
![Create Account](../../assets/account_creation.png)

### **Navigation**

1. Open the **Green** project named like **Finding Fossils Labelling - Production** or create a new one.
![Project tab](../../assets/green_tab.png)

2. Navigate to the settings menu of the project. Here, several options are available to tweak the settings to be compatible for your task,
![Project Settings](../../assets/settings.png)

  - Review or create labelling instructions.
  ![Labeling instructions button](../../assets/labeling_instructions_button.png)
  - The instructions look like this:
  ![Labeling instructions](../../assets/labeling_instructions.png)

  - Labeling configuration:
After syncing the buckets, the final step is to define the different categories of entities that the named entity recognition model will be trained to predict. A configuration file is used to define the classes and to initialize the UI components to aid a user label entities. A sample config file has the following tags:
```html
<View>
  <View style="display:flex;align-items:start;gap:8px;flex-direction:row-reverse">
    <Text name="text" valueType="text" value="$text" granularity="word"/>
    <Labels name="label" toName="text" showInline="false">
      <Label value="SITE" background="#336cf0"/>
      <Label value="GEOG" background="#D4380D"/>
      <Label value="AGE" background="#f0c528"/>
      <Label value="ALTI" background="#86d425"/>
      <Label value="TAXA" background="#925ff2"/>
      <Label value="EMAIL" background="#ff941a"/>
    <Label value="REGION" background="#ff9ee5"/></Labels>
  </View>
</View>
```
For more information about config files to setup a custom LabelStudio NER labeling task, refer the [this documentation](https://labelstud.io/templates/named_entity.html).

For general information, [visit LabelStudios templates page.](https://labelstud.io/templates/index.html).

### **Labeling**

1. Select the task with **global_index** of 0, the **global index** indicates this is the start of the article and start labelling each task by moving onto the next **global_index** number.
![Global Index of tasks](../../assets/global_index.png)
- **Ensure pre-labelled entities are correct and/or fix:** we have tried to auto-tag entities to make this faster but it’s not perfect and this is what we’re improving, so this commonly misses entities or gets them partially right.
- **Label any missed entities:** these can be things with typos, words being smushed together, etc.
2. **Using the labelling interface:**
![Labeling](../../assets/labeling.png)
3. **Correct a pre-labelled entity:**
- If it’s completely wrong, delete it 
  - Select the label
  - On the right bar click the delete button
- To fix a partial match
  - Delete the entity using above
  - Select the correct label and click/drag the correct span of text

  ![Correct Entity](../../assets/correct_labels.png)