# Invoice QA - Invoice Database Interaction

This project simplifies interaction with an Invoice Database stored in Google BigQuery by answering your questions in natural language. It comprises Python scripts powered by Streamlit for a user-friendly interface, Google Cloud services for data storage and retrieval, and SQLite for local data caching.

## Requirements
- **Streamlit**: Python library for building interactive web applications.
- **langchain**: Library for natural language processing tasks.
- **Google Cloud BigQuery**: Service for managing big data analytics.
- **SQLite**: Local database for data caching and retrieval.

## Usage
1. Clone the repository to your local machine.
2. Install the required dependencies listed in `requirements.txt`.
3. Ensure proper configuration of Google Cloud credentials.
4. Run the `main2.py` script using Streamlit.
5. Input queries in the provided text box to interact with the Invoice Database.

## Features
- Import data from Google BigQuery to a local SQLite database.
- Query the Invoice Database using Streamlit UI. Asks users to enter their questions about the invoice data.
- Efficient data retrieval and caching for improved performance.

## API Keys
Ensure to set up the OpenAI API Key: Obtained from OpenAI for natural language processing tasks.
Set these API keys as environment variables or directly in the code.
