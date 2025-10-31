from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
from dotenv import load_dotenv
import os, io, re, random, tempfile, subprocess
import requests
from validation import *
from anamnese import *
from datetime import datetime

# ------------------------- Inicialização -------------------------
load_dotenv()

# -------- Flask --------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "alura")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB uploads
app.config["JSON_AS_ASCII"] = False      # JSON UTF-8 (sem \u00e9)

# Persistência simples em memória
db_memory = {}

# Configurar CORS
CORS(app, 
     origins=["http://localhost:5000", "http://127.0.0.1:5000"], 
     supports_credentials=True,
     allow_headers=["Content-Type"],
     methods=["GET", "POST", "OPTIONS"])

# ------------------------- Integração com API de Predição -------------------------
API_PREDICT_URL = os.getenv("API_PREDICT_URL", "http://localhost:8000/predict")

def _build_api_payload(session):
    """Monta o payload esperado pela API a partir dos valores normalizados já salvos na sessão."""
    # Mapeia campos coletados pelo bot -> API
    # Garantir tipos numéricos básicos onde aplicável
    def to_int(x):
        try: return int(x)
        except: return None
    def to_float(x):
        try: return float(str(x).replace(",", "."))
        except: return None

    payload = {
        "Age": to_int(db_memory["idade"]),
        "Sex": db_memory["sexo"],
        "ChestPainType": db_memory["chestpain_type"],
        "RestingBP": to_float(db_memory["restingbp"]),
        "Cholesterol": to_int(db_memory["cholesterol"]),
        "FastingBS": 1 if db_memory["fastingbs"] in (1, "1", True, "sim") else 0,
        "RestingECG": db_memory["restingecg"],
        "MaxHR": to_int(db_memory["maxhr"]),
        # Exang pode ser 1/0 -> API aceita Exang ou ExerciseAngina ('Y'/'N'); enviaremos Exang
        "Exang": 1 if db_memory["exang"] in (1, "1", True, "sim") else 0,
        "Oldpeak": to_float(db_memory["oldpeak"]),
        "ST_Slope": db_memory["st_slope"]
    }
    return payload

def _call_predict_api(payload: dict):
    try:
        resp = requests.post(API_PREDICT_URL, json=payload, timeout=10)
        resp.raise_for_status()
        return True, resp.json()
    except Exception as e:
        return False, f"Falha ao chamar a API em {API_PREDICT_URL}: {e}"


def gerar_explicacao(payload: dict, label: str) -> str:
    """
    Gera uma explicação legível com base nos valores coletados e na classe prevista.
    Não altera nenhum outro comportamento do app.
    """
    try:
        idade  = payload.get("Age") or 0
        hr     = payload.get("MaxHR") or 0
        slope  = (payload.get("ST_Slope") or "").lower()
        chest  = (payload.get("ChestPainType") or "").lower()
        fbs    = payload.get("FastingBS")
        ecg    = (payload.get("RestingECG") or "").lower()
        oldpk  = payload.get("Oldpeak") or 0.0
        exang  = payload.get("Exang")

        motivos = []
        if label == "ALTO_RISCO":
            if isinstance(idade, (int, float)) and idade >= 55: motivos.append("idade avançada")
            if isinstance(hr, (int, float)) and hr < 100: motivos.append("HR baixo (<100)")
            if fbs == 1: motivos.append("jejum alterado")
            if "flat" in slope: motivos.append("ST plano")
            if "down" in slope: motivos.append("ST descendente")
            if "asy" in chest: motivos.append("assintomático")
            if "lvh" in ecg: motivos.append("ECG com hipertrofia")
            if exang in (1, "1", True, "sim"): motivos.append("esforço com angina")
            try:
                if float(oldpk) >= 2.0: motivos.append("oldpeak alto")
            except Exception:
                pass
            texto = ", ".join(motivos) or "características semelhantes às observadas em pacientes com doença cardíaca"
            return "\n➡️ Explicação:\n" + texto + " → o modelo tende a classificar como alto risco.\n\n"
        else:
            if isinstance(idade, (int, float)) and idade < 50: motivos.append("idade jovem")
            if isinstance(hr, (int, float)) and hr > 140: motivos.append("HR elevado (>140)")
            if fbs == 0: motivos.append("jejum normal")
            if "up" in slope: motivos.append("ST ascendente")
            if ("ata" in chest) or ("nap" in chest): motivos.append("dor anginosa atípica/não anginosa")
            if "normal" in ecg: motivos.append("ECG normal")
            if exang in (0, "0", False, "não", "nao"): motivos.append("sem angina ao esforço")
            try:
                if float(oldpk) <= 0.2: motivos.append("oldpeak baixo")
            except Exception:
                pass
            texto = ", ".join(motivos) or "padrão compatível com baixo risco de doença cardíaca"
            return "\n➡️ Explicação:\n" + texto + " → o modelo tende a classificar como baixo risco.\n\n"
    except Exception as e:
        return f"\n➡️ Explicação automática não gerada ({e}).\n\n"



