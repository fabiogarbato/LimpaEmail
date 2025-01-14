import tkinter as tk
import tkinter.scrolledtext as st
import sys
import io
import backend

def listar_remetentes():
    antigo_stdout = sys.stdout
    sys.stdout = buffer_captura = io.StringIO()
    backend.listar_remetentes()
    saida = buffer_captura.getvalue()
    sys.stdout = antigo_stdout
    texto_saida.insert(tk.END, saida + "\n")

def limpar_emails():
    antigo_stdout = sys.stdout
    sys.stdout = buffer_captura = io.StringIO()
    backend.limpar_emails()
    saida = buffer_captura.getvalue()
    sys.stdout = antigo_stdout
    texto_saida.insert(tk.END, saida + "\n")

janela = tk.Tk()
janela.title("Limpa Email Launcher")
janela.minsize(600, 400)
janela.configure(bg="#f2f2f2")

quadro = tk.Frame(janela, bg="#f2f2f2")
quadro.pack(padx=10, pady=10, fill=tk.BOTH)

estilo_botao = {
    "bg": "#4CAF50",
    "fg": "white",
    "activebackground": "#45a049",
    "padx": 10,
    "pady": 5,
    "relief": tk.FLAT,
    "font": ("Arial", 10, "bold")
}

botao_listar = tk.Button(quadro, text="Listar Remetentes", command=listar_remetentes, **estilo_botao)
botao_listar.pack(fill=tk.X, pady=5)

botao_limpar = tk.Button(quadro, text="Limpar Remetentes", command=limpar_emails, **estilo_botao)
botao_limpar.pack(fill=tk.X, pady=5)

botao_sair = tk.Button(quadro, text="Sair", command=janela.quit, bg="#f44336", fg="white", activebackground="#e53935",
                       padx=10, pady=5, relief=tk.FLAT, font=("Arial", 10, "bold"))
botao_sair.pack(fill=tk.X, pady=5)

texto_saida = st.ScrolledText(janela, width=80, height=20, bg="white", fg="black", wrap="word")
texto_saida.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

janela.mainloop()
