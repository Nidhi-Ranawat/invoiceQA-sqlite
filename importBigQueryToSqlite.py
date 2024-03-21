from utils import *
import streamlit as st
import os

@st.cache_data
def fetching_data_bq(_client, query):
    df = _client.query(query).to_dataframe()
    df_cleaned = clean_data(df)
    db_file = 'invoicedb.sqlite'
    save_to_sqlite(df_cleaned, db_file)

def load_data():
    root = os.getcwd()
    # Defining service account file path
    service_account_file = os.path.join(root, "credential.json")

    # Connect to BigQuery
    bq_client = connect_to_bigquery(service_account_file)

    # Define BigQuery dataset details - project, dataset, and table
    project = "data-23-24"
    dataset = "invoice_dataset"
    table = "bu18dec"
    sqlite_row_count = get_row_count()
    # print(sqlite_row_count, type(row_count))

    # Define BigQuery query
    query = f"SELECT * FROM `{project}.{dataset}.{table}` ORDER BY PNR DESC LIMIT 50000 OFFSET {sqlite_row_count+1};"

    fetching_data_bq(bq_client, query)


# from apscheduler.schedulers.blocking import BlockingScheduler

# scheduler = BlockingScheduler()
# scheduler.add_job(load_data, 'interval', minutes=1)
# scheduler.start()
# scheduler.end()





