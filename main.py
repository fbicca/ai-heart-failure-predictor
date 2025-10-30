import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib # Para salvar o modelo

# Carregar dataset
df = pd.read_csv("heart.csv")

# 1. Verificar valores ausentes
print(df.isnull().sum())

# 2. Transformar variáveis categóricas em numéricas
df_encoded = pd.get_dummies(df, drop_first=True)

# 3. Separar features e target
X = df_encoded.drop("HeartDisease", axis=1)
y = df_encoded["HeartDisease"]

# 4. Dividir em treino e teste (70% treino, 30% teste)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 5. Escalonar variáveis numéricas (opcional, mas recomendado)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Dados prontos para o modelo!")
print("Shape treino:", X_train.shape, "Shape teste:", X_test.shape)

# Salvar os dados em CSV
pd.DataFrame(X_train_scaled, columns=X_train.columns).to_csv("X_train.csv", index=False)
pd.DataFrame(X_test_scaled, columns=X_test.columns).to_csv("X_test.csv", index=False)
y_train.to_csv("y_train.csv", index=False)
y_test.to_csv("y_test.csv", index=False)

print("Arquivos CSV criados: X_train.csv, X_test.csv, y_train.csv, y_test.csv")

# 1️⃣ Carregar os dados já separados e escalonados
X_train_scaled = pd.read_csv("X_train.csv")
X_test_scaled = pd.read_csv("X_test.csv")
y_train = pd.read_csv("y_train.csv").squeeze()  # transforma DataFrame em Series
y_test = pd.read_csv("y_test.csv").squeeze()

# Escolher um modelo (Ex: Regressão Logística, bom ponto de partida)
model = LogisticRegression(random_state=42, solver='liblinear') 

# Treinar o modelo usando os dados escalonados
model.fit(X_train_scaled, y_train)

# Fazer previsões no conjunto de teste
y_pred = model.predict(X_test_scaled)

# Avaliar o desempenho (Métricas importantes para classificação de saúde)
print("\nAvaliação do Modelo:")
print(f"Acurácia: {accuracy_score(y_test, y_pred):.4f}")
print("\nRelatório de Classificação (Precision, Recall, F1-Score):")
print(classification_report(y_test, y_pred))

# *IMPORTANTE*: Se a classe "insuficiência cardíaca" for a classe positiva (1), 
# foque em 'Recall' (sensibilidade) para minimizar falsos negativos (FN).

# Salvar o modelo e o scaler
joblib.dump(model, 'modelo_insuficiencia_cardiaca.pkl')
joblib.dump(scaler, 'scaler_dados.pkl')

print("\nModelo e Scaler salvos com sucesso!")