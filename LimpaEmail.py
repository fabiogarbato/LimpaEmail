import configparser
import imaplib
import email
from email.header import decode_header

def apagar_emails():
    try:
        config = configparser.ConfigParser()
        config.read("config.ini")

        IMAP_SERVER = config["Email"]["IMAP_SERVER"]
        EMAIL_USER = config["Email"]["EMAIL_USER"]
        EMAIL_PASS = config["Email"]["EMAIL_PASS"]
        REMETENTES = config["Email"]["REMETENTES"].split(",")

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX")

        for remetente in REMETENTES:
            status, message_numbers = mail.search(None, f'(FROM "{remetente}")')
            if status == "OK":
                ids = message_numbers[0].split()
                total = len(ids)
                print(f"Encontrados {total} e-mail(s) de {remetente}.")
                for i, msg_id in enumerate(ids, start=1):
                    mail.store(msg_id, "+FLAGS", "\\Deleted")
                    print(f"Excluindo {i} de {total} de {remetente}...")
                mail.expunge()
            else:
                print(f"Não foi possível buscar e-mails de {remetente}.")
        
        mail.close()
        mail.logout()
        print("E-mails apagados com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    apagar_emails()
