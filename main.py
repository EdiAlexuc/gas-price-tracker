import time
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import Error
import re

# Function to extract and store gas price data 
def extract_and_store_gas_prices():
    # Make a GET request to the website
    response = requests.get("https://www.plinul.ro/pret/benzina-standard/botosani-botosani/omv")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table with the class "tabel table-striped"
    price_text = soup.find("table", class_="table table-striped").find("tr", class_="cursor-pointer").find_all("td")[3].text.strip()
    price = re.findall(r'\d+\.\d+', price_text)[0]

    # Establish database connection 
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="1234",
            host="localhost",
            port="5432",
            database="gas_prices"
        )
        cursor = connection.cursor()
    except(Exception, Error) as error:
        print("Error while trying to connect to db: ", error)
        return
    
    # Create table in db
    create_table_query = ''' CREATE TABLE IF NOT EXISTS gas_prices (
                                id SERIAL PRIMARY KEY,
                                price FLOAT,
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )'''
    cursor.execute(create_table_query)

    # Insert the extracted data into db
    try:
        insert_query = "INSERT INTO gas_prices (price) VALUES (%s)"
        data = (price,)
        cursor.execute(insert_query, data)
        connection.commit()
        print("Gas price data successfully inserted into db.")
    except(Exception, Error) as error:
        print("Error while inserting data into db: ", error)
    
    # Close db connection
    if connection:
        cursor.close()
        connection.close()
        print("Db connection is closed")


# Continuously monitor the website for updates:
while True:
    extract_and_store_gas_prices()
    time.sleep(86400) # Wait 24 hours before checking again





# Print the data
#print(price)

