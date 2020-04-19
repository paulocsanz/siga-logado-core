from sys import argv
from bs4 import BeautifulSoup
import requests

def login_to_siga(user, password):

    with requests.Session() as session:       

        #Login into intranet login page
        intranet_login_url      = "https://intranetauxiliar.ufrj.br/LoginUfrj/redireciona/?url_redir=https%3A%2F%2Fsiga.ufrj.br%2Fsira%2Fintranet%2FLoginIntranet.jsp%3FidentificacaoUFRJ%3D%3Aidentificacao_ufrj%3A%26idSessao%3D%3Aid_sessao%3A"
        intranet_login_response = session.get(intranet_login_url)

        #Find the tokens necessary to the post Data
        intranet_login_page_html = BeautifulSoup(intranet_login_response.content.decode('utf-8'), "html.parser")
        authenticity_token       = intranet_login_page_html.find("input", {"name": "authenticity_token"})["value"]
        lt_token                 = intranet_login_page_html.find("input", {"id": "lt"})["value"]

        #Creates the post to Login on intranet
        cas_response = session.post(intranet_login_response.url, data = {
            "authenticity_token": authenticity_token,
            "lt":                 lt_token,
            "username":           user,
            "password":           password
        })
        
        #Login into Siga page (303 Treatment)
        gnosys_portal_url      = "https://gnosys.ufrj.br/Portal/auth.seam"
        gnosys_portal_response = session.get(gnosys_portal_url)
        siga_main_page_html    = BeautifulSoup(gnosys_portal_response.content.decode("utf-8"), "html.parser")
        name                   = siga_main_page_html.find("div", {"class":"gnosys-login-nome"}).text

        print(title_case(name))

        #Treat the cookies to join the Registration Page (Get the user information)
        session.cookies.set_cookie(requests.cookies.create_cookie(list(gnosys_portal_response.cookies.get_dict().keys())[0], gnosys_portal_response.cookies.get_dict()[list(gnosys_portal_response.cookies.get_dict().keys())[0]]))

        #Access the User Personal Information URL
        personal_info_url            = "https://portalaluno.ufrj.br/Registro"
        personal_info_response       = session.get(personal_info_url)
        gnosys_registration_url      = "https://gnosys.ufrj.br/Registro/auth.seam"
        gnosys_registration_response = session.get(gnosys_registration_url)

        #Here We can take all user personal information. (We need to parse some of those information)
        personal_data_html = BeautifulSoup(gnosys_registration_response.content.decode("utf-8"), "html.parser")

        #Access the Enrolled Disciplines URL
        enrolled_disciplines_url     = "https://portalaluno.ufrj.br/Inscricao"
        enrolled_discipline_response = session.get(enrolled_disciplines_url)
        gnosys_enrollment_url        = "https://gnosys.ufrj.br/Inscricao/auth.seam"
        gnosys_enrollment_response   = session.get(gnosys_enrollment_url)

        #Here We can take all user enrolled disciplines. We need to parse some of those information
        enrolled_disciplines_html = BeautifulSoup(gnosys_enrollment_response.content.decode("utf-8"), "html.parser")

        #Gets the token value to get all the user Enrolled Disciplines
        json_token = enrolled_disciplines_html.find("span", {"id": "token"}).contents[0]

        #Gets the json with all the user disciplines (We need to parse some of those information)
        json_enrolled_disciplines_url     = "https://portalaluno.ufrj.br/Inscricao/seam/resource/rest/inscricao/pedidos?token=" + json_token
        json_enrolled_disciplines_content = session.get(json_enrolled_disciplines_url).text

        return (json_enrolled_disciplines_content)

def title_case(txt):
    return " ".join([t[0].upper() + t[1:].lower() for t in txt.split(" ")])

if __name__ == "__main__":

    argv = ["", ""]

    if len(argv) != 2:
        print("Must call script with username and password\n  python3 main.py <username> <password>")

    else:
        print(login_to_siga(argv[0], argv[1]))
