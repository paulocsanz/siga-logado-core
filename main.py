from sys import argv
from bs4 import BeautifulSoup
import requests

def login_to_siga(user, password):
    with requests.Session() as session:
        auxiliar_url = "https://intranetauxiliar.ufrj.br/LoginUfrj/redireciona/?url_redir=https%3A%2F%2Fsiga.ufrj.br%2Fsira%2Fintranet%2FLoginIntranet.jsp%3FidentificacaoUFRJ%3D%3Aidentificacao_ufrj%3A%26idSessao%3D%3Aid_sessao%3A"
        auxiliar_resp = session.get(auxiliar_url)

        soup = BeautifulSoup(auxiliar_resp.content.decode('utf-8'), "html.parser")
        authenticity_token = soup.find("input", {"name": "authenticity_token"})["value"]
        lt = soup.find("input", {"id": "lt"})["value"]

        cas_resp = session.post(auxiliar_resp.url, data = {
            "authenticity_token": authenticity_token,
            "lt": lt,
            "username": user,
            "password": password
        })

        gnosys_url = "https://gnosys.ufrj.br/Portal/auth.seam"
        gnosys_resp = session.get(gnosys_url)
        soup = BeautifulSoup(gnosys_resp.content.decode("utf-8"), "html.parser")
        name = soup.find("div", {"class":"gnosys-login-nome"}).text
        print(title_case(name))
        return (gnosys_url, gnosys_resp.cookies)

def title_case(txt):
    return " ".join([t[0].upper() + t[1:].lower() for t in txt.split(" ")])

if __name__ == "__main__":
    if len(argv) != 3:
        print("Must call script with username and password\n  python3 main.py <username> <password>")
    else:
        print(login_to_siga(argv[1], argv[2]))
