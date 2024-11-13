import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import sqlite3

def fetch_page():
    url = "https://www.mercadolivre.com.br/fritadeira-sem-oleo-air-fryer-6l-mondial-afn-60-bi-1900w-pretoinox/p/MLB25401959?pdp_filters=item_id:MLB3411318187#wid=MLB3411318187&sid=search&is_advertising=true&searchVariation=MLB25401959&position=1&search_layout=stack&type=pad&tracking_id=5ea6e707-d1ab-4484-8f73-814f8184abe5&is_advertising=true&ad_domain=VQCATCORE_LST&ad_position=1&ad_click_id=MDgyN2Y5OWEtZDYzNS00YzU3LTk0NzEtYzM0NTY4MDQ0ZmI1"
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
        current_price = product_info["new_price"]

        max_price, max_timestamp = get_max_price(conn)

        max_price_timestamp = None
                                     
        if current_price > max_price:
            print("Preço maior detectado")
            max_price = current_price
            max_price_timestamp = product_info['timestamp']
        else:
            print("O preço máximo registrado é {max_price}")
                                    
        save_to_database(conn, product_info)
        print("Dados salvos no banco de dados:  ", product_info)

        time.sleep(10)

