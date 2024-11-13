import requests
from bs4 import BeautifulSoup
import time

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

    return {
        "product_name": product_name,
        "old_price": old_price,
        "new_price": new_price,
        "installment_price": installment_price
    }

if __name__ == "__main__":
    while True:
        page_content = fetch_page()
        product_info = parse_page(page_content)
        print(product_info)
        time.sleep(10)

