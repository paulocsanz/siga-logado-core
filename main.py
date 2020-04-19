from sys import argv
from bs4 import BeautifulSoup
import requests

portal_uri = "https://gnosys.ufrj.br"

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

        gnosys_resp = session.get(portal_uri + "/Portal/auth.seam")
        return gnosys_resp.cookies

def personal(cookies):
    with requests.Session() as session:
        session.cookies = cookies
        session.get(portal_uri + "/Registro")
        resp = session.get(portal_uri + "/Registro/auth.seam")
        soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")
        return str(soup.find("div", {"id": "blocoDadosPessoais"}))

def enrolled(cookies):
    with requests.Session() as session:
        session.cookies = cookies
        session.get(portal_uri + "/Inscricao")
        resp = session.get(portal_uri + "/Inscricao/auth.seam")
        soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")
        token = soup.find("span", {"id": "token"}).text

        resp = session.get(portal_uri + "/Inscricao/seam/resource/rest/inscricao/pedidos?token=" + token)
        return resp.content.decode("utf-8")

def documents(cookies):
    with requests.Session() as session:
        session.cookies = cookies
        session.get(portal_uri + "/Documentos")
        resp = session.get(portal_uri + "/Documentos/auth.seam")
        return resp.content.decode("utf-8")

def title_case(txt):
    return " ".join([t[0].upper() + t[1:].lower() for t in txt.split(" ")])

if __name__ == "__main__":
    if len(argv) != 3:
        print("Must call script with username and password\n  python3 main.py <username> <password>")
    else:
        cookie = login_to_siga(argv[1], argv[2])
        print(personal(cookie))
        print(enrolled(cookie))
        print(documents(cookie))
