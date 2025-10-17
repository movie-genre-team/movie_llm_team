# infer_utils.py

import os
import subprocess
import sys
import pickle
from typing import List, Dict, Tuple, Union
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import matplotlib.pyplot as plt
MODEL_DIR = "movie_genre_model"
TOKENIZER_DIR = "movie_genre_tokenizer"
METADATA_PATH = os.path.join("out", "metadata.pkl")  # opcional, se existir terá labels

DEFAULT_GENRES = ["Ação", "Comédia", "Drama", "Ficção científica", "Terror"]
def ensure_model_and_tokenizer_present():
    """Garante que as pastas do modelo e tokenizer existam e estejam preenchidas."""
    # Model
    if not os.path.exists(MODEL_DIR) or len(os.listdir(MODEL_DIR)) == 0:
        print(f"📥 Pasta '{MODEL_DIR}' ausente ou vazia. Baixando modelo...")
        subprocess.run([sys.executable, "baixar_movie_genre_model.py"], check=True)
    else:
        print(f"✅ Pasta '{MODEL_DIR}' já contém arquivos.")

    # Tokenizer
    if not os.path.exists(TOKENIZER_DIR) or len(os.listdir(TOKENIZER_DIR)) == 0:
        print(f"📥 Pasta '{TOKENIZER_DIR}' ausente ou vazia. Baixando tokenizer...")
        subprocess.run([sys.executable, "baixar_movie_genre_tokenizer.py"], check=True)
    else:
        print(f"✅ Pasta '{TOKENIZER_DIR}' já contém arquivos.")


# === Chama antes de carregar modelo ===
ensure_model_and_tokenizer_present()

def _ensure_metadata_exists(default_genres: List[str] = DEFAULT_GENRES, path: str = METADATA_PATH) -> dict:
    """Garante que out/metadata.pkl exista. Se não existir, cria com default_genres."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        meta = {"genres": default_genres, "top_k": None}
        with open(path, "wb") as f:
            pickle.dump(meta, f)
        print(f"⚠ metadata não encontrado. Criado {path} com gêneros padrão: {default_genres}")
        return meta
    try:
        with open(path, "rb") as f:
            meta = pickle.load(f)
        # validação simples
        if not isinstance(meta, dict) or "genres" not in meta:
            print("⚠ metadata.pkl com formato inesperado. Recriando com gêneros padrão.")
            meta = {"genres": default_genres, "top_k": None}
            with open(path, "wb") as f:
                pickle.dump(meta, f)
        return meta
    except Exception as e:
        print("⚠ Erro lendo metadata.pkl:", e)
        # recria
        meta = {"genres": default_genres, "top_k": None}
        with open(path, "wb") as f:
            pickle.dump(meta, f)
        return meta

def load_model_and_tokenizer(model_dir: str = MODEL_DIR,
                             tokenizer_dir: str = TOKENIZER_DIR,
                             device: str = None) -> Tuple[object, object, List[str], str]:
    """
    Carrega tokenizer, model e labels.
    Retorna: tokenizer, model, labels, device
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    # Carrega tokenizer e modelo (usa tokenizer_dir se existir, senão model_dir)
    tokenizer_path = tokenizer_dir if os.path.exists(tokenizer_dir) else model_dir
    print("Carregando tokenizer de:", tokenizer_path)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    print("Carregando modelo de:", model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.to(device)
    model.eval()

    # tenta obter labels do metadata (cria se não existir)
    meta = _ensure_metadata_exists()
    labels = None
    if isinstance(meta, dict):
        if "genres" in meta and isinstance(meta["genres"], list) and len(meta["genres"]) > 0:
            labels = [str(x) for x in meta["genres"]]

    # se não encontrou em metadata, tenta config.id2label
    if labels is None:
        cfg = getattr(model, "config", None)
        id2label = getattr(cfg, "id2label", None) if cfg is not None else None
        if isinstance(id2label, dict) and len(id2label) > 0:
            try:
                ordered = [id2label[str(i)] if str(i) in id2label else id2label.get(i) for i in range(len(id2label))]
                labels = ordered
            except Exception:
                labels = [id2label[k] for k in sorted(id2label.keys(), key=lambda x: int(x) if str(x).isdigit() else x)]

    # fallback: rótulos numéricos
    if labels is None:
        n = getattr(model.config, "num_labels", None) or 1
        labels = [f"label_{i}" for i in range(int(n))]
        print("⚠ Nenhum labels legível encontrado. Usando labels numéricos como fallback.")

    print(f"Labels carregados: {labels}")
    return tokenizer, model, labels, device

def _logits_to_probs(logits: np.ndarray, model) -> np.ndarray:
    """
    Converte logits em probabilidades. Usa sigmoid para multi-label e softmax para multiclass.
    """
    if logits is None:
        return np.array([])
    logits = np.array(logits).squeeze()
    if logits.ndim == 0:
        logits = np.array([float(logits)])

    problem_type = getattr(model.config, "problem_type", None)
    if problem_type == "multi_label_classification":
        probs = 1 / (1 + np.exp(-logits))  # sigmoid
    else:
        exps = np.exp(logits - np.max(logits))
        probs = exps / exps.sum()
    return probs

def predict_probs(text: str, tokenizer, model, device: str) -> np.ndarray:
    """
    Retorna numpy array de probabilidades (ordeadas pelo index das labels).
    """
    if not isinstance(text, str):
        text = str(text)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits.cpu().numpy()
    probs = _logits_to_probs(logits, model)
    return probs

def predict_genres(text: str, tokenizer, model, labels: List[str], device: str) -> Dict[str, float]:
    """
    Retorna um dict {label: prob} (não ordenado).
    """
    probs = predict_probs(text, tokenizer, model, device)
    n = len(labels)
    if probs.shape[0] != n:
        # ajustar tamanho se necessário
        if probs.shape[0] < n:
            padded = np.zeros(n, dtype=float)
            padded[:probs.shape[0]] = probs
            probs = padded
        else:
            probs = probs[:n]
    return {labels[i]: float(probs[i]) for i in range(len(labels))}

def plot_probabilities(probs: Union[Dict[str,float], np.ndarray], outpath: str = "probs.png") -> str:
    """
    Recebe dict label->prob ou array (assumindo ordem das labels conhecida fora) e salva gráfico.
    Retorna caminho do arquivo salvo.
    """
    if isinstance(probs, np.ndarray):
        labels = [f"label_{i}" for i in range(len(probs))]
        items = list(zip(labels, probs.tolist()))
    elif isinstance(probs, dict):
        items = list(probs.items())
    else:
        raise ValueError("probs deve ser dict ou numpy array")

    items = sorted(items, key=lambda x: x[1], reverse=True)
    names = [x[0] for x in items]
    values = [x[1] for x in items]

    plt.figure(figsize=(10, 5))
    y_pos = np.arange(len(names))
    plt.barh(y_pos, values[::-1])
    plt.yticks(y_pos, names[::-1])
    plt.xlim(0, 1)
    plt.xlabel("Probabilidade")
    plt.title("Probabilidade por gênero")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
    return outpath
