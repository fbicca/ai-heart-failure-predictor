# api.py - FastAPI para predição de risco cardíaco (12 inputs, PT/EN, fallback de colunas via X_train.csv)
# Execução: uvicorn api:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal, Dict, Any
import pandas as pd
import numpy as np
import joblib
import os

# ------------------------------------------------------------------------------
# Config
# ------------------------------------------------------------------------------
MODEL_PATH = os.getenv("MODEL_PATH", "modelo_insuficiencia_cardiaca.pkl")
SCALER_PATH = os.getenv("SCALER_PATH", "scaler_dados.pkl")
# Fallback de colunas do treino (usa cabeçalho do CSV para recuperar ordem/nomes)
FEATURE_COLUMNS_PATH = os.getenv("FEATURE_COLUMNS_PATH", "X_train.csv")

app = FastAPI(title="Heart Failure Predictor API", version="1.2.0")


# ------------------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------------------
class Patient(BaseModel):
    # 12 entradas (com normalização PT/EN via validadores)
    Age: int = Field(..., ge=0, le=120)
    Sex: str  # M/F ou masculino/feminino
    ChestPainType: str  # TA/ATA/NAP/ASY + sinônimos
    RestingBP: float  # 70–250
    Cholesterol: float  # 100–600
    FastingBS: int | str | bool  # sim/não, 1/0
    RestingECG: str  # Normal/ST/LVH + sinônimos
    MaxHR: int  # 40–250
    # Aceita Exang e ExerciseAngina; será normalizado para ExerciseAngina ('Y'/'N')
    ExerciseAngina: Optional[str] = None
    Exang: Optional[int | str | bool] = None
    Oldpeak: float | str  # aceita vírgula
    ST_Slope: str  # Up/Flat/Down + sinônimos
    # Extra do chatbot
    Thal: Optional[str] = None

    # ---- Validadores (Pydantic v2) ----
    @field_validator('Sex')
    @classmethod
    def norm_sex(cls, v: str) -> str:
        s = str(v).strip().lower()
        if s in {'m','masc','masculino','male','homem'}: return 'M'
        if s in {'f','fem','feminino','female','mulher'}: return 'F'
        raise ValueError("Sexo inválido. Use M/F ou masculino/feminino.")

    @field_validator('ChestPainType')
    @classmethod
    def norm_cpt(cls, v: str) -> str:
        s = str(v).strip().lower()
        mapping = {
            'ta':'TA','típica':'TA','tipica':'TA','typical angina':'TA',
            'ata':'ATA','atípica':'ATA','atipica':'ATA','atypical angina':'ATA',
            'nap':'NAP','não anginosa':'NAP','nao anginosa':'NAP','non-anginal pain':'NAP',
            'asy':'ASY','assintomática':'ASY','assintomatica':'ASY','asymptomatic':'ASY'
        }
        return mapping.get(s, s.upper())

    @field_validator('RestingBP')
    @classmethod
    def check_bp(cls, v) -> float:
        try:
            bp = float(str(v).replace(',', '.'))
        except Exception:
            raise ValueError("RestingBP inválido.")
        if not (70 <= bp <= 250):
            raise ValueError("RestingBP fora do intervalo recomendado (70–250 mmHg).")
        return bp

    @field_validator('Cholesterol')
    @classmethod
    def check_chol(cls, v) -> float:
        try:
            c = float(str(v).replace(',', '.'))
        except Exception:
            raise ValueError("Cholesterol inválido.")
        if not (100 <= c <= 600):
            raise ValueError("Cholesterol fora do intervalo recomendado (100–600 mg/dL).")
        return c

    @field_validator('FastingBS')
    @classmethod
    def norm_fbs(cls, v) -> int:
        s = str(v).strip().lower()
        if s in {'1','true','sim','yes'}: return 1
        if s in {'0','false','nao','não','no'}: return 0
        try:
            n = int(float(s))
            return 1 if n >= 1 else 0
        except Exception:
            raise ValueError("FastingBS inválido (use 1/0, sim/não).")

    @field_validator('RestingECG')
    @classmethod
    def norm_ecg(cls, v: str) -> str:
        s = str(v).strip().lower()
        mapping = {
            'normal':'Normal',
            'st':'ST','st-t wave abnormality':'ST','anormalidade st-t':'ST',
            'lvh':'LVH','left ventricular hypertrophy':'LVH','hipertrofia ventricular esquerda':'LVH'
        }
        return mapping.get(s, s.capitalize())

    @field_validator('MaxHR')
    @classmethod
    def check_hr(cls, v) -> int:
        try:
            hr = int(float(str(v).replace(',', '.')))
        except Exception:
            raise ValueError("MaxHR inválido.")
        if not (40 <= hr <= 250):
            raise ValueError("MaxHR fora do intervalo recomendado (40–250 bpm).")
        return hr

    @field_validator('Oldpeak')
    @classmethod
    def norm_oldpeak(cls, v) -> float:
        try:
            op = float(str(v).replace(',', '.'))
        except Exception:
            raise ValueError("Oldpeak inválido (use número, aceita vírgula).")
        if not (0.0 <= op <= 10.0):
            raise ValueError("Oldpeak fora do intervalo (0.0–10.0).")
        return op

    @field_validator('ST_Slope')
    @classmethod
    def norm_slope(cls, v: str) -> str:
        s = str(v).strip().lower()
        mapping = {
            'up':'Up','ascendente':'Up','asc':'Up',
            'flat':'Flat','plano':'Flat',
            'down':'Down','descendente':'Down','desc':'Down'
        }
        return mapping.get(s, s.capitalize())

    @field_validator('ExerciseAngina', mode='before')
    @classmethod
    def norm_exang1(cls, v):
        if v is None: return None
        s = str(v).strip().lower()
        if s in {'y','yes','sim'}: return 'Y'
        if s in {'n','no','nao','não'}: return 'N'
        return s.upper()

    @field_validator('Exang', mode='before')
    @classmethod
    def norm_exang2(cls, v):
        if v is None: return None
        s = str(v).strip().lower()
        if s in {'1','true','yes','sim'}: return 1
        if s in {'0','false','no','nao','não'}: return 0
        try:
            return 1 if int(float(s))>=1 else 0
        except Exception:
            raise ValueError("Exang inválido (use 1/0, sim/não).")

    @field_validator('Thal', mode='before')
    @classmethod
    def norm_thal(cls, v):
        if v is None: return None
        s = str(v).strip().lower()
        mapping = {
            'normal':'Normal',
            'fixed defect':'Fixed defect','defeito fixo':'Fixed defect',
            'reversible defect':'Reversible defect','defeito reversível':'Reversible defect','defeito reversivel':'Reversible defect'
        }
        return mapping.get(s, s.title())

    @model_validator(mode='after')
    def combine_exang(self):
        # Se Exang foi informado e ExerciseAngina não, convertê-lo (1->'Y', 0->'N')
        if self.Exang is not None and self.ExerciseAngina is None:
            self.ExerciseAngina = 'Y' if int(self.Exang)==1 else 'N'
        # Se ainda ausente, default conservador 'N'
        if self.ExerciseAngina is None:
            self.ExerciseAngina = 'N'
        return self


