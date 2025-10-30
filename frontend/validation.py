# Validação idade
def valida_idade(var_idade):
    try:
        idade = int(var_idade)
        if idade <= 0:
            return "Ops! 😅\n❌ Essa idade não parece válida.\n\nPor favor, informe uma idade válida (deve ser maior que 0 e em anos completos)."
        elif idade > 120:
            return "Ops! 😅\n❌ Essa idade parece fora do padrão esperado.\n\nPor favor, confirme a idade do paciente (deve estar entre 1 e 120 anos)."
        return True
    except (ValueError, TypeError):
        return "Ops! 😅\n❌ Essa idade não parece válida.\n\nPor favor, informe uma idade válida (deve ser maior que 0 e em anos completos)."

# Validação do sexo    
def valida_sexo(resposta):
    if not resposta:
        return False, "🩺 Por favor, informe o sexo do paciente:\n👉 Masculino ou Feminino."
    
    low = resposta.strip().lower()

    if low in {"m", "masculino"}:
        return True, "M"
    elif low in {"f", "feminino"}:
        return True, "F"
    else:
        return False, "Ops! 😅\n❌ Não entendi essa resposta.\n\nPor favor, digite 'M' para Masculino ou 'F' para Feminino."
    
# Validação dor no peito
def valida_dor_no_peito(resposta):
    if not resposta:
        return False, ("😊 Tudo bem!\n\n💬 Por favor, selecione uma das opções abaixo:\n\n"
            "💔 TA – Angina típica (dor típica de esforço)\n"
            "💓 ATA – Angina atípica (dor incomum)\n"
            "❤️ NAP – Dor não anginosa (não relacionada ao coração)\n"
            "🚫 ASY – Assintomática (sem dor no peito)")

    low = resposta.strip().lower()

    if low in {"ta", "típica", "tipica", "angina típica", "angina tipica"}:
        return True, "TA"
    elif low in {"ata", "atípica", "atipica", "angina atípica", "angina atipica"}:
        return True, "ATA"
    elif low in {"nap", "dor não anginosa", "dor nao anginosa"}:
        return True, "NAP"
    elif low in {"asy", "assintomático", "assintomatica", "assintomático", "sem dor"}:
        return True, "ASY"
    else:
        return False, (
            "Ops! 😅\n❌ Essa resposta não é válida.\n\n"
            "Por favor, escolha uma das opções válidas:\n\n"
            "💔 TA – Angina típica\n"
            "💓 ATA – Angina atípica\n"
            "❤️ NAP – Dor não anginosa\n"
            "🚫 ASY – Assintomática"
        )
    
# Validação pressao
def valida_pressao(var_pressao):
    try:
        valor = int(var_pressao)
        if valor < 70:
            return (
                "Ops! 😅\n⚠️ Pressão muito baixa!\n\n"
                "Por favor, verifique se o valor informado está correto (o mínimo permitido é **70 mmHg**)."
            )
        elif valor > 250:
            return (
                "Ops! 😅\n⚠️ Pressão muito alta!\n\n"
                "Por favor, verifique se o valor informado está correto (o máximo permitido é **250 mmHg**)."
            )
        return True
    except (ValueError, TypeError):
        return (
            "Ops! 😅\n❌ Essa resposta não é válida.\n\n"
            "A pressão arterial deve ser um **número inteiro**, em milímetros de mercúrio (**mmHg**)."
        )
