import configparser
import imaplib
import email
from email.header import decode_header

CHUNK_SIZE = 500

def listar_remetentes():
    try:
        print("[DEBUG] Lendo arquivo de configuração...")
        config = configparser.ConfigParser()
        config.read("config.ini")

        IMAP_SERVER = config["Email"]["IMAP_SERVER"]
        EMAIL_USER = config["Email"]["EMAIL_USER"]
        EMAIL_PASS = config["Email"]["EMAIL_PASS"]

        print("[DEBUG] Conectando ao servidor IMAP...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        print("[DEBUG] Realizando login...")
        mail.login(EMAIL_USER, EMAIL_PASS)
        print("[DEBUG] Selecionando INBOX...")
        mail.select("INBOX")

        print("[DEBUG] Buscando TODOS os e-mails (search ALL)...")
        status, message_numbers = mail.search(None, "ALL")
        if status != "OK":
            print("Não foi possível buscar os e-mails.")
            return

        ids = message_numbers[0].split()
        total_ids = len(ids)
        total_ids = 50000
        print(f"Total de e-mails encontrados na INBOX: {total_ids}")

        remetentes_dict = {}

        if total_ids == 0:
            print("[DEBUG] Não há nenhum e-mail na INBOX.")
            mail.close()
            mail.logout()
            return

        current_chunk_start = 0

        while current_chunk_start < total_ids:
            current_chunk_end = min(current_chunk_start + CHUNK_SIZE, total_ids)
            chunk_ids = ids[current_chunk_start:current_chunk_end]
            ids_str = b",".join(chunk_ids)

            print(f"[DEBUG] Fazendo fetch dos e-mails de {current_chunk_start} até {current_chunk_end - 1}...")

            try:
                status, response = mail.fetch(ids_str, "(BODY[HEADER.FIELDS (FROM)])")
                if status != "OK":
                    print(f"[DEBUG] Falha ao fazer fetch do chunk {current_chunk_start} - {current_chunk_end - 1}")
                else:
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
                                            if not charset or "unknown" in charset.lower():
                                                charset = "utf-8"
                                            try:
                                                decodificado += decoded.decode(charset, errors="ignore")
                                            except:
                                                decodificado += decoded.decode("latin-1", errors="ignore")
                                        else:
                                            decodificado += str(decoded)
                                    remetente = decodificado.strip().lower()
                                    remetentes_dict[remetente] = remetentes_dict.get(remetente, 0) + 1
            except Exception as e_fetch:
                print(f"[DEBUG] Erro ao fazer fetch do chunk {current_chunk_start} - {current_chunk_end - 1}: {e_fetch}")

            current_chunk_start = current_chunk_end

        print("[DEBUG] Fechando caixa de entrada e fazendo logout...")
        mail.close()
        mail.logout()

        remetentes_ordenados = sorted(remetentes_dict.items(), key=lambda x: x[1], reverse=True)

        if len(remetentes_ordenados) == 0:
            print("[DEBUG] Nenhum remetente encontrado.")
            return

        print("\nTop 500 remetentes com mais e-mails:")
        for i, (rem, qtde) in enumerate(remetentes_ordenados[:500], start=1):
            print(f"{i}. {rem} - {qtde} e-mail(s)")
    except Exception as e:
        print(f"[DEBUG] Ocorreu um erro ao listar remetentes: {e}")

def limpar_emails():
    try:
        print("[DEBUG] Lendo arquivo de configuração para limpeza...")
        config = configparser.ConfigParser()
        config.read("config.ini")

        IMAP_SERVER = config["Email"]["IMAP_SERVER"]
        EMAIL_USER = config["Email"]["EMAIL_USER"]
        EMAIL_PASS = config["Email"]["EMAIL_PASS"]
        REMETENTES = config["Email"]["REMETENTES"].split(",")

        print("[DEBUG] Conectando ao servidor IMAP para limpar...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX")

        for remetente in REMETENTES:
            remetente = remetente.strip()
            print(f"[DEBUG] Buscando e-mails de {remetente}...")
            status, message_numbers = mail.search(None, f'(FROM "{remetente}")')
            if status == "OK":
                ids = message_numbers[0].split()
                total = len(ids)
                print(f"Encontrados {total} e-mail(s) de {remetente}.")
                for i, msg_id in enumerate(ids, start=1):
                    try:
                        mail.store(msg_id, "+FLAGS", "\\Deleted")
                        print(f"[DEBUG] Marcado para exclusão {i} de {total} de {remetente} (ID: {msg_id.decode()})")
                    except Exception as e_mark:
                        print(f"[DEBUG] Erro ao marcar e-mail {msg_id.decode()} para exclusão: {e_mark}")
                try:
                    mail.expunge()
                    print(f"[DEBUG] Expunge realizado para {remetente}.")
                except Exception as e_expunge:
                    print(f"[DEBUG] Erro ao fazer expunge para {remetente}: {e_expunge}")
            else:
                print(f"Não foi possível buscar e-mails de {remetente}. Status: {status}")

        mail.close()
        mail.logout()
        print("E-mails apagados com sucesso!")
    except Exception as e:
        print(f"[DEBUG] Ocorreu um erro ao limpar e-mails: {e}")

def exibir_menu():
    print("> ============================")
    print("> Limpa Email Launcher")
    print("> ============================")
    print("> Selecione uma opção:")
    print("> [1] Listar remetentes/qtde")
    print("> [2] Limpar remetentes")
    print("> [0] Sair")
    print("> ============================\n")
    opcao = input("Digite o número da opção desejada: ")
    return opcao

def main():
    while True:
        opcao = exibir_menu()
        if opcao == "1":
            listar_remetentes()
        elif opcao == "2":
            limpar_emails()
        elif opcao == "0":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Tente novamente.")
        print("\n")

if __name__ == "__main__":
    main()
