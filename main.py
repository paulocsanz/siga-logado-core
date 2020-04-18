from sys import argv
from bs4 import BeautifulSoup
import requests

def login_to_siga(user, password):
    cas_url = "https://cas.ufrj.br/login"
    cas_get_resp = requests.get(cas_url)

    soup = BeautifulSoup(cas_get_resp.content.decode('utf-8'), "html.parser")
    csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]
    lt = soup.find("input", {"id": "lt"})["value"]

    cas_post_resp = requests.post(cas_url, data = {
        "authenticity_token": csrf_token,
        "lt": lt,
        "service": "https://intranet.ufrj.br/cas?destination=node/4",
        "username": user,
        "password": password
    })

    print(cas_post_resp.content.decode("utf-8"))
    print("\n\n\n\n\n")
    print("You are logged in")
    #soup = BeautifulSoup(cas_post_resp.content.decode('utf-8'), "html.parser")
    #next_url = soup.find("div", {"id": "block-block-3"}).find("div", {"class": "content"}).find_all("p")[3].find("a")["href"]

    #auxiliar = requests.get(next_url)
    #print(auxiliar.content.decode("utf-8"))

if __name__ == "__main__":
    if len(argv) != 3:
        print("Must call script with username and password\n  python3 main.py <username> <password>")
    else:
        login_to_siga(argv[1], argv[2])
