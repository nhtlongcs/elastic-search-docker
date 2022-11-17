## Elastic search docker compose

This is a docker compose file for running elastic search in a docker container. It is based on the official elastic search docker image. It is configured to run elastic on port 9200 and kibana on port 5601. 


### Usage
#### Start elastic search
Create `.env` file with the following content:
```text
ELASTIC_VERSION=8.5.0
ELASTIC_SECURITY=true
ELASTIC_PASSWORD=123456
```
Where `ELASTIC_VERSION` is the version of elastic search you want to run(checkout [this link](https://hub.docker.com/_/elasticsearch) for available versions). `ELASTIC_SECURITY` is a boolean value that determines if you want to enable security on elastic search. `ELASTIC_PASSWORD` is the password for the elastic user.

Then run the following command:
```bash
docker-compose up -d
```

For logs:
```bash
docker-compose logs -f
```
Stop elastic search:
```bash
docker-compose down
```

#### Indexing and searching

We also provide a example usecase for indexing and searching. The scripts are located in `example` directory. To run the example, first create a virtual conda environment and install the dependencies by running:
```bash
conda env create -f environment.yml
conda activate elastic
```

To index data, you can use the [elastic search bulk api](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html). For example, checkout the example [here](example/index.ipynb). To query data, you can use the [elastic search search api](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html). In the example, we use the [elasticsearch-dsl](https://elasticsearch-dsl.readthedocs.io/en/latest/) library to query data. Checkout the example [here](example/search.ipynb).

### Monitoring

You can monitor the elastic search cluster using the kibana dashboard. To access the kibana dashboard, go to `http://localhost:5601` in your browser. You will be prompted to enter the elastic user password. The default password is `changeme`. You can change the password by setting the `ELASTIC_PASSWORD` environment variable in the `.env` file.