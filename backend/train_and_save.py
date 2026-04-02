import os
import joblib
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, random_split
from sklearn.preprocessing import StandardScaler, LabelEncoder


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


FEATURES = [
    'specObjID', 'ra', 'dec', 'mjd', 'plate', 'fiberID',
    'modelMag_u', 'modelMag_g', 'modelMag_r', 'modelMag_i', 'modelMag_z',
    'cmodelMag_u', 'cmodelMag_g', 'cmodelMag_r', 'cmodelMag_i', 'cmodelMag_z',
    'psfMag_u', 'psfMag_g', 'psfMag_r', 'psfMag_i', 'psfMag_z',
    'w1mpro', 'w2mpro', 'w3mpro', 'w4mpro', 'z'
]


def clean_numeric_column(series: pd.Series) -> pd.Series:
    series = series.astype(str).str.strip()
    series = series.str.replace(" ", "", regex=False)
    series = series.str.replace(r"[^\d,.\-eE+]", "", regex=True)

    if series.str.contains(",", regex=False).any():
        series = series.str.replace(".", "", regex=False)
        series = series.str.replace(",", ".", regex=False)

    return pd.to_numeric(series, errors="coerce")


def main():
    csv_path = r"C:\Users\vanem\Downloads\SDSS_DR16_com_WISE.csv"
    output_dir = "model"
    os.makedirs(output_dir, exist_ok=True)

    print("Lendo CSV...")
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    df.columns = df.columns.str.strip()

    print("\nShape original:", df.shape)
    print("\nColunas lidas:")
    print(df.columns.tolist())

    print("\nPrimeiras 5 linhas:")
    print(df.head())

    missing_cols = [col for col in FEATURES + ['class'] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas ausentes no CSV: {missing_cols}")

    print("\nLimpando colunas numéricas...")
    for col in FEATURES:
        df[col] = clean_numeric_column(df[col])

    print("\nAmostra das features após limpeza:")
    print(df[FEATURES].head())

    print("\nQuantidade de NaN por coluna nas features:")
    print(df[FEATURES].isna().sum())

    print("\nQuantidade de NaN na coluna class:")
    print(df['class'].isna().sum())

    print("\nQuantidade de linhas antes do tratamento de NaN:", len(df))

    # Mantém apenas linhas com classe válida
    df = df.dropna(subset=['class'])

    # Preenche NaN das features com a média da coluna
    df[FEATURES] = df[FEATURES].fillna(df[FEATURES].mean(numeric_only=True))

    print("Quantidade de linhas depois do tratamento de NaN:", len(df))

    if df.empty:
        raise ValueError(
            "O DataFrame ficou vazio após o tratamento. "
            "Verifique o separador do CSV e o formato numérico das colunas."
        )

    X = df[FEATURES].values
    y = df['class'].values

    print("\nShape de X:", X.shape)
    print("Quantidade de rótulos em y:", len(y))
    print("Classes encontradas:", pd.Series(y).value_counts())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
    y_tensor = torch.tensor(y_encoded, dtype=torch.long)

    dataset = TensorDataset(X_tensor, y_tensor)
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_ds, test_ds = random_split(dataset, [train_size, test_size])

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=64)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("\nDevice usado:", device)

    model = AstroClassifier(
        input_size=len(FEATURES),
        hidden_size=64,
        output_size=len(encoder.classes_)
    ).to(device)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    epochs = 20
    print("\nIniciando treinamento...")

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = loss_fn(outputs, batch_y)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_loss = running_loss / len(train_loader)
        print(f"Época {epoch + 1}/{epochs} - Loss: {avg_loss:.4f}")

    print("\nAvaliando modelo...")
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            predicted = torch.argmax(outputs, dim=1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

    accuracy = 100 * correct / total
    print(f"Acurácia no conjunto de teste: {accuracy:.2f}%")

    model_path = os.path.join(output_dir, "model.pth")
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    encoder_path = os.path.join(output_dir, "encoder.pkl")

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "input_size": len(FEATURES),
            "hidden_size": 64,
            "output_size": len(encoder.classes_),
            "features": FEATURES
        },
        model_path
    )

    joblib.dump(scaler, scaler_path)
    joblib.dump(encoder, encoder_path)

    print("\nArquivos salvos com sucesso:")
    print(f"Modelo: {model_path}")
    print(f"Scaler: {scaler_path}")
    print(f"Encoder: {encoder_path}")


if __name__ == "__main__":
    main()