class PredictResponse(BaseModel):
    prediction: Literal[0,1]
    label: Literal["BAIXO_RISCO","ALTO_RISCO"]
    probability_positive: float
    model_info: Dict[str, Any]
    warnings: List[str] = []


# ------------------------------------------------------------------------------
# Carregar artefatos
# ------------------------------------------------------------------------------
def _load_artifacts():
    if not (os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH)):
        raise FileNotFoundError("Modelo e/ou scaler não encontrados. Treine e salve os arquivos .pkl.")
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler

MODEL, SCALER = _load_artifacts()


# ------------------------------------------------------------------------------
# Colunas esperadas (robusto com fallback para CSV)
# ------------------------------------------------------------------------------
def get_expected_columns() -> List[str]:
    """
    Retorna a lista/ordem de colunas esperadas pelo modelo.
    1) Se o modelo tiver feature_names_in_ com nomes de colunas, usa.
    2) Caso contrário, carrega do cabeçalho do X_train.csv (FEATURE_COLUMNS_PATH).
    """
    names = getattr(MODEL, "feature_names_in_", None)
    if names is not None:
        are_strings = all(isinstance(c, (str, bytes)) for c in names)
        if are_strings:
            return list(names)

    # Fallback: cabeçalho do arquivo de treino
    if not os.path.exists(FEATURE_COLUMNS_PATH):
        raise RuntimeError(
            "Não foi possível determinar as colunas esperadas. "
            "Defina FEATURE_COLUMNS_PATH para um CSV com o cabeçalho correto (ex.: X_train.csv)."
        )
    header = pd.read_csv(FEATURE_COLUMNS_PATH, nrows=0)
    cols = list(header.columns)
    if len(cols) == 0:
        raise RuntimeError(f"O arquivo {FEATURE_COLUMNS_PATH} não possui cabeçalho de colunas.")
    return cols


