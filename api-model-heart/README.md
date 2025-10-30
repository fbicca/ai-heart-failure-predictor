# 💖 API – Preditor de Insuficiência Cardíaca (FastAPI)

API desenvolvida em **FastAPI** para prever o risco de **insuficiência cardíaca** com base em 12 parâmetros clínicos.
O modelo foi treinado com **scikit-learn (Regressão Logística)** e utiliza **StandardScaler** para normalização.

---

## 🚀 Endpoints principais

| Endpoint         | Método | Descrição                                                     |
|------------------|--------|---------------------------------------------------------------|
| `/health`        | GET    | Verifica se o modelo e o scaler foram carregados corretamente |
| `/predict`       | POST   | Realiza predição individual de risco cardíaco                 |
| `/predict-batch` | POST   | Permite predição em lote                                      |
| `/debug-vector`  | POST   | Retorna o vetor processado e colunas utilizadas               |

---

## ⚙️ Instalação e execução

### 1️⃣ Instalar dependências
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2️⃣ Estrutura esperada
```
.
├── api.py
├── modelo_insuficiencia_cardiaca.pkl
├── scaler_dados.pkl
├── exemplos.txt
└── requirements_api.txt
```

### 3️⃣ Executar a API
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## 📬 Exemplo de uso (HTTPie ou curl)

### `/predict`
```bash
http POST :8000/predict   Age:=52 Sex=M ChestPainType=ASY RestingBP:=110 Cholesterol:=130   FastingBS:=0 RestingECG=Normal MaxHR:=78 Exang=não Oldpeak:=0.0 ST_Slope=Flat Thal=Normal
```

**Resposta:**
```json
{
  "prediction": 1,
  "label": "ALTO_RISCO",
  "probability_positive": 0.91,
  "warnings": [],
  "model_info": {
    "features_expected": ["Age", "Sex", "ChestPainType", "..."],
    "model_class": "LogisticRegression"
  }
}
```

---

## 🧩 Parâmetros aceitos

| Campo           | Tipo     | Descrição                                     |
|-----------------|----------|-----------------------------------------------|
| `Age`           | int      | Idade (1–120)                                 |
| `Sex`           | str      | `M` ou `F`                                    |
| `ChestPainType` | str      | `TA`, `ATA`, `NAP`, `ASY`                     |
| `RestingBP`     | int      | Pressão arterial de repouso (70–250 mmHg)     |
| `Cholesterol`   | int      | Colesterol total (100–600 mg/dL)              |
| `FastingBS`     | int/bool | 0 = normal, 1 = glicemia alterada             |
| `RestingECG`    | str      | `Normal`, `ST`, `LVH`                         |
| `MaxHR`         | int      | Frequência cardíaca máxima (40–250 bpm)       |
| `Exang`         | str      | “sim” / “não”                                 |
| `Oldpeak`       | float    | Depressão ST (0.0–10.0)                       |
| `ST_Slope`      | str      | `Up`, `Flat`, `Down`                          |
| `Thal`          | str      | `Normal`, `Fixed defect`, `Reversible defect` |

---

## 🧪 Casos de teste

### 🟢 Baixo Risco
```bash
http POST :8000/predict   Age:=50 Sex=M ChestPainType=NAP RestingBP:=125 Cholesterol:=190   FastingBS:=0 RestingECG=Normal MaxHR:=165 Exang=não Oldpeak:=0.2 ST_Slope=Up Thal=Normal
```

### 🔴 Alto Risco
```bash
http POST :8000/predict   Age:=68 Sex=M ChestPainType=ASY RestingBP:=160 Cholesterol:=290   FastingBS:=1 RestingECG=LVH MaxHR:=82 Exang=sim Oldpeak:=3.1 ST_Slope=Flat Thal="Fixed defect"
```

---

## 🧠 Modelo

- **Tipo:** LogisticRegression
- **Scaler:** StandardScaler
- **Features:** 11–12 parâmetros clínicos
- **Métrica:** Recall (reduz falsos negativos)

---

## 🩺 Health Check
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

**Resposta:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "scaler_loaded": true,
  "feature_columns_source": "model.feature_names_in_"
}
```

---

## 📜 Licença
Uso acadêmico e educacional.  
Desenvolvido por **Filipe Bicca e Edmilson Teixeira (50+Dev)**.