# ------------------------- Lógica do Chatbot -------------------------

# saudação
def greet_and_menu():
    
    return {
        "msg": (
                " Olá! Seja bem-vindo(a) à avaliação de risco cardiovascular.\n\n"
                "Este assistente ajudará você a estimar, de forma simples e segura, o seu risco de doenças cardíacas com base em alguns dados clínicos.\n\n"
                "Podemos começar agora?\n"
                " Responda “sim” para iniciar ou “não” para sair."
        ),
        "type_conversation": "await_service"
    }



###########################################################################################
# árvore do chatbot
###########################################################################################
@app.post("/chat")
def chat():

    data = request.get_json(silent=True) or {}
    user_msg = (data.get("msg") or "").strip()
    type_conversation = data.get("type_conversation")

    print(f"Chatbot - user_msg: {user_msg}")
    print(f"Chatbot - type_conversation: {type_conversation}")

    if user_msg.startswith("<") or "</" in user_msg:
        user_msg = ""

    #captura digitação do usuário
    low = user_msg.lower()

    # return start
    if low in {"menu", "inicio", "início", "recomeçar"}:
        print("reset state #2")
        return greet_and_menu()
    
    # inicia coleta informações do estado clínico da paciente
    if type_conversation == "await_service":
        if low in {"sim", "vamos", "ok"}:
            return {
                "msg": "Perfeito!\nAgora, por favor, informe a idade do paciente (em anos completos).",
                "type_conversation": "await_age"
            }
        elif low in {"não", "negativo"}:
            return {
                "msg": "✅ Entendido!\nO atendimento foi encerrado.\n\n💬 Agradecemos seu tempo e confiança. Cuide bem do seu coração! ❤️\n\nAté logo!",
                "type_conversation": "await_service"
            }
        else:
            return {
                "msg": "Opa! 😅\nEsse tipo de solicitação não pode ser feita aqui.\n\n"
                "Podemos iniciar sua avaliação de risco cardiovascular agora?\n\n"
                "👉 Responda “sim” para começar ou “não” para sair.",
                "type_conversation": "await_service"
            }
           
    # Idade: idade do paciente [anos]
    if type_conversation == "await_age":
        print("await_age - processando idade")
        resultado = valida_idade(low)
        if resultado is True:
            db_memory["idade"] = int(low)
            return {
                "msg": f"Perfeito! 👏\nA idade registrada é {db_memory["idade"]} anos.\n\nAgora, por favor, informe o sexo do paciente (Masculino ou Feminino).",
                "type_conversation": "await_sex"
            }
        else:
            return (f"{resultado}")

    # Sexo: sexo do paciente [M: Masculino, F: Feminino]
    if type_conversation == "await_sex":
        ok, resultado = valida_sexo(low)

        if ok:
            db_memory["sexo"] = resultado
            return {
                "msg": f"Entendido! 👍\nSexo registrado: {'Masculino' if resultado == 'M' else 'Feminino'}.\n\n"
                    "Agora, por favor, informe se o paciente sente dor no peito. Se sim, escolha a opção que melhor descreve o tipo de dor:\n\n"
                    "💔 TA: Angina típica (dor típica de esforço)\n"
                    "💓 ATA: Angina atípica (dor atípica)\n"
                    "❤️ NAP: Dor não anginosa (não relacionada ao coração)\n"
                    "🚫 ASY: Assintomática (sem dor no peito)",
                "type_conversation": "await_chestpain"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_sex"
            }


    # ChestPainType: tipo de dor no peito [TA: Angina típica, ATA: Angina atípica, NAP: Dor não anginosa, ASY: Assintomática]
    if type_conversation == "await_chestpain":
        ok, resultado = valida_dor_no_peito(low)

        if ok:
            db_memory["chestpain_type"] = resultado
            return {
                "msg": f"Entendido! 👍\n Dor no peito registrada: {resultado}.\n\n"
                "Agora, por favor, informe a pressão arterial em repouso (em mmHg).",
                "type_conversation": "await_restingbp"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_chestpain"
            }
        

    # RestingBP: pressão arterial em repouso [mm Hg]
    if type_conversation == "await_restingbp":
        resultado = valida_pressao(low)

        if resultado is True:
            db_memory["restingbp"] = int(low)
            return {
                "msg": f"Perfeito! 🙌\nPressão registrada: {db_memory['restingbp']} mmHg.\n\nAgora, por favor, informe o **nível de colesterol total** (em **mg/dL**).",
                "type_conversation": "await_cholesterol"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_restingbp"
            }


    # Colesterol: colesterol sérico [mm/dl
    if type_conversation == "await_cholesterol":
        resultado = valida_colesterol(low)

        if resultado is True:
            db_memory["cholesterol"] = int(low)
            return {
                "msg": f"Ótimo! 🙌 \nColesterol registrado: {db_memory['cholesterol']} mg/dL.\n\n"
                "Agora, por favor, informe se o paciente estava em jejum (FastingBS).\n👉 Responda 'sim' ou 'não'.",
                "type_conversation": "await_fastingbs"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_cholesterol"
            }


    # FastingBS: glicemia em jejum [1: se FastingBS > 120 mg/dl, 0: caso contrário]
    if type_conversation == "await_fastingbs":
        ok, resultado = valida_jejum(low)

        if ok:
            db_memory["fastingbs"] = resultado
            return {
                "msg": f"Entendido! 👍\nPaciente {'estava' if resultado == 1 else 'não estava'} em jejum.\n\n"
                    "Agora, por favor, informe o resultado do eletrocardiograma em repouso (RestingECG).\n\n"

                    "As opções são:\n"
                    "🩺 Normal\n"
                    "⚡ ST-T wave abnormality\n"
                    "❤️ LVH Left ventricular hypertrophy",
                "type_conversation": "await_ecg"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_fastingbs"
            }
        
    # RestingECG: resultados do eletrocardiograma em repouso [Normal: Normal, ST: com anormalidade da onda ST-T (inversões da onda T e/ou elevação ou depressão do segmento ST de > 0,05 mV), HVE: mostrando hipertrofia ventricular esquerda provável ou definitiva pelos critérios de Estes]
    if type_conversation == "await_ecg":
        ok, resultado = valida_ecg(low)

        if ok:
            db_memory["restingecg"] = resultado
            return {
                "msg": f"Perfeito! 💓\nResultado do ECG: {db_memory['restingecg']}.\n\n"
                    "Agora, por favor, informe a frequência cardíaca máxima atingida (MaxHR), em batimentos por minuto (bpm).",
                "type_conversation": "await_maxhr"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_ecg"
            }
        
    # MaxHR: frequência cardíaca máxima atingida [Valor numérico entre 60 e 202]
    if type_conversation == "await_maxhr":
        ok, resultado = valida_maxhr(low)

        if ok:
            db_memory["maxhr"] = resultado
            return {
                    "msg": f"Excelente! 🩺\nFrequência cardíaca máxima: {db_memory['maxhr']} bpm.\n\n"
                        "Agora, por favor, informe se o paciente apresentou angina induzida por exercício (Exang).\n👉 Responda 'sim' ou 'não'.",
                    "type_conversation": "await_exang"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_maxhr"
            }
        
    # ExerciseAngina: angina induzida por exercício [S: Sim, N: Não]
    if type_conversation == "await_exang":
        ok, resultado = valida_exang(low)

        if ok:
            db_memory["exang"] = resultado
            return {
                        "msg": f"Entendido 👍\nO paciente {'APRESENTOU' if resultado == 1 else 'NÃO APRESENTOU'} Angina Induzida durante o exercício.\n\n"
                    "Agora, por favor, informe o valor da depressão do segmento ST (Oldpeak), em relação ao repouso.\n"
                    "👉 Informe um número entre 0.0 e 10.0\n",
                        "type_conversation": "await_oldpeak"
                }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_exang"
            }

    # Oldpeak: oldpeak = ST [Valor numérico medido em depressão]
    if type_conversation == "await_oldpeak":
        ok, resultado = valida_oldpeak(low)

        if ok:
            db_memory["oldpeak"] = resultado
            return {
                "msg": f"Perfeito 👍\nValor de Oldpeak registrado: {db_memory['oldpeak']} mV.\n\n"
                "Agora, por favor, informe a inclinação do segmento ST (Slope):\n"
                "📈 Up → crescente\n"
                "➖ Flat → plano\n"
                "📉 Down → decrescente",
                "type_conversation": "await_slope"
            }
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_oldpeak"
            }

    # ST_Slope: a inclinação do segmento ST de pico do exercício [Up: inclinação ascendente, Flat: plano, Down: inclinação descendente]
    # Finaliza a coleta de heart_disease:
    if type_conversation == "await_slope":
        ok, resultado = valida_slope(low)

        if ok:
            db_memory["st_slope"] = resultado
            return montar_resumo(db_memory)
        else:
            return { 
                "msg": f"{resultado}",
                "type_conversation": "await_slope"
            }

    # Confirmação final: 'sim' envia para a API; 'não' reinicia
    if type_conversation == "confirm_summary":
        if low in {"sim", "confirmo", "ok"}:
            payload = _build_api_payload(db_memory)
            ok_api, result = _call_predict_api(payload)
            if ok_api:
                # Formatar retorno amigável
                pred = result.get("prediction")
                label = result.get("label")
                prob = result.get("probability_positive")
                warnings = result.get("warnings") or []
