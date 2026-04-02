import os
import joblib
import torch
import torch.nn as nn
import torch.nn.functional as F
from flask import Flask, request, jsonify
from flask_cors import CORS


class AstroClassifier(nn.Module):
    def __init__(self, input_size=26, hidden_size=64, output_size=3):
        super(AstroClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        return self.out(x)


app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False
)

MODEL_DIR = "model"

checkpoint = torch.load(os.path.join(MODEL_DIR, "model.pth"), map_location="cpu")
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
encoder = joblib.load(os.path.join(MODEL_DIR, "encoder.pkl"))

FEATURES = checkpoint["features"]

model = AstroClassifier(
    input_size=checkpoint["input_size"],
    hidden_size=checkpoint["hidden_size"],
    output_size=checkpoint["output_size"]
)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()


def gerar_explicacao(classe_predita):
    if classe_predita.lower() == "star":
        return "O modelo identificou um padrão compatível com uma fonte pontual de luz."
    elif classe_predita.lower() == "galaxy":
        return "O modelo identificou características típicas de estruturas extensas."
    elif classe_predita.lower() == "qso":
        return "O modelo identificou padrões de objetos muito energéticos e distantes."
    return "Classificação realizada pelo modelo."

def normalizar_valor_numerico(valor, media_padrao):
    if valor is None:
        return float(media_padrao)

    texto = str(valor).strip()

    if texto == "":
        return float(media_padrao)

    texto = texto.replace(" ", "")

    # Se vier no formato brasileiro decimal
    if "," in texto:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return float(media_padrao)
    
@app.route("/")
def home():
    return "Backend do AstroClassifier está funcionando com o modelo real."


@app.route("/features", methods=["GET"])
def listar_features():
    return jsonify({"features": FEATURES})


@app.route("/classificar", methods=["POST"])
def classificar():
    dados = request.get_json()

    valores = []
    campos_preenchidos_com_media = []

    for i, col in enumerate(FEATURES):
        valor_original = dados.get(col, "")
        valor_convertido = normalizar_valor_numerico(valor_original, scaler.mean_[i])

        texto_original = str(valor_original).strip() if valor_original is not None else ""
        texto_teste = texto_original.replace(" ", "")
        if "," in texto_teste:
            texto_teste = texto_teste.replace(".", "")
            texto_teste = texto_teste.replace(",", ".")

        try:
            float(texto_teste)
        except:
            campos_preenchidos_com_media.append(col)

        if texto_original == "":
            if col not in campos_preenchidos_com_media:
                campos_preenchidos_com_media.append(col)

        valores.append(valor_convertido)

    x = scaler.transform([valores])
    x_tensor = torch.tensor(x, dtype=torch.float32)

    with torch.no_grad():
        logits = model(x_tensor)
        probs = torch.softmax(logits, dim=1).numpy()[0]

    classe_idx = probs.argmax()
    classe_predita = encoder.inverse_transform([classe_idx])[0]
    confianca = round(float(probs[classe_idx]) * 100, 2)

    mensagem_extra = ""
    if campos_preenchidos_com_media:
        mensagem_extra = (
            " Campos ausentes preenchidos automaticamente com a média do treinamento: "
            + ", ".join(campos_preenchidos_com_media) + "."
        )

    return jsonify({
        "classe": classe_predita,
        "confianca": confianca,
        "explicacao": gerar_explicacao(classe_predita) + mensagem_extra
    })

@app.route("/classificar_lote", methods=["POST"])
def classificar_lote():
    dados = request.get_json()
    linhas = dados.get("linhas", [])

    if not linhas:
        return jsonify({"erro": "Nenhuma linha recebida para teste em lote."}), 400

    classes_ordem = ["STAR", "GALAXY", "QSO"]

    matriz = {
        "STAR": {"STAR": 0, "GALAXY": 0, "QSO": 0},
        "GALAXY": {"STAR": 0, "GALAXY": 0, "QSO": 0},
        "QSO": {"STAR": 0, "GALAXY": 0, "QSO": 0}
    }

    total = 0
    acertos = 0
    erros = 0
    resultados = []

    for row in linhas:
        valores = []

        for i, col in enumerate(FEATURES):
            valor_convertido = normalizar_valor_numerico(row.get(col, ""), scaler.mean_[i])
            valores.append(valor_convertido)

        x = scaler.transform([valores])
        x_tensor = torch.tensor(x, dtype=torch.float32)

        with torch.no_grad():
            logits = model(x_tensor)
            probs = torch.softmax(logits, dim=1).numpy()[0]

        classe_idx = probs.argmax()
        classe_predita = encoder.inverse_transform([classe_idx])[0]

        classe_real = str(row.get("class", "")).strip().upper()
        classe_prevista = str(classe_predita).strip().upper()

        acertou = classe_real == classe_prevista if classe_real else False

        total += 1
        if acertou:
            acertos += 1
        else:
            erros += 1

        if classe_real in classes_ordem and classe_prevista in classes_ordem:
            matriz[classe_real][classe_prevista] += 1

        resultados.append({
            "classe_real": classe_real,
            "classe_prevista": classe_prevista,
            "acertou": acertou
        })

    acuracia = round((acertos / total) * 100, 2) if total > 0 else 0.0

    return jsonify({
        "total": total,
        "acertos": acertos,
        "erros": erros,
        "acuracia": acuracia,
        "resultados": resultados,
        "matriz_confusao": matriz
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)