# Validação colesterol
def valida_colesterol(valor):
    try:
        col = int(valor)
        if col <= 0:
            return ( "Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                     "O colesterol deve ser maior que 0 mg/dL.")
        elif col < 100:
            return "Ops! 😅\n⚠️ Colesterol muito baixo!\n\nPor favor, verifique se o valor informado está correto (o mínimo permitido é **100 mg/dL.**)."
        elif col > 600:
            return "Ops! 😅\n⚠️ Colesterol muito alto!\n\nPor favor, verifique se o valor informado está correto (o máximo permitido é **600 mg/dL.**"
        return True
    except (ValueError, TypeError):
        return ("Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                "O valor de colesterol deve ser informado como um número inteiro, em mg/dL.")
    
# Validação jejum
def valida_jejum(resposta):
    if not resposta:
        return ("Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                "Por favor, informe se o paciente estava em jejum (FastingBS).\n👉 Responda 'sim' ou 'não'.")

    low = resposta.strip().lower()

    if low in {"sim", "s", "yes", "y"}:
        return True, 1  # jejum positivo (glicemia em jejum)
    elif low in {"não", "nao", "n", "no"}:
        return True, 0  # não estava em jejum
    else:
        return False, ("Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                "Por favor, informe se o paciente estava em jejum (FastingBS).\n👉 Responda 'sim' ou 'não'.")

    
# validação eletro cardiograma
def valida_ecg(resposta):
    if not resposta:
        return False, (
            "Por favor, informe o resultado do eletrocardiograma em repouso (RestingECG).\n\n"
            "As opções são:\n"
            "🩺 Normal\n"
            "⚡ ST-T wave abnormality\n"
            "❤️ LVH Left ventricular hypertrophy")
  
    low = resposta.strip().lower()

    if low in {"normal"}:
        return True, "Normal"
    elif low in {"st-t", "st-t wave", "st-t wave abnormality", "anormalidade st-t"}:
        return True, "ST-T wave abnormality"
    elif low in {"lvh", "left ventricular hypertrophy", "hipertrofia ventricular esquerda"}:
        return True, "Left ventricular hypertrophy"
    else:
       return False, ("Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                "Por favor, informe o resultado do eletrocardiograma em repouso (RestingECG).\n\n"
                "As opções são:\n"
                "🩺 Normal\n"
                "⚡ ST-T wave abnormality\n"
                "❤️ LVH Left ventricular hypertrophy")
    
# valida frequencia cardiaca
def valida_maxhr(resposta):
    """Valida a frequência cardíaca máxima (bpm)."""
    try:
        valor = int(resposta)
        if 40 <= valor <= 250:
            return True, valor
        else:
            return False, (
                "Ops! 😅\n⚠️ Valor fora do intervalo esperado."
                "Por favor, informe a frequência cardíaca máxima atingida (MaxHR), em batimentos por minuto (bpm), entre 40 e 250 bpm."
            )
    except (ValueError, TypeError):
        return False, (
            "Ops! 😅\n⚠️ Valor fora do intervalo esperado.\n\nPor favor, informe um número inteiro, representando a frequência cardíaca máxima atingida (MaxHR), em batimentos por minuto (bpm), entre 40 e 250 bpm."
        )
    

def valida_exang(resposta):
    """Valida a presença de angina induzida por exercício."""
    if not resposta:
        return False, (
                "Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                "Por favor, informe se o paciente apresentou angina induzida por exercício (Exang).\n👉 Responda 'sim' ou 'não'."
            )

    low = resposta.strip().lower()

    if low in {"sim", "s", "yes", "y"}:
        return True, 1   # 1 = apresentou angina
    elif low in {"nao", "não", "n", "no"}:
        return True, 0   # 0 = não apresentou
    else:
        return False, (
                "Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                "Por favor, informe se o paciente apresentou angina induzida por exercício (Exang).\n👉 Responda 'sim' ou 'não'."
            )


def valida_oldpeak(resposta):
    """Valida o valor de Oldpeak (depressão do segmento ST em mV)."""
    if not resposta:
        return (False, "Por favor, informe o valor da depressão do segmento ST (Oldpeak), em relação ao repouso.\n"
                "💡 Exemplo: 1.4 (Informe um número entre 0.0 e 10.0)")

    try:
        valor = float(resposta.replace(",", "."))  # aceita vírgula ou ponto
        if 0.0 <= valor <= 10.0:
            return True, valor
        else:
            return False, (
                "Ops! 😅\n⚠️ Valor fora do intervalo esperado."
                "Por favor, informe o valor da depressão do segmento ST (Oldpeak), em relação ao repouso.\n"
                "👉 Informe um número entre 0.0 e 10.0\n"
            )
    except ValueError:
        return False, (
                "Ops! 😅\n⚠️ Valor fora do intervalo esperado."
                "Por favor, informe o valor da depressão do segmento ST (Oldpeak), em relação ao repouso.\n"
                "👉 Informe um número entre 0.0 e 10.0\n"
        )
   

def valida_slope(resposta):
    """Valida a inclinação do segmento ST (ST_Slope)."""
    if not resposta:
        return False, (
                "Por favor, informe a inclinação do segmento ST (Slope):\n"
                "📈 Up → crescente\n"
                "➖ Flat → plano\n"
                "📉 Down → decrescente"
        )

    low = resposta.strip().lower()

    if low in {"up", "ascendente", "crescente"}:
        return True, "Up"
    elif low in {"flat", "plano", "reta"}:
        return True, "Flat"
    elif low in {"down", "descendente", "decrescente"}:
        return True, "Down"
    else:
        return False, (
                "Ops! 😅\n❌ Essa resposta não é válida.\n\n"
                "Por favor, informe a inclinação do segmento ST (Slope):\n"
                "📈 Up → crescente\n"
                "➖ Flat → plano\n"
                "📉 Down → decrescente"
            )


def valida_thal(resposta):
    """Valida o resultado do exame de tálio (Thal)."""
    if not resposta:
        return False, (
                    "Por favor, informe o resultado do exame de tálio (Thal):\n"
                    "🟢 Normal\n"
                    "🟠 Fixed defect (defeito fixo)\n"
                    "🔵 Reversible defect (defeito reversível)"
        )

    low = resposta.strip().lower()

    if low in {"normal"}:
        return True, "Normal"

    if low in {
        "fixed defect", "fixed", "defeito fixo", "defeito permanente", "fixo"
    }:
        return True, "Fixed defect"

    if low in {
        "reversible defect", "reversible", "reversivel", "defeito reversivel", "defeito reversível"
    }:
        return True, "Reversible defect"

    return False, (
            "Ops! 😅\n❌ Essa resposta não é válida.\n\n"
            "Por favor, informe o resultado do exame de tálio (Thal):\n"
            "🟢 Normal\n"
            "🟠 Fixed defect (defeito fixo)\n"
            "🔵 Reversible defect (defeito reversível)"
    )

