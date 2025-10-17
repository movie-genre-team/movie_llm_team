# app_gui_tk.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import tempfile
import os
import threading

from infer_utils import load_model_and_tokenizer, predict_genres, plot_probabilities

# === Variáveis globais do app ===
tokenizer = None
model = None
labels = None
device = None

def load_model_background(lbl_status):
    """Carrega o modelo em thread de background para não travar a UI."""
    global tokenizer, model, labels, device
    try:
        lbl_status.config(text="Carregando modelo... (pode demorar)")
        tokenizer, model, labels, device = load_model_and_tokenizer()
        lbl_status.config(text=f"Modelo carregado. {len(labels)} rótulos encontrados.")
        # habilitar botão prever
        predict_btn.config(state="normal")
    except Exception as e:
        lbl_status.config(text="Erro ao carregar modelo.")
        messagebox.showerror("Erro", f"Falha ao carregar modelo/tokenizer:\n{e}")

def on_predict():
    synopsis = text_input.get("1.0", tk.END).strip()
    if not synopsis:
        messagebox.showwarning("Aviso", "Digite uma sinopse antes de prever!")
        return
    try:
        # Desabilitar botão para evitar múltiplos cliques
        predict_btn.config(state="disabled")
        status_var.set("Predizendo...")

        probs_dict = predict_genres(synopsis, tokenizer, model, labels, device)

        # preencher tabela top-5
        for item in tree.get_children():
            tree.delete(item)
        sorted_items = sorted(probs_dict.items(), key=lambda x: x[1], reverse=True)
        for genre, prob in sorted_items[:10]:
            tree.insert("", "end", values=(genre, f"{prob:.3f}"))

        # gerar gráfico temporário
        tmp = os.path.join(tempfile.gettempdir(), "probs_temp.png")
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass
        plot_probabilities(probs_dict, outpath=tmp)

        # carregar imagem e exibir
        img = Image.open(tmp)
        img = img.resize((560, 300))
        photo = ImageTk.PhotoImage(img)
        chart_label.config(image=photo)
        chart_label.image = photo

        status_var.set("Pronto")
    except Exception as e:
        messagebox.showerror("Erro na predição", str(e))
        status_var.set("Erro")
    finally:
        predict_btn.config(state="normal")

# === Criar janela principal ===
root = tk.Tk()
root.title("Classificador de Gênero de Filmes")
root.geometry("800x700")

mainframe = ttk.Frame(root, padding="10")
mainframe.pack(fill="both", expand=True)

ttk.Label(mainframe, text="Digite a sinopse do filme:").grid(row=0, column=0, sticky="w")
text_input = tk.Text(mainframe, height=8, width=90)
text_input.grid(row=1, column=0, columnspan=3, pady=5)

predict_btn = ttk.Button(mainframe, text="Prever", command=on_predict, state="disabled")
predict_btn.grid(row=2, column=0, sticky="w", pady=8)

clear_btn = ttk.Button(mainframe, text="Limpar", command=lambda: text_input.delete("1.0", tk.END))
clear_btn.grid(row=2, column=1, sticky="w", padx=6)

exit_btn = ttk.Button(mainframe, text="Sair", command=root.quit)
exit_btn.grid(row=2, column=2, sticky="e")

ttk.Label(mainframe, text="Top predições:").grid(row=3, column=0, sticky="w", pady=(10,0))
tree = ttk.Treeview(mainframe, columns=("Gênero", "Prob"), show="headings", height=8)
tree.heading("Gênero", text="Gênero")
tree.heading("Prob", text="Probabilidade")
tree.column("Gênero", width=300)
tree.column("Prob", width=120)
tree.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=5)

chart_label = ttk.Label(mainframe)
chart_label.grid(row=5, column=0, columnspan=3, pady=(10,0))

status_var = tk.StringVar(value="Carregando modelo...")
status_label = ttk.Label(mainframe, textvariable=status_var)
status_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=8)

# grid weight para expandir
mainframe.rowconfigure(4, weight=1)
mainframe.columnconfigure(0, weight=1)

# Carregar modelo em background thread
lbl_status = status_label
thread = threading.Thread(target=load_model_background, args=(lbl_status,), daemon=True)
thread.start()

root.mainloop()

