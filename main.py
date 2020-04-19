from sys import argv
from bs4 import BeautifulSoup
import requests

portal_uri = "https://gnosys.ufrj.br"

def login_to_siga(user, password):
    with requests.Session() as session:
        # Uses SIGA's internal redirect to bypass captcha
        auxiliar_url = "https://intranetauxiliar.ufrj.br/LoginUfrj/redireciona/?url_redir=https%3A%2F%2Fsiga.ufrj.br%2Fsira%2Fintranet%2FLoginIntranet.jsp%3FidentificacaoUFRJ%3D%3Aidentificacao_ufrj%3A%26idSessao%3D%3Aid_sessao%3A"
        auxiliar_resp = session.get(auxiliar_url)

        # We were redirected to SIGA's CAS (Central Authority Server)
        # So let's get the csrf token and the login token
        soup = BeautifulSoup(auxiliar_resp.content.decode('utf-8'), "html.parser")
        authenticity_token = soup.find("input", {"name": "authenticity_token"})["value"]
        lt = soup.find("input", {"id": "lt"})["value"]

        # Make the request to CAS, credentials and form protections
        cas_resp = session.post(auxiliar_resp.url, data = {
            "authenticity_token": authenticity_token,
            "lt": lt,
            "username": user,
            "password": password
        })

        # We were redirected to gnosys.ufrj.br using the redirect server
        # Going to $uri/auth.seam with the appropriate cookies return
        # the desired page
        gnosys_resp = session.get(portal_uri + "/Portal/auth.seam")
        return gnosys_resp.cookies

def personal(cookies):
    with requests.Session() as session:
        # Set session cookies with the ones obtained in `login_to_siga`
        session.cookies = cookies

        # Go to the page just to wait for the redirect request
        session.get(portal_uri + "/Registro")
        # Going here with the appropriate cookies return the desired page
        resp = session.get(portal_uri + "/Registro/auth.seam")
        soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")

        # Return raw HTML of personal infos' div
        return str(soup.find("div", {"id": "blocoDadosPessoais"}))

def enrolled(cookies):
    with requests.Session() as session:
        # Set session cookies with the ones obtained in `login_to_siga`
        session.cookies = cookies

        # Go to the page just to wait for the redirect request
        session.get(portal_uri + "/Inscricao")
        # Going here with the appropriate cookies return the desired page
        resp = session.get(portal_uri + "/Inscricao/auth.seam")


        soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")
        # We need a token to get the raw json enrollment data
        token = soup.find("span", {"id": "token"}).text

        # Make request to JSON API with appropriate token and return it raw
        resp = session.get(portal_uri + "/Inscricao/seam/resource/rest/inscricao/pedidos?token=" + token)
        return resp.content.decode("utf-8")

def documents(cookies):
    with requests.Session() as session:
        # Set session cookies with the ones obtained in `login_to_siga`
        session.cookies = cookies
        # Go to the page just to wait for the redirect request
        session.get(portal_uri + "/Documentos")
        # Going here with the appropriate cookies return the desired page
        resp = session.get(portal_uri + "/Documentos/auth.seam")

        # We return the raw HTML of the page containing all the pdfs
        # Reverse engineering is needed to select specific pdfs (it uses js to lazy load)
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
