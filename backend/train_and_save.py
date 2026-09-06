import os
import random

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch.utils.data import DataLoader, TensorDataset


# =========================================================
# CONFIGURAÇÃO
# =========================================================

RANDOM_SEED = 42
TEST_RATIO = 0.20
BATCH_SIZE = 64
EPOCHS = 20
LEARNING_RATE = 0.001

CSV_PATH = r"C:\Users\vanem\Downloads\SDSS_DR16_com_WISE.csv"
OUTPUT_DIR = "model"


FEATURES = [
    "modelMag_u",
    "modelMag_g",
    "modelMag_r",
    "modelMag_i",
    "modelMag_z",
    "cmodelMag_u",
    "cmodelMag_g",
    "cmodelMag_r",
    "cmodelMag_i",
    "cmodelMag_z",
    "psfMag_u",
    "psfMag_g",
    "psfMag_r",
    "psfMag_i",
    "psfMag_z",
    "w1mpro",
    "w2mpro",
    "w3mpro",
    "w4mpro",
    "z",
]

# =========================================================
# REPRODUTIBILIDADE
# =========================================================

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# =========================================================
# MODELO
# =========================================================

class AstroClassifier(nn.Module):
    def __init__(self, input_size=26, hidden_size=64, output_size=3):
        super().__init__()

        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        return self.out(x)


# =========================================================
# LIMPEZA NUMÉRICA
# =========================================================

def clean_numeric_column(series: pd.Series) -> pd.Series:
    series = series.astype(str).str.strip()

    # Remove espaços.
    series = series.str.replace(" ", "", regex=False)

    # Mantém apenas caracteres numéricos relevantes.
    series = series.str.replace(
        r"[^\d,.\-eE+]",
        "",
        regex=True,
    )

    # Se houver vírgula, assume formato decimal brasileiro.
    if series.str.contains(",", regex=False).any():
        series = series.str.replace(".", "", regex=False)
        series = series.str.replace(",", ".", regex=False)

    return pd.to_numeric(series, errors="coerce")


# =========================================================
# MAIN
# =========================================================

