def _fmt_bool01(v):
    if v in (1, "1", True, "sim"):  return "Sim"
    if v in (0, "0", False, "não", "nao"): return "Não"
    return "—"

def _fmt_or(v, default="—"):
    return default if v in (None, "", []) else str(v)

def _fmt_chestpain(v):
    mapa = {"TA": "TA (Angina típica)", "ATA": "ATA (Angina atípica)",
            "NAP": "NAP (Dor não anginosa)", "ASY": "ASY (Assintomática)"}
    return mapa.get(v, _fmt_or(v))

def _fmt_ecg(v):
    mapa = {"Normal": "Normal", "ST": "ST-T wave abnormality",
            "HVE": "Left ventricular hypertrophy"}
    return mapa.get(v, _fmt_or(v))

def _fmt_slope(v):
    mapa = {"Up": "Up (ascendente)", "Flat": "Flat (plano)", "Down": "Down (descendente)"}
    return mapa.get(v, _fmt_or(v))


def montar_resumo(session):
    linhas = [
        "✅ Resumo dos dados informados\n",
        f"👤 Idade: {_fmt_or(session.get('idade'))}",
        f"🚻 Sexo: {_fmt_or('Masculino' if session.get('sexo') == 'M' else ('Feminino' if session.get('sexo') == 'F' else '—'))}",
        f"❤️ Dor no Peito (ChestPainType): {_fmt_chestpain(session.get('chestpain_type'))}",
        f"🩺 Pressão arterial (mmHg - RestingBP): {_fmt_or(session.get('restingbp'))}",
        f"🧬 Colesterol (mg/dL): {_fmt_or(session.get('cholesterol'))}",
        f"🍽️ Jejum (FastingBS): {_fmt_bool01(session.get('fastingbs'))}",
        f"⚡ ECG em repouso (RestingECG): {_fmt_ecg(session.get('restingecg'))}",
        f"💓 Frequência cardíaca máxima (bpm - MaxHR): {_fmt_or(session.get('maxhr'))}",
        f"💢 Angina durante exercício (Exang): {_fmt_bool01(session.get('exang'))}",
        f"📉 Oldpeak (mV): {_fmt_or(session.get('oldpeak'))}",
        f"📈 Inclinação do ST (ST_Slope): {_fmt_slope(session.get('st_slope'))}",
        "",
        "🔎 Confere?\n\n",
        "👉 Responda SIM para confirmar e enviar à API, ou NÃO para reiniciar o preenchimento.",
        ""
    ]
     
    return {
        "msg": "\n".join(linhas),
        "type_conversation": "confirm_summary"
    }