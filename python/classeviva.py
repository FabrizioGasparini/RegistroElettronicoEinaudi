import requests
import json
import re
import datetime


# ==== Classe Principale (Utente) ===== #
class Utente:
    # === Inizializza Utente === #
    # -> ()        -> se il token NON è necessario (ex. login)
    # -> ({token}) -> se il token è necessario (ex. status)
    def __init__(self, token: str = ''):
        self.token = token

        self.connesso = False

    # === Effettua il Login === #
    #  -> ''        -> se il login NON viene effettuato
    #  -> '{token}' -> se il login viene effettuato correttamente
    def login(self, uid: str, pwd: str):
        response = requests.post(RequestURLs.login, headers=headers(), data=f'{{"ident":null,"pass":"{pwd}","uid":"{uid}"}}')

        if response.status_code == 200:
            data = json.loads(response.text)

            print('Login effettuato con successo.')
            self.token = data['token']
            return self.token
        else:
            print('Errore durante il Login.')

        return ''

    # === Controlla lo stato dell'utente === #
    #  -> return ''        -> l'utente NON è connesso/è insistente
    #  -> return '{ident}' -> l'utente è connesso
    def status(self):
        if self.token == '':
            return ''

        response = requests.get(RequestURLs.status, headers=headers(self.token))

        if response.status_code == 200:
            data = json.loads(response.text)['status']

            return re.search(r'\d+', data['ident']).group()
        else:
            return ''


    # === Effettua una Richiesta 'GET' === #
    def request(self, reqeust_url: tuple, params=()):
        ident = self.status()

        if ident == '':
            return ''

        args = (ident,)
        if params is not None:
            args += params

        if reqeust_url[1] == 'get':
            response = requests.get(reqeust_url[0].format(*args), headers=headers(self.token))
        else:
            response = requests.post(reqeust_url[0].format(*args), headers=headers(self.token))

        if response.status_code == 200:
            return response
        else:
            return ''


    def get_name(self):
        if self.token == '':
            return ''

        response = self.request(RequestURLs.card)

        if response != '' and response.status_code == 200:
            data = json.loads(response.text)['card']
            name = f"{data['firstName'].capitalize()} {data['lastName'].capitalize()}"

            return name
        else:
            return ''


    def get_total_absences(self):
        if self.token == '':
            return ''

        response = self.request(RequestURLs.assenze)

        output = {"total": '0', "to_justify": '0'}
        if response != '' and response.status_code == 200:
            data = json.loads(response.text)['events']

            tot = 0
            to_justify = 0
            for absence in data:
                if absence['evtCode'] == 'ABA0':
                    tot += 1

                if not absence['isJustified']:
                    to_justify += 1

            output['total'] = str(tot)
            output['to_justify'] = str(to_justify)

        return output

    def get_today_events(self):
        if self.token == '':
            return ''

        date = get_cvv_date(datetime.date(2023, 10, 8))

        response = self.request(RequestURLs.agenda, (date, date))

        output = {'total': '0', 'list': 'Nessun evento in programma per oggi!'}
        if response != '' and response.status_code == 200:
            data = json.loads(response.text)['agenda']

            if len(data) > 0:
                output['total'] = len(data)
                hw_cnt = 0
                nt_cnt = 0
                print(data)

                for event in data:
                    eventCode = event['evtCode']

                    if eventCode == "AGHW":
                        hw_cnt += 1
                    else:
                        nt_cnt += 1

                hw = ''
                if hw_cnt > 1:
                    hw = f'{hw_cnt} Compiti'
                else:
                    hw = f'{hw_cnt} Compito'

                nt = ''
                if nt_cnt > 1:
                    nt = f'{nt_cnt} Annotazioni'
                else:
                    nt = f'{nt_cnt} Annotazione'

                if hw_cnt > 0 and nt_cnt > 0:
                    output['list'] = f"{hw} | {nt}"
                elif hw_cnt > 0:
                    output['list'] = hw
                elif nt_cnt > 0:
                    output['list'] = nt


        return output



    def get_last_grade(self):
        if self.token == '':
            return ''

        response = self.request(RequestURLs.voti)

        output = {'grade': 'Nessuno', 'subject': 'Non hai ancora preso alcun voto'}
        if response != '' and response.status_code == 200:
            data = json.loads(response.text)['grades']

            last_date = datetime.date(2000, 1, 1)
            for grade in data:
                date = datetime.datetime.strptime(grade['evtDate'], "%Y-%m-%d").date()
                if date > last_date:
                    last_date = date
                    output['grade'] = grade['displayValue']
                    output['subject'] = grade['subjectDesc']

        return output

    def get_last_comm(self):
        if self.token == '':
            return ''

        response = self.request(RequestURLs.bacheca)

        output = {'title': 'Nessuno', 'message': 'Non hai ancora comunicazioni in bacheca', 'link': '#'}
        print(response.text)
        if response != '' and response.status_code == 200:
            data = json.loads(response.text)['items']

            last_date = datetime.date(2000, 1, 1)
            for comm in data:
                date = datetime.datetime.fromisoformat(comm['pubDT']).date()
                if date > last_date:
                    last_date = date
                    output['title'] = comm['cntTitle']


                attachment = self.request(RequestURLs.bacheca_leggi, (comm['evtCode'], comm['pubId']))

                if attachment != '' and attachment.status_code == 200:
                    output['message'] = json.loads(attachment.text)['item']['text']
                    return output

                output['message'] = 'La comunicazione non ha un testo'

        return output


