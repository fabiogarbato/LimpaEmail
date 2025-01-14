import configparser
import imaplib
import email
from email.header import decode_header

imaplib.Debug = 4
CHUNK_SIZE = 500
TIMEOUT = 600

def listar_remetentes():
    try:
        config = configparser.ConfigParser()
        config.read("config.ini")

        IMAP_SERVER = config["Email"]["IMAP_SERVER"]
        EMAIL_USER = config["Email"]["EMAIL_USER"]
        EMAIL_PASS = config["Email"]["EMAIL_PASS"]

        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=TIMEOUT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX")

        status, message_numbers = mail.search(None, "ALL")
        if status != "OK":
            return {
                "status": "erro",
                "mensagem": "Não foi possível buscar os e-mails."
            }

        ids = message_numbers[0].split()
        total_ids = len(ids)

        remetentes_dict = {}
        if total_ids == 0:
            mail.close()
            mail.logout()
            return {
                "status": "ok",
                "total_emails": 0,
                "top_5_remetentes": []
            }

        current_chunk_start = 0
        while current_chunk_start < total_ids:
            current_chunk_end = min(current_chunk_start + CHUNK_SIZE, total_ids)
            chunk_ids = ids[current_chunk_start:current_chunk_end]
            ids_str = b",".join(chunk_ids)

            status, response = mail.fetch(ids_str, "(BODY[HEADER.FIELDS (FROM)])")
            if status == "OK":
                for resp in response:
                    if isinstance(resp, tuple):
                        raw_header = resp[1]
                        if raw_header:
                            msg = email.message_from_bytes(raw_header)
                            remetente_bruto = msg["From"]
                            if remetente_bruto:
                                parts = decode_header(remetente_bruto)
                                decodificado = ""
                                for decoded, charset in parts:
                                    if isinstance(decoded, bytes):
                                        if not charset or "unknown" in str(charset).lower():
                                            charset = "utf-8"
                                        try:
                                            decodificado += decoded.decode(charset, errors="ignore")
                                        except:
                                            decodificado += decoded.decode("latin-1", errors="ignore")
                                    else:
                                        decodificado += str(decoded)
                                remetente = decodificado.strip().lower()
                                remetentes_dict[remetente] = remetentes_dict.get(remetente, 0) + 1

            current_chunk_start = current_chunk_end

        mail.close()
        mail.logout()

        remetentes_ordenados = sorted(remetentes_dict.items(), key=lambda x: x[1], reverse=True)
        top_5 = [
            {"remetente": rem, "quantidade": qtde}
            for rem, qtde in remetentes_ordenados[:5]
        ]

        return {
            "status": "ok",
            "total_emails": total_ids,
            "top_5_remetentes": top_5
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Ocorreu um erro ao listar remetentes: {e}"
        }

def limpar_emails(remetentes=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    IMAP_SERVER = config["Email"]["IMAP_SERVER"]
    EMAIL_USER = config["Email"]["EMAIL_USER"]
    EMAIL_PASS = config["Email"]["EMAIL_PASS"]
    if remetentes is None:
        remetentes = config["Email"]["REMETENTES"].split(",")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=TIMEOUT)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("INBOX")
    encontrou_emails = False
    for remetente in remetentes:
        remetente = remetente.strip()
        status, message_numbers = mail.search(None, f'(FROM "{remetente}")')
        if status == "OK":
            ids = message_numbers[0].split()
            if ids:
                encontrou_emails = True
                for msg_id in ids:
                    try:
                        mail.store(msg_id, "+FLAGS", "\\Deleted")
                    except:
                        pass
                try:
                    mail.expunge()
                except:
                    pass
    mail.close()
    mail.logout()
    if encontrou_emails:
        return {"status": "ok", "mensagem": "E-mails apagados com sucesso!"}
    else:
        return {"status": "ok", "mensagem": "Nenhum e-mail para apagar, mas operação concluída com sucesso."}
