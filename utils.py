from typing import Dict, List
from langchain import PromptTemplate, OpenAI, LLMChain
from google.cloud import bigquery
import json
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import numpy as np
import os
import sqlite3

from langchain import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
root = os.getcwd()
file_path = os.path.join(root, "credential.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = file_path

@st.cache_resource(ttl=24*60*60)
def connect_to_bigquery(credentials_file):
    # Getting credentials from service account file
    credentials = service_account.Credentials.from_service_account_file(credentials_file)
    # Creating BigQuery client with credentials (connection)
    return bigquery.Client(credentials=credentials, project=credentials.project_id)

# @st.cache(ttl=24*60*60)
def execute_sqlite_query(_client, query):
    df = _client.query(query).to_dataframe()
    return df

# @st.cache_data(ttl=24*60*60)
def clean_data(df):
    # Cleaning PNR numbers for unexpected values
    # df['PNR'] = df['PNR'].apply(clean_invalid_chars)

    # DATE FORMATTING
    date_columns = ['Date', 'Start Date', 'End Date', 'Paid Date', 'Received Date']
    df[date_columns] = df[date_columns].apply(pd.to_datetime, errors='coerce', format="%Y-%m-%d")

    # FLOAT VALUES
    float_columns = ['Base Fare', 'Airport and Other Taxes', 'Service Fee', 'Cancellation Charge', 
                    'GST Out', 'Total Inv', 'Rate Per Adlt', 'Rate Per Child', 'Rate Per Infant', 
                    'Tax Per Adult', 'Tax Per Child', 'Tax Per Infant', 'Cost in FC', 'Exchange Rate', 
                    'Amt In INR', 'Amt Received']
    df[float_columns] = df[float_columns].apply(pd.to_numeric, errors='coerce')

    # Converting Int64 columns to integers
    int_columns = ['Credit Days', 'Real Credit', 'Segments', 'Service Fee Rev']
    df[int_columns] = df[int_columns].fillna(0).astype(int)

    # Converting object columns to string
    object_columns = df.select_dtypes(include=['object']).columns
    df[object_columns] = df[object_columns].fillna('').astype(str)
    
    return df

# @st.cache_data
def save_to_sqlite(df, db_file):
    # Creating a SQLite database connection
    conn = sqlite3.connect(db_file)
    # Save DataFrame to SQLite database
    # df.to_sql('invoices', conn, if_exists='append', index=False)
    df.to_sql('invoices', conn, if_exists='append', index=False)
    conn.close()

def get_row_count():
    conn = sqlite3.connect('invoicedb.sqlite')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM invoices')
    except:
        return 0
    count = cursor.fetchone()[0]
    conn.close()
    return count


TEMPLATE = '''
Write a SQLite query that achieves the following.
```
{{ content }}
```

The format of the target tables is as follows.
```json
{{ schema }}
```

Output the SQLite query in raw text.
    '''

TEMPLATE2 = '''
Write a case insensitive SQLite query that achieves the following.
```
{{ content }} for 25 records max include following columns only Customer, `Passenger Name`, PNR, `Ticket No`, `Base Fare`, `Total Inv`, Agent, `Amt In INR` aways use wildcards for names in WHERE conditions.
```

The format of the target tables is as follows.
```json
{{ schema }}
```

Output the SQLite query in raw text.
    '''

def get_schema(table_name: str) -> Dict[str, any]:
    conn = sqlite3.connect('invoicedb.sqlite')
    cursor = conn.cursor()

    # Fetching table schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema_info = cursor.fetchall()
    schema = [{'name': column[1], 'type': column[2]} for column in schema_info]

    # Closing cursor and connection
    cursor.close()
    conn.close()

    return {'table': table_name, 'schema': schema}

def get_schemas(table_name):
    print(get_schema(table_name))
    return json.dumps(get_schema(table_name))

def predict(content: str, verbose: bool = False):
    prompt = PromptTemplate(
        input_variables=["content","schema"],
        template=TEMPLATE,
        template_format='jinja2',
    )
    llm_chain = LLMChain(
        llm=OpenAI(model="gpt-3.5-turbo-instruct",temperature=0), 
        prompt=prompt, 
        verbose=verbose,
    )
    return llm_chain.predict(content=content, schema=get_schemas('invoices'))

def predict_df(content: str, verbose: bool = False):
    prompt = PromptTemplate(
        input_variables=["content","schema"],
        template=TEMPLATE2,
        template_format='jinja2',
    )
    llm_chain = LLMChain(
        llm=OpenAI(model="gpt-3.5-turbo-instruct",temperature=0), 
        prompt=prompt, 
        verbose=verbose,
    )
    return llm_chain.predict(content=content, schema=get_schemas('invoices'))

def execute_sqlite_query(query):
    conn = sqlite3.connect('invoicedb.sqlite')
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(df)
    return df

def get_response(input):
    query = predict(input,True)
    print(query)
    df = execute_sqlite_query(query)
    return df

def get_response_df(input):
    query = predict_df(input, True)
    print(query)
    df = execute_sqlite_query(query)
    return df