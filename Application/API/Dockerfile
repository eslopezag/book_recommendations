FROM continuumio/miniconda3:4.9.2
WORKDIR /api
EXPOSE 3000
COPY . .

# Make `bash` the detault shell:
SHELL ["/bin/bash", "-c"]

RUN conda env create -f ./conda-env.yml

# Make `books_mongo the default environment:`
ENV PATH /opt/conda/envs/books_mongo/bin:$PATH
ENV CONDA_DEFAULT_ENV books_mongo

CMD . ./run.sh
