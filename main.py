from sys import argv
from bs4 import BeautifulSoup
import requests

def LoginToSiga(user, password):

    with requests.Session() as session:       

        #Login into intranet login page
        intranetLoginUrl      = "https://intranetauxiliar.ufrj.br/LoginUfrj/redireciona/?url_redir=https%3A%2F%2Fsiga.ufrj.br%2Fsira%2Fintranet%2FLoginIntranet.jsp%3FidentificacaoUFRJ%3D%3Aidentificacao_ufrj%3A%26idSessao%3D%3Aid_sessao%3A"
        intranetLoginResponse = session.get(intranetLoginUrl)

        #Find the tokens necessary to the post Data
        intranetLoginPageHTML = BeautifulSoup(intranetLoginResponse.content.decode('utf-8'), "html.parser")
        authenticityToken     = intranetLoginPageHTML.find("input", {"name": "authenticity_token"})["value"]
        ltToken               = intranetLoginPageHTML.find("input", {"id": "lt"})["value"]

        #Creates the post to Login on intranet
        casResponse = session.post(intranetLoginResponse.url, data = {
            "authenticity_token": authenticityToken,
            "lt":                 ltToken,
            "username":           user,
            "password":           password
        })
        
        #Login into Siga page (303 Treatment)
        gnosysPortalUrl      = "https://gnosys.ufrj.br/Portal/auth.seam"
        gnosysPortalResponse = session.get(gnosysPortalUrl)
        sigaMainPageHTML     = BeautifulSoup(gnosysPortalResponse.content.decode("utf-8"), "html.parser")
        name                 = sigaMainPageHTML.find("div", {"class":"gnosys-login-nome"}).text

        print(TitleCase(name))

        #Treat the cookies to join the Registration Page (Get the user information)
        session.cookies.set_cookie(requests.cookies.create_cookie(list(gnosysPortalResponse.cookies.get_dict().keys())[0], gnosysPortalResponse.cookies.get_dict()[list(gnosysPortalResponse.cookies.get_dict().keys())[0]]))

        #Access the User Personal Information URL
        personalInfoUrl            = "https://portalaluno.ufrj.br/Registro"
        personalInfoResponse       = session.get(personalInfoUrl)
        gnosysRegistrationUrl      = "https://gnosys.ufrj.br/Registro/auth.seam"
        gnosysRegistrationResponse = session.get(gnosysRegistrationUrl)

        #Here We can take all user personal information. (We need to parse some of those information)
        PersonalDataHTML = BeautifulSoup(gnosysRegistrationResponse.content.decode("utf-8"), "html.parser")

        #Access the Enrolled Disciplines URL
        enrolledDisciplinesUrl     = "https://portalaluno.ufrj.br/Inscricao"
        enrolledDisciplineResponse = session.get(enrolledDisciplinesUrl)
        gnosysEnrollmentUrl        = "https://gnosys.ufrj.br/Inscricao/auth.seam"
        gnosysEnrollmentResponse   = session.get(gnosysEnrollmentUrl)

        #Here We can take all user enrolled disciplines. We need to parse some of those information
        enrolledDisciplinesHTML = BeautifulSoup(gnosysEnrollmentResponse.content.decode("utf-8"), "html.parser")

        #Gets the token value to get all the user Enrolled Disciplines
        jsonToken = enrolledDisciplinesHTML.find("span", {"id": "token"}).contents[0]

        #Gets the json with all the user disciplines (We need to parse some of those information)
        jsonEnrolledDisciplinesUrl     = "https://portalaluno.ufrj.br/Inscricao/seam/resource/rest/inscricao/pedidos?token=" + jsonToken
        jsonEnrolledDisciplinesContent = session.get(jsonEnrolledDisciplinesUrl).text

        return (jsonEnrolledDisciplinesContent)

def TitleCase(txt):
    return " ".join([t[0].upper() + t[1:].lower() for t in txt.split(" ")])

if __name__ == "__main__":

    argv = ["13429384702", "8778Bruno"]

    if len(argv) != 2:
        print("Must call script with username and password\n  python3 main.py <username> <password>")

    else:
        print(LoginToSiga(argv[0], argv[1]))
