# 💖 Treinamento do Modelo – Preditor de Insuficiência Cardíaca

Este repositório contém o **algoritmo de criação e teste do modelo** utilizado pela API. O pipeline treina um modelo de **classificação binária** (doença cardíaca: 0/1) a partir do dataset `heart.csv`, gera métricas e persiste **modelo** e **scaler** para uso em produção.

---

## 🗂️ Estrutura

```
.
├── main.py                       # Script de treino/avaliação do modelo
├── heart.csv                     # Dataset de entrada (features + HeartDisease)
├── X_train.csv  X_test.csv       # Features escalonadas (geradas pelo pipeline)
├── y_train.csv  y_test.csv       # Targets correspondentes
├── modelo_insuficiencia_cardiaca.pkl  # Modelo treinado (joblib)
├── scaler_dados.pkl                   # Scaler treinado (joblib)
└── requirements_model.txt        # Dependências para treino/avaliação
```

---
# Desativar o ambiente virtual, se estiver ativo
```bash
deactivate

# Remover toda a pasta do ambiente virtual
rm -rf .venv


## ⚙️ Ambiente

Crie e ative um ambiente virtual e instale as dependências do arquivo `requirements_model.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Se preferir versões mínimas (não fixas), você pode usar um requirements com **constraints `>=`** (ver seção “Alternativa com versões mínimas”).

---

## 🧠 Pipeline de Treinamento

O script `main.py` executa as seguintes etapas principais:

1. **Carregamento do dataset** `heart.csv` e checagem de nulos.  
2. **Codificação One‑Hot** das variáveis categóricas com `pd.get_dummies(drop_first=True)`.  
3. **Split treino/teste** estratificado (70/30) com `train_test_split`.  
4. **Escalonamento** das features com `StandardScaler` (fit no treino, transform em treino e teste).  
5. **Persistência** dos conjuntos escalonados (`X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`).  
6. **Treinamento** de uma **Regressão Logística** (`solver='liblinear'`, `random_state=42`).  
7. **Avaliação** com acurácia e `classification_report` (precision, recall, f1).  
8. **Exportação** dos artefatos: `modelo_insuficiencia_cardiaca.pkl` e `scaler_dados.pkl` (via `joblib`).

> O **alvo** (variável dependente) é a coluna `HeartDisease` (0/1).  
> Para aplicações clínicas, recomenda‑se acompanhar **Recall/Sensibilidade** (minimizar falsos negativos).

### Execução

```bash
python main.py
```

Após a execução, você deverá ver no console as métricas do modelo e os arquivos `.pkl`/`.csv` serão gerados na raiz do projeto.

---

## 🔬 Métricas e Relatórios

O script imprime no console:  
- **Acurácia** no conjunto de teste;  
- **Classification Report**: *precision*, *recall*, *f1‑score* por classe;  
- *Observação*: ajuste de limiar pode ser considerado conforme a necessidade (ex.: priorizar recall).

---

## 🔁 Reprodutibilidade

- `random_state=42` no split e no modelo;  
- `StandardScaler` treinado apenas no treino (evita *data leakage*);  
- As colunas finais usadas pelo modelo ficam registradas na propriedade `model.feature_names_in_` (útil para alinhar produção).

---

## 🧩 Handoff para Produção (API)

Na etapa de inferência (API), é **obrigatório alinhar** o vetor de entrada às **mesmas colunas** do treino:

- Usar `model.feature_names_in_` para reordenar/“completar” dummies;  
- Aplicar **o mesmo `scaler_dados.pkl`** (fit no treino) ao vetor antes de `predict`/`predict_proba`;  
- Em caso de divergência de colunas, usar `X_train.csv` como **fonte da verdade** para o conjunto de features.

---

## 🧪 Exemplo de uso dos artefatos (inferência local)

```python
import joblib
import pandas as pd

# 1) Carrega artefatos
model = joblib.load('modelo_insuficiencia_cardiaca.pkl')
scaler = joblib.load('scaler_dados.pkl')

# 2) Novo paciente (exemplo)
novo = pd.DataFrame([{
    "Age": 50, "Sex": "M", "ChestPainType": "NAP", "RestingBP": 125,
    "Cholesterol": 190, "FastingBS": 0, "RestingECG": "Normal",
    "MaxHR": 165, "ExerciseAngina": "N", "Oldpeak": 0.2, "ST_Slope": "Up"
}])

# 3) One‑Hot e alinhamento
X_cols = model.feature_names_in_
novo_d = pd.get_dummies(novo, drop_first=True)
for c in set(X_cols) - set(novo_d.columns):
    novo_d[c] = 0
novo_alinhado = novo_d[X_cols]

# 4) Escalonar e prever
X_scaled = scaler.transform(novo_alinhado)
pred = model.predict(X_scaled)[0]
prob = model.predict_proba(X_scaled)[0, 1]
print("Classe:", pred, "Prob.:", f"{prob:.2%}")
```

---

## 🪪 Licença
Uso acadêmico e educacional. Ajuste conforme sua necessidade.

---

## 📦 Alternativa com versões mínimas (requirements “aberto”)

Se preferir dependências com `>=`:

```
pandas>=2.0.0
scikit-learn>=1.3.0
joblib>=1.3.0
numpy>=1.25.0
# opcionais
matplotlib>=3.8.0
jupyter>=1.0.0
```