# ------------------------------------------------------------------------------
# Pré-processamento de uma linha e escala
# ------------------------------------------------------------------------------
def encode_align_scale(df_row: pd.DataFrame):
    """
    Normaliza entradas, faz get_dummies(drop_first=True), alinha para as colunas do treino
    e aplica o scaler.
    """
    # Se houver Exang mas não ExerciseAngina, inferir
    if 'Exang' in df_row.columns and 'ExerciseAngina' not in df_row.columns:
        df_row = df_row.copy()
        df_row['ExerciseAngina'] = df_row['Exang'].apply(lambda x: 'Y' if int(x)==1 else 'N')

    expected_cols = get_expected_columns()

    # One-Hot consistente com o treino (drop_first=True)
    dummies = pd.get_dummies(df_row, drop_first=True)

    # Adiciona colunas faltantes
    for col in expected_cols:
        if col not in dummies.columns:
            dummies[col] = 0

    # Remove extras e reordena
    dummies = dummies[expected_cols]

    # Checagem opcional de consistência com o scaler
    n_expected = len(expected_cols)
    n_scaler = getattr(SCALER, "n_features_in_", None)
    if n_scaler is not None and n_scaler != n_expected:
        raise RuntimeError(
            f"Incompatibilidade de features: scaler espera {n_scaler} colunas, "
            f"mas o alinhamento gerou {n_expected}. Verifique FEATURE_COLUMNS_PATH."
        )

    # Escala
    scaled = SCALER.transform(dummies.values)
    return scaled, expected_cols


# ------------------------------------------------------------------------------
# Rotas
# ------------------------------------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": os.path.exists(MODEL_PATH),
        "scaler_loaded": os.path.exists(SCALER_PATH),
        "feature_columns_source": (
            "model.feature_names_in_" if getattr(MODEL, "feature_names_in_", None) is not None else FEATURE_COLUMNS_PATH
        )
    }


@app.post("/predict", response_model=PredictResponse)
def predict(patient: Patient):
    warnings = []
    try:
        # Aviso se Thal vier mas o modelo não usar
        thal_used = False
        if patient.Thal is not None and getattr(MODEL, "feature_names_in_", None) is not None:
            thal_used = any(c.startswith("Thal_") or c == "Thal" for c in MODEL.feature_names_in_)
        if patient.Thal is not None and not thal_used:
            warnings.append("Campo 'Thal' recebido, mas não foi utilizado pelo modelo treinado.")

        df = pd.DataFrame([patient.dict()])
        x_scaled, cols = encode_align_scale(df)

        if hasattr(MODEL, "predict_proba"):
            proba = float(MODEL.predict_proba(x_scaled)[:, 1][0])
        else:
            raw = MODEL.decision_function(x_scaled)[0]
            proba = float(1 / (1 + np.exp(-raw)))

        pred = int(MODEL.predict(x_scaled)[0])
        label = "ALTO_RISCO" if pred == 1 else "BAIXO_RISCO"

        return {
            "prediction": pred,
            "label": label,
            "probability_positive": proba,
            "model_info": {
                "features_expected": cols,
                "model_class": type(MODEL).__name__,
            },
            "warnings": warnings,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class BatchRequest(BaseModel):
    items: List[Patient]


@app.post("/predict-batch")
def predict_batch(payload: BatchRequest):
    try:
        df = pd.DataFrame([p.dict() for p in payload.items])
        x_scaled, _ = encode_align_scale(df)
        preds = MODEL.predict(x_scaled).astype(int).tolist()
        if hasattr(MODEL, "predict_proba"):
            probas = MODEL.predict_proba(x_scaled)[:, 1].astype(float).tolist()
        else:
            raw = MODEL.decision_function(x_scaled)
            probas = (1 / (1 + np.exp(-raw))).astype(float).tolist()
        labels = ["ALTO_RISCO" if p == 1 else "BAIXO_RISCO" for p in preds]
        return {"predictions": preds, "labels": labels, "probabilities_positive": probas}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------------------------------------------------------------------
# Endpoint de debug para inspecionar o vetor alinhado/escalado
# ------------------------------------------------------------------------------
@app.post("/debug-vector")
def debug_vector(patient: Patient):
    try:
        df = pd.DataFrame([patient.dict()])
        x_scaled, cols = encode_align_scale(df)
        # Retorna apenas uma amostra (primeiros 12 valores) para não poluir
        sample = x_scaled[0][:min(12, x_scaled.shape[1])].tolist()
        return {
            "n_features": len(cols),
            "cols_sample": cols[:min(12, len(cols))],
            "vector_sample": sample,
            "feature_columns_source": (
                "model.feature_names_in_" if getattr(MODEL, "feature_names_in_", None) is not None else FEATURE_COLUMNS_PATH
            )
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
