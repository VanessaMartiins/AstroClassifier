#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AstroClassifier - Rede Neural para Classificação de Objetos Astronômicos
Autora: Vanessa Gomes Martins da Silva (UFF)
"""

import os
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, random_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, label_binarize
from sklearn.metrics import (
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
    roc_curve, auc
)
import matplotlib.pyplot as plt
import numpy as np

# =====================================================
# 0️⃣ Criar pasta de resultados
# =====================================================
output_dir = "Resultados"
os.makedirs(output_dir, exist_ok=True)

# =====================================================
# 1️⃣ Definição da Rede Neural
# =====================================================
class AstroClassifier(nn.Module):
    def __init__(self, input_size=25, hidden_size=64, output_size=3):
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

# =====================================================
# 2️⃣ Carregar e preparar os dados
# =====================================================
df = pd.read_csv("C:/Users/vanem/Downloads/SDSS_DR16_com_WISE.csv", sep=';', encoding='utf-8')
df.columns = df.columns.str.strip()

features = [
    'specObjID','ra','dec','mjd','plate','fiberID',
    'modelMag_u','modelMag_g','modelMag_r','modelMag_i','modelMag_z',
    'cmodelMag_u','cmodelMag_g','cmodelMag_r','cmodelMag_i','cmodelMag_z',
    'psfMag_u','psfMag_g','psfMag_r','psfMag_i','psfMag_z',
    'w1mpro','w2mpro','w3mpro','w4mpro','z'
]

for col in features:
    df[col] = df[col].astype(str)
    df[col] = df[col].str.replace('.', '', regex=False)
    df[col] = df[col].str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=features + ['class'])

X = df[features].values
y = df['class'].values

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

# =====================================================
# 3️⃣ Treinamento
# =====================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AstroClassifier(input_size=len(features), hidden_size=64, output_size=3).to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

epochs = 20
train_losses = []

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
    train_losses.append(avg_loss)
    print(f"Época {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")

# =====================================================
# 4️⃣ Avaliação
# =====================================================
model.eval()
correct, total = 0, 0
all_preds, all_labels = [], []
all_probs = []

with torch.no_grad():
    for batch_X, batch_y in test_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        outputs = model(batch_X)
        probs = torch.softmax(outputs, dim=1)
        _, predicted = torch.max(probs, 1)
        total += batch_y.size(0)
        correct += (predicted == batch_y).sum().item()
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(batch_y.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

accuracy = 100 * correct / total
print(f"\n✅ Acurácia no conjunto de teste: {accuracy:.2f}%")

# =====================================================
# 5️⃣ Relatório e Matriz de Confusão
# =====================================================
report = classification_report(all_labels, all_preds, target_names=encoder.classes_)
with open(os.path.join(output_dir, "relatorio_classificacao.txt"), "w", encoding="utf-8") as f:
    f.write(report)

print("\n📄 Relatório salvo em:", os.path.join(output_dir, "relatorio_classificacao.txt"))

cm = confusion_matrix(all_labels, all_preds)
ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=encoder.classes_).plot(cmap=plt.cm.Blues)
plt.title("Matriz de Confusão")
plt.savefig(os.path.join(output_dir, "matriz_confusao.png"), dpi=300, bbox_inches='tight')
plt.close()

# =====================================================
# 6️⃣ Distribuição das probabilidades de previsão
# =====================================================
confidences = np.max(np.array(all_probs), axis=1)
plt.figure(figsize=(8, 5))
plt.hist(confidences, bins=30, color='royalblue', alpha=0.7)
plt.title("Distribuição das probabilidades de previsão (confiança do modelo)")
plt.xlabel("Probabilidade máxima prevista")
plt.ylabel("Número de amostras")
plt.grid(True)
plt.savefig(os.path.join(output_dir, "distribuicao_confianca.png"), dpi=300, bbox_inches='tight')
plt.close()

# =====================================================
# 7️⃣ Curva de Loss
# =====================================================
plt.plot(train_losses)
plt.title("Evolução da Loss durante o Treinamento")
plt.xlabel("Épocas")
plt.ylabel("Loss")
plt.grid(True)
plt.savefig(os.path.join(output_dir, "curva_loss.png"), dpi=300, bbox_inches='tight')
plt.close()

# =====================================================
# 8️⃣ Importância das Características
# =====================================================
importances = np.zeros(len(features))

model.eval()
with torch.no_grad():
    baseline_pred = torch.softmax(model(X_tensor.to(device)), dim=1).cpu().detach().numpy()

for i, col in enumerate(features):
    X_temp = X_scaled.copy()
    np.random.shuffle(X_temp[:, i])
    X_temp_tensor = torch.tensor(X_temp, dtype=torch.float32).to(device)
    with torch.no_grad():
        perm_pred = torch.softmax(model(X_temp_tensor), dim=1).cpu().numpy()
    diff = np.mean(np.abs(baseline_pred - perm_pred))
    importances[i] = float(diff)

importances = importances / importances.sum()
sorted_idx = np.argsort(importances)[::-1]
sorted_features = [features[i] for i in sorted_idx]
sorted_importances = importances[sorted_idx]

plt.figure(figsize=(10, 6))
plt.barh(sorted_features[:15][::-1], sorted_importances[:15][::-1], color='skyblue')
plt.xlabel("Importância Relativa")
plt.title("Importância das Características na Classificação")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "importancia_caracteristicas.png"), dpi=300, bbox_inches='tight')
plt.close()

# =====================================================
# 9️⃣ Curvas ROC e AUC
# =====================================================
y_test_bin = label_binarize(all_labels, classes=range(len(encoder.classes_)))
probs = np.array(all_probs)
n_classes = y_test_bin.shape[1]

plt.figure(figsize=(8, 6))
for i in range(n_classes):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], probs[:, i])
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, lw=2, label=f"{encoder.classes_[i]} (AUC = {roc_auc:.3f})")

plt.plot([0, 1], [0, 1], 'k--', lw=1)
plt.xlabel("Taxa de Falsos Positivos (FPR)")
plt.ylabel("Taxa de Verdadeiros Positivos (TPR)")
plt.title("Curvas ROC por Classe")
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "curvas_ROC.png"), dpi=300, bbox_inches='tight')
plt.close()

# =====================================================
# 🔟 Salvar modelo e dados de teste
# =====================================================
torch.save(model.state_dict(), os.path.join(output_dir, "modelo_state_dict.pth"))
np.save(os.path.join(output_dir, "X_test.npy"), X_scaled[train_size:])
np.save(os.path.join(output_dir, "y_test.npy"), y_encoded[train_size:])
np.save(os.path.join(output_dir, "encoder_classes.npy"), encoder.classes_)

print("\n💾 Todos os resultados salvos com sucesso em:", os.path.abspath(output_dir))