#                linhas = [
#                    "🔮 *Resultado da Predição*",
#                    f"- Classe: {label} ({pred})",
#                    f"- Probabilidade de classe positiva: {prob:.2%}" if isinstance(prob, (int,float)) else f"- Probabilidade: {prob}",
#                ]

                linhas = [
                       "🔮 *Resultado da Predição*",
                    ]

                # Mapeia a classe para o texto com emoji
                if str(label).strip().upper() in ["ALTO_RISCO", "ALTO RISCO", "1"]:
                    linhas.append("- Classe: 🔴 ALTO RISCO CARDÍACO")
                else:
                    linhas.append("- Classe: 🟢 BAIXO RISCO CARDÍACO")

                linhas.append(
                    f"- Probabilidade de classe positiva: {prob:.2%}"
                    if isinstance(prob, (int, float))
                    else f"- Probabilidade: {prob}"
                )
                if warnings:
                    linhas.append("\n⚠️ Avisos:\n " + "; ".join(warnings))
                linhas.append(gerar_explicacao(payload, label))
                linhas.append("Digite 'sim' para iniciar novo atendimento ou 'não' para encerrar.")
                return {
                        "msg": "\n".join(linhas),
                        "type_conversation": "await_service"
                }
            else:
                # erro ao chamar API
                return {
                    "msg": f"❌ {result}\n\nDigite 'sim' para tentar novamente ou 'não' para encerrar.",
                    "type_conversation": "await_service"
                }
        elif low in {"não", "nao"}:
            return greet_and_menu()
        else:
            return {
                    "msg": "Por favor, responda 'sim' para confirmar e enviar à API, ou 'não' para recomeçar.",
            }


# ------------------------- Home -------------------------
@app.get("/")
def home():
    try:
        db_memory["state"] = "await_service"
        return render_template("index.html")
    except Exception:
        return "BotHealth backend ativo."

# ------------------------- Main -------------------------
if __name__ == "__main__":
    print("[BotHealth] iniciado.")
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))