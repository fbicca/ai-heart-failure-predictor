# BotHealth – Chatbot de Anamnese (Flask) + Integração com API de Predição

Chatbot em **Flask** para coletar 12 parâmetros clínicos de risco cardíaco, gerar um **resumo para confirmação** e enviar o payload para uma **API externa de predição**.  
Inclui **explicação dinâmica** do resultado (alto/baixo risco) a partir dos valores informados.

---

## 🔎 Visão geral

- Backend em **Flask** com sessão simples.
- Coleta guiada (**idade → sexo → dor no peito → … → Thal**), gera **resumo** e pede **confirmação** para enviar à API de predição. fileciteturn5file1
- **Formatação** do resumo com funções utilitárias (ex.: `_fmt_bool01`, `_fmt_ecg`, `_fmt_slope`, `_fmt_thal`). fileciteturn5file0
- **Validações** robustas para cada passo (ex.: `valida_idade`, `valida_pressao`, `valida_ecg`, `valida_slope`, etc.). fileciteturn5file2
- Integração com API externa via `API_PREDICT_URL` (método `POST /predict`) e retorno amigável com **classe**, **probabilidade**, **avisos** e **explicação**.

---

## 🗂️ Estrutura dos principais arquivos

```
.
├─ app.py            # Flask app, fluxo do chatbot e integração com API fileciteturn5file1
├─ anamnese.py       # Helpers de formatação e resumo final               fileciteturn5file0
├─ validation.py     # Funções de validação de cada entrada               fileciteturn5file2
├─ templates/        # (opcional) templates Jinja2 (index.html etc.)
└─ static/           # (opcional) CSS/JS/Imagens
```

---

## 🔧 Requisitos

Ver `requirements.txt` gerado junto com este README (Flask, requests, python-dotenv).

---

# 1. Desativar o ambiente virtual, se estiver ativo

````bash
deactivate

# 2. Remover toda a pasta do ambiente virtual
rm -rf .venv


## ⚙️ Configuração

# 1. **Criar e ativar o ambiente virtual**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
````

2. **Variáveis de ambiente**

   - `API_PREDICT_URL` (obrigatória em produção): URL do endpoint de predição, p.ex.
     ```bash
     export API_PREDICT_URL="http://localhost:8000/predict"
     ```
   - `FLASK_SECRET_KEY` (opcional): chave de sessão do Flask.
     ```bash
     export FLASK_SECRET_KEY="uma_chave_secreta_segura"
     ```
   - `PORT` (opcional): porta do Flask (default: `5000`).

3. **Executar em modo desenvolvimento**

   ```bash
   export FLASK_APP=app.py
   flask run --host 0.0.0.0 --port ${PORT:-5000}
   ou flask run --host 0.0.0.0 --port ${PORT:-5000} --debug
   ```

4. **Executar em produção (exemplo com gunicorn)**
   ```bash
   gunicorn -w 2 -b 0.0.0.0:5000 app:app
   ```

> **Dica:** Se a API de predição for o serviço em FastAPI que você já tem, garanta que está rodando e acessível em `API_PREDICT_URL` antes de iniciar o bot.

---

## 🚦 Uso – endpoint do chatbot

- **POST** `http://localhost:5000/chat`
  ```json
  { "msg": "sim" }
  ```
  Responda às perguntas até ver o **resumo**.  
  Envie **“sim”** para confirmar e disparar a predição.

O **payload** enviado para a API é montado por `_build_api_payload` e contém **12 campos** no formato esperado pela sua API (Age, Sex, ChestPainType, RestingBP, Cholesterol, FastingBS, RestingECG, MaxHR, Exang, Oldpeak, ST_Slope, Thal). fileciteturn5file1

---

## 🧠 Lógica de validação e formatação

- **Validações** (exemplos):
  - `valida_idade` (1–120), `valida_pressao` (70–250), `valida_colesterol` (100–600),  
    `valida_jejum` (sim/não → 1/0), `valida_ecg` (Normal/ST/LVH), `valida_maxhr` (40–250),  
    `valida_exang` (sim/não → 1/0), `valida_oldpeak` (0.0–10.0), `valida_slope` (Up/Flat/Down), `valida_thal`. fileciteturn5file2
- **Resumo**: montado por `montar_resumo(session)`, usando helpers como `_fmt_bool01`, `_fmt_ecg`, `_fmt_slope`, `_fmt_thal` para exibição amigável. fileciteturn5file0

---

## 🔮 Predição e explicação dinâmica

Ao confirmar “sim”, o bot chama a API em `API_PREDICT_URL` (`POST /predict`).  
A resposta é renderizada com:

- **Classe** (`ALTO_RISCO`/`BAIXO_RISCO`), **probabilidade** e **avisos** da API. fileciteturn5file1
- **Explicação dinâmica** gerada por `gerar_explicacao(payload, label)` com base nos 12 parâmetros (ex.: idade, MaxHR, ST_Slope, FastingBS, Exang, Oldpeak, ECG, ChestPainType). fileciteturn5file1

---

## 🧪 Testes rápidos (HTTPie)

**Baixo risco (esperado)**

```bash
http POST :8000/predict   Age:=50 Sex=M ChestPainType=NAP RestingBP:=125 Cholesterol:=190   FastingBS:=0 RestingECG=Normal MaxHR:=165 Exang=não Oldpeak:=0.2 ST_Slope=Up Thal=Normal
```

**Alto risco (esperado)**

```bash
http POST :8000/predict   Age:=65 Sex=M ChestPainType=ASY RestingBP:=150 Cholesterol:=280   FastingBS:=1 RestingECG=LVH MaxHR:=85 Exang=sim Oldpeak:=2.8 ST_Slope=Flat Thal="Fixed defect"
```

> Ajuste a URL se sua API não estiver em `localhost:8000`.

---

## 🛠️ Solução de problemas

- **Tudo sai ~50% e classe ALTO_RISCO**  
  Sinal de **desalinhamento de colunas** entre treino e predição.  
  Verifique a API: use `GET /health` (fonte das colunas) e `POST /debug-vector` para checar `n_features` e vetor escalado.  
  Confirme o `API_PREDICT_URL` no ambiente do bot. fileciteturn5file1

- **Erro “cannot execute: required file not found” ao rodar `pip` no venv**  
  Recrie o venv: `rm -rf .venv && python3 -m venv .venv && source .venv/bin/activate && python -m pip install --upgrade pip`.

---

## 📄 Licença

Uso acadêmico e educacional. Adapte conforme necessidade do seu curso/projeto.
