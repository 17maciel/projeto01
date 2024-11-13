import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import sqlite3

def fetch_page():
    url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-256-gb-titnio-deserto-distribuidor-autorizado/p/MLB1040287840#polycard_client=search-nordic&wid=MLB3846027829&sid=search&searchVariation=MLB1040287840&position=3&search_layout=stack&type=product&tracking_id=c53122b0-4d92-48b3-93de-e1afccc1f2e4"
    response = requests.get(url)
    return response.text

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    product_name = soup.find("h1", {"class": "ui-pdp-title"}).get_text()
    product_price = soup.find_all("span", {"class": "andes-money-amount__fraction"})
    old_price: int = int(product_price[0].get_text().replace('.', ''))
    new_price: int = int(product_price[1].get_text().replace('.', ''))
    installment_price : int = int(product_price[2].get_text().replace('.', ''))

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "product_name": product_name,
        "old_price": old_price,
        "new_price": new_price,
        "installment_price": installment_price,
        "timestamp": timestamp
    }

def create_connection(db_name='Iphone_prices.db'):
    """Cria um conexão com o banco de dados SQLite"""
    conn = sqlite3.connect(db_name)
    return conn

def setup_database(conn):
    """Cria a tabela de preços se ela não existir"""
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prices(
        id  INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        old_price INTEGER,
        new_price INTEGER,
        installment_price INTEGER,
        timestamp TEXT NOT NULL
    )
''')
    conn.commit()

def save_to_database(conn, product_info):
    new_row = pd.DataFrame([product_info])
    new_row.to_sql('prices', conn, if_exists='append', index=False)

def get_max_price(conn): 
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(new_price), timestamp from prices")  # Changed 'price' to 'prices'
    result = cursor.fetchone()
    return result[0], result[1]

if __name__ == "__main__":

    conn = create_connection()
    setup_database(conn)

    while True:
        page_content = fetch_page()
        product_info = parse_page(page_content)

        max_price, max_timestamp = get_max_price(conn)

        current_price = product_info["new_price"]
                                     
        if current_price > max_price:
            print("Preço maior detectado")
            max_price = current_price
            max_price_timestamp = product_info['timestamp']
        else:
            print("O preço máximo registrado é o antigo")
                                    
        save_to_database(conn, product_info)
        print("Dados salvos no banco de dados:  ", product_info)

        time.sleep(10)

