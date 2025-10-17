import os
import gdown

# === Configurações ===
FOLDER_URL = "https://drive.google.com/drive/folders/1PQ3wCx1mYGUPz_yeuy_HC098tZnuMxcG?usp=sharing"  # movie_genre_tokenizer
LOCAL_DIR = "movie_genre_tokenizer"  # nome da pasta correta

# === Passo 1: cria a pasta se não existir ===
os.makedirs(LOCAL_DIR, exist_ok=True)

# === Passo 2: verifica se está vazia ===
if len(os.listdir(LOCAL_DIR)) == 0:
    print(f"📂 Pasta '{LOCAL_DIR}' está vazia. Iniciando download do Google Drive...")

    # === Passo 3: baixar todo o conteúdo da pasta ===
    gdown.download_folder(
        url=FOLDER_URL,
        output=LOCAL_DIR,
        quiet=False,
        use_cookies=False
    )

    print("✅ Download concluído para:", LOCAL_DIR)
else:
    print(f"✅ A pasta '{LOCAL_DIR}' já contém arquivos. Nenhum download necessário.")
