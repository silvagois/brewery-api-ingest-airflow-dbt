FROM apache/airflow:3.1.6

USER root

# System deps (DuckDB sometimes needs these)
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    apt-get clean

USER airflow

# Copy requirements
COPY requirements.txt /requirements.txt

# Install python deps
RUN pip install --no-cache-dir -r /requirements.txt