def get_cvv_date(normal_date: datetime.date):
    return normal_date.strftime("%Y%m%d")

# ===== Headers ===== #
def headers(token: str = '') -> dict[str, str]:
    if token == None:
        return {
            "User-Agent": "CVVS/std/4.1.7 Android/12",
            "Content-Type": "application/json",
            "Z-Dev-ApiKey": "Tg1NWEwNGIgIC0K"
        }
    else:
        return {
            "User-Agent": "CVVS/std/4.1.7 Android/12",
            "Content-Type": "application/json",
            "Z-Dev-ApiKey": "Tg1NWEwNGIgIC0K",
            "Z-Auth-Token": str(token)
        }

# ===== Reqeust URLs ===== #
class RequestURLs:
    base_url: str = 'https://web.spaggiari.eu/rest/v1'
    students_url: str = f'{base_url}/students/{{}}'  # Student Ident

    assenze: tuple = (f'{students_url}/absences/details', 'get')
    agenda: tuple = (f'{students_url}/agenda/all/{{}}/{{}}', 'get')  # Data Inizio (YYYYMMDD) / Data Fine (YYYYMMDD)
    didattica: tuple = (f'{students_url}/didactics', 'get')
    libri: tuple = (f'{students_url}/schoolbooks', 'get')
    calendario: tuple = (f'{students_url}/calendar/all', 'get')
    card: tuple = (f'{students_url}/card', 'get')
    voti: tuple = (f'{students_url}/grades', 'get')
    lezioni_oggi: tuple = (f'{students_url}/lessons/today', 'get')
    lezioni_giorno: tuple = (f'{students_url}/lessons/{{}}', 'get')  # Lezioni Giorno (YYYYMMDD)
    note: tuple = (f'{students_url}/notes/all', 'get')
    periods: tuple = (f'{students_url}/perioids', 'get')
    materie: tuple = (f'{students_url}/subjects', 'get')
    bacheca: tuple = (f'{students_url}/noticeboard', 'get')
    bacheca_leggi: tuple = (f'{students_url}/noticeboard/read/{{}}/{{}}/101', 'post')  # eventCode | pubId

    login: str = f'{base_url}/auth/login'
    status: str = f'{base_url}/auth/status'
    noticeboard: tuple = (f'{students_url}/noticeboard', 'post')
    documenti: tuple = (f'{students_url}/documents', 'post')


class MaterieID:
    italiano = 212238
    storia = 212239
    matematica = 212249
    inglese = 212242
    diritto = 212243
    educazione_civica = 408053
    geografica = 427832
    fisica = 212234
    biologia = 212237
    chimica = 212233
    ttrg = 212228
    informatica = 212220
    educazione_fisica = 212236
    alternativa = 427831

    materie = [
        italiano,
        storia,
        matematica,
        inglese,
        diritto,
        educazione_civica,
        geografica,
        fisica,
        biologia,
        chimica,
        ttrg,
        informatica,
        educazione_fisica,
        alternativa
    ]


class Compito:
    def __init__(self, id_compito, giorno, descrizione, tipo, materia, insegnante):
        self.id = id_compito
        self.giorno = giorno
        self.descrizione = descrizione
        self.tipo = tipo
        self.materia = materia
        self.insegnante = insegnante