def main():
    set_seed(RANDOM_SEED)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Lendo CSV...")

    df = pd.read_csv(
        CSV_PATH,
        sep=";",
        encoding="utf-8",
    )

    df.columns = df.columns.str.strip()

    print("\nShape original:", df.shape)

    missing_cols = [
        col
        for col in FEATURES + ["class"]
        if col not in df.columns
    ]

    if missing_cols:
        raise ValueError(
            f"Colunas ausentes no CSV: {missing_cols}"
        )

    print("\nLimpando colunas numéricas...")

    for col in FEATURES:
        df[col] = clean_numeric_column(df[col])

    # Mantém apenas linhas com classe válida.
    df = df.dropna(subset=["class"]).copy()

    # Remove linhas em que TODAS as features estejam vazias.
    df = df.dropna(
        subset=FEATURES,
        how="all",
    ).copy()

    if df.empty:
        raise ValueError(
            "O DataFrame ficou vazio após a limpeza."
        )

    print("\nQuantidade de objetos válidos:", len(df))

    # =====================================================
    # LABELS
    # =====================================================

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(df["class"].values)

    X = df[FEATURES].to_numpy(dtype=np.float64)

    # =====================================================
    # SPLIT REPRODUZÍVEL
    # =====================================================

    indices = np.arange(len(X))

    rng = np.random.default_rng(RANDOM_SEED)
    rng.shuffle(indices)

    test_size = int(len(indices) * TEST_RATIO)

    test_indices = indices[:test_size]
    train_indices = indices[test_size:]

    X_train_raw = X[train_indices]
    X_test_raw = X[test_indices]

    y_train = y_encoded[train_indices]
    y_test = y_encoded[test_indices]

    print("\nObjetos de treino:", len(X_train_raw))
    print("Objetos de teste:", len(X_test_raw))

    # =====================================================
    # IMPUTAÇÃO SEM LEAKAGE
    # =====================================================

    train_means = np.nanmean(
        X_train_raw,
        axis=0,
    )

    # Caso alguma coluna seja inteiramente NaN no treino.
    train_means = np.where(
        np.isnan(train_means),
        0.0,
        train_means,
    )

    X_train_filled = np.where(
        np.isnan(X_train_raw),
        train_means,
        X_train_raw,
    )

    X_test_filled = np.where(
        np.isnan(X_test_raw),
        train_means,
        X_test_raw,
    )

    # =====================================================
    # STANDARD SCALER SEM LEAKAGE
    # =====================================================

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train_filled
    )

    X_test_scaled = scaler.transform(
        X_test_filled
    )

    # =====================================================
    # TENSORES
    # =====================================================

    X_train_tensor = torch.tensor(
        X_train_scaled,
        dtype=torch.float32,
    )

    y_train_tensor = torch.tensor(
        y_train,
        dtype=torch.long,
    )

    X_test_tensor = torch.tensor(
        X_test_scaled,
        dtype=torch.float32,
    )

    y_test_tensor = torch.tensor(
        y_test,
        dtype=torch.long,
    )

    train_dataset = TensorDataset(
        X_train_tensor,
        y_train_tensor,
    )

    test_dataset = TensorDataset(
        X_test_tensor,
        y_test_tensor,
    )

    train_generator = torch.Generator()
    train_generator.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=train_generator,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    # =====================================================
    # MODELO
    # =====================================================

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print("\nDevice usado:", device)

    model = AstroClassifier(
        input_size=len(FEATURES),
        hidden_size=64,
        output_size=len(encoder.classes_),
    ).to(device)

    loss_fn = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    # =====================================================
    # TREINAMENTO
    # =====================================================

    print("\nIniciando treinamento...")

    train_losses = []

    for epoch in range(EPOCHS):
        model.train()

        running_loss = 0.0

        for batch_X, batch_y in train_loader:
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()

            outputs = model(batch_X)
            loss = loss_fn(outputs, batch_y)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_loss = (
            running_loss / len(train_loader)
        )

        train_losses.append(avg_loss)

        print(
            f"Época {epoch + 1}/{EPOCHS}"
            f" - Loss: {avg_loss:.4f}"
        )

    # =====================================================
    # AVALIAÇÃO
    # =====================================================

    print("\nAvaliando modelo...")

    model.eval()

    correct = 0
    total = 0

    all_preds = []
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            outputs = model(batch_X)

            probs = torch.softmax(
                outputs,
                dim=1,
            )

            predicted = torch.argmax(
                probs,
                dim=1,
            )

            total += batch_y.size(0)

            correct += (
                predicted == batch_y
            ).sum().item()

            all_preds.extend(
                predicted.cpu().numpy()
            )

            all_probs.extend(
                probs.cpu().numpy()
            )

            all_labels.extend(
                batch_y.cpu().numpy()
            )

    accuracy = 100 * correct / total

    print(
        "\nAcurácia no conjunto de teste:"
        f" {accuracy:.2f}%"
    )

    # =====================================================
    # SALVAR MODELO
    # =====================================================

    model_path = os.path.join(
        OUTPUT_DIR,
        "model.pth",
    )

    scaler_path = os.path.join(
        OUTPUT_DIR,
        "scaler.pkl",
    )

    encoder_path = os.path.join(
        OUTPUT_DIR,
        "encoder.pkl",
    )

    imputer_path = os.path.join(
        OUTPUT_DIR,
        "feature_means.npy",
    )

    torch.save(
        {
            "model_state_dict":
                model.state_dict(),
            "input_size":
                len(FEATURES),
            "hidden_size":
                64,
            "output_size":
                len(encoder.classes_),
            "features":
                FEATURES,
            "random_seed":
                RANDOM_SEED,
        },
        model_path,
    )

    joblib.dump(
        scaler,
        scaler_path,
    )

    joblib.dump(
        encoder,
        encoder_path,
    )

    np.save(
        imputer_path,
        train_means,
    )

    # =====================================================
    # SALVAR DADOS DA EXECUÇÃO
    # =====================================================

    np.save(
        os.path.join(
            OUTPUT_DIR,
            "X_test.npy",
        ),
        X_test_scaled,
    )

    np.save(
        os.path.join(
            OUTPUT_DIR,
            "y_test.npy",
        ),
        y_test,
    )

    np.save(
        os.path.join(
            OUTPUT_DIR,
            "predictions.npy",
        ),
        np.asarray(all_preds),
    )

    np.save(
        os.path.join(
            OUTPUT_DIR,
            "probabilities.npy",
        ),
        np.asarray(all_probs),
    )

    np.save(
        os.path.join(
            OUTPUT_DIR,
            "train_losses.npy",
        ),
        np.asarray(train_losses),
    )

    np.save(
        os.path.join(
            OUTPUT_DIR,
            "test_indices.npy",
        ),
        test_indices,
    )

    print("\nArquivos salvos com sucesso:")
    print("Modelo:", model_path)
    print("Scaler:", scaler_path)
    print("Encoder:", encoder_path)
    print("Médias das features:", imputer_path)

    print(
        "\nClasses:",
        encoder.classes_.tolist(),
    )


if __name__ == "__main__":
    main()