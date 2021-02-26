FROM continuumio/miniconda3:4.9.2
WORKDIR /recom
EXPOSE 3000
COPY . .

# Make `bash` the detault shell:
SHELL ["/bin/bash", "-c"]

RUN conda install -c conda-forge --file requirements.txt

CMD . ./run.sh
