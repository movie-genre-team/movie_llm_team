# 🎬 Classificador de Gênero de Filmes  

Interface gráfica em Python para **classificação automática de gêneros de filmes** a partir de sinopses, usando **modelos Transformers** (Hugging Face).  

---

## 🧩 Visão Geral  

Este projeto utiliza **PyTorch** e **Transformers** para prever o gênero de um filme com base em sua sinopse.  
A interface gráfica foi desenvolvida com **Tkinter**, exibindo os gêneros mais prováveis e um gráfico com as probabilidades.  

---

## 🛠️ Requisitos  

- Python 3.9 ou superior  
- As pastas locais `movie_genre_model/` e `movie_genre_tokenizer/` (já existentes localmente, não versionadas)  

---

## ⚙️ Instalação  

### 1️⃣ Crie e ative o ambiente virtual  

#### 💻 No Windows (cmd ou PowerShell)
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### 🐧 No Linux ou macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2️⃣ Instale as dependências  

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Estrutura esperada de pastas  

```
📦 movie-genre-classifier/
 ┣ 📁 movie_genre_model/          ← baixada automaticamente na primeira execução
 ┣ 📁 movie_genre_tokenizer/      ← baixada automaticamente na primeira execução
 ┣ 📁 out/                        ← criada automaticamente
 ┣ 📄 app_gui.py
 ┣ 📄 infer_utils.py
 ┣ 📄 baixar_movie_genre_model.py
 ┣ 📄 baixar_movie_genre_tokenizer.py
 ┣ 📄 test.py
 ┣ 📄 requirements.txt
 ┣ 📄 .gitignore
 ┗ 📄 README.md

```

> ⚠️ As pastas `movie_genre_model/` e `movie_genre_tokenizer/` **devem existir localmente**, mas estão **no `.gitignore`** e **não devem ser commitadas**.  

---

### 4️⃣ Inicialize o arquivo de metadados  

Antes de usar a interface, gere o arquivo `out/metadata.pkl` com os gêneros padrão executando:  

```bash
python test.py
```

Isso criará a pasta `out/` e salvará o arquivo de metadados com os gêneros iniciais.

---

### 5️⃣ Execute a aplicação  

```bash
python app_gui.py
```

A janela **"Classificador de Gênero de Filmes"** será aberta.  
Digite uma sinopse, clique em **"Prever"**, e veja os gêneros mais prováveis e suas probabilidades.  

---

## 🧠 Como funciona  

1. O modelo Transformer é carregado de `movie_genre_model/`  
2. O tokenizer é carregado de `movie_genre_tokenizer/`  
3. A sinopse é processada e as probabilidades de cada gênero são calculadas  
4. O resultado é exibido em uma tabela e em um gráfico de barras  

---

## 📦 Dependências Principais  

| Biblioteca | Uso principal |
|-------------|----------------|
| `transformers` | Carregamento de modelo e tokenizer |
| `torch` | Execução e inferência |
| `numpy`, `pandas` | Manipulação numérica e dados |
| `matplotlib` | Plotagem do gráfico de probabilidades |
| `pillow` | Exibição de imagens na interface |
| `tkinter` | Interface gráfica |
| `PySimpleGUI` | Alternativa gráfica (não usada por padrão) |

---

## 🧪 Teste rápido  

Após configurar o ambiente e gerar o `metadata.pkl`, rode:  
```bash
python app_gui.py
```
Digite algo como:
> "Um grupo de amigos descobre uma nave alienígena escondida no deserto e tenta evitar uma invasão."

O modelo exibirá as probabilidades para gêneros como **Ficção científica**, **Ação**, etc.

---

## 🔒 .gitignore  

O repositório já inclui um `.gitignore` configurado para ignorar:
- `.venv/`
- `__pycache__/`
- `.idea/`, `.vscode/`
- `*.pyc`, `*.pyo`
- `*.safetensors`
- `movie_genre_model/`
- `movie_genre_tokenizer/`

---

## 🧰 Tecnologias  

- **Python 3.10+**
- **PyTorch**
- **Transformers (Hugging Face)**
- **Tkinter**
- **Matplotlib**
- **gdown**

---

## 🧑‍💻 Autores  

Projeto desenvolvido por João Pedro Soares dos Santos 🎓  

---

## 📝 Licença  

Este projeto é distribuído sob a licença **MIT**.  
Sinta-se livre para usar, modificar e distribuir com os devidos créditos.

---

## ⭐ Dica  

Se desejar empacotar este projeto como um aplicativo standalone, você pode usar:  
```bash
pip install pyinstaller
pyinstaller --onefile app_gui.py
```
O executável será gerado na pasta `dist/`.
