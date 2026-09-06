import os

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


MODEL_DIR = "model"
OUTPUT_DIR = "Resultados"
RANDOM_SEED = 42


class AstroClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
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


def calculate_accuracy(model, X, y, device):
    X_tensor = torch.tensor(
        X,
        dtype=torch.float32,
    ).to(device)

    y_tensor = torch.tensor(
        y,
        dtype=torch.long,
    ).to(device)

    model.eval()

    with torch.no_grad():
        outputs = model(X_tensor)

        predictions = torch.argmax(
            outputs,
            dim=1,
        )

    accuracy = (
        predictions == y_tensor
    ).float().mean().item()

    return accuracy


def main():
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    print("Carregando modelo e conjunto de teste...")

    checkpoint = torch.load(
        os.path.join(
            MODEL_DIR,
            "model.pth",
        ),
        map_location="cpu",
    )

    features = checkpoint["features"]

    X_test = np.load(
        os.path.join(
            MODEL_DIR,
            "X_test.npy",
        )
    )

    y_test = np.load(
        os.path.join(
            MODEL_DIR,
            "y_test.npy",
        )
    )

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    model = AstroClassifier(
        input_size=checkpoint["input_size"],
        hidden_size=checkpoint["hidden_size"],
        output_size=checkpoint["output_size"],
    ).to(device)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    baseline_accuracy = calculate_accuracy(
        model,
        X_test,
        y_test,
        device,
    )

    print(
        f"Acurácia original: "
        f"{baseline_accuracy * 100:.2f}%"
    )

    # =====================================================
    # PERMUTATION IMPORTANCE
    # =====================================================

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    importances = []

    for index, feature in enumerate(features):
        X_permuted = X_test.copy()

        X_permuted[:, index] = rng.permutation(
            X_permuted[:, index]
        )

        permuted_accuracy = calculate_accuracy(
            model,
            X_permuted,
            y_test,
            device,
        )

        importance = (
            baseline_accuracy
            - permuted_accuracy
        )

        importances.append(
            importance
        )

        print(
            f"{feature}: "
            f"queda de "
            f"{importance * 100:.2f} "
            f"p.p."
        )

    importances = np.asarray(
        importances
    )

    sorted_indices = np.argsort(
        importances
    )[::-1]

    top_n = min(
        15,
        len(features),
    )

    top_indices = sorted_indices[
        :top_n
    ]

    top_features = [
        features[index]
        for index in top_indices
    ]

    top_importances = (
        importances[top_indices]
        * 100
    )

    # =====================================================
    # GRÁFICO
    # =====================================================

    fig, ax = plt.subplots(
        figsize=(10, 7)
    )

    positions = np.arange(
        len(top_features)
    )

    ax.barh(
        positions,
        top_importances[::-1],
    )

    ax.set_yticks(
        positions
    )

    ax.set_yticklabels(
        top_features[::-1]
    )

    ax.set_xlabel(
        "Queda na acurácia após permutação "
        "(pontos percentuais)"
    )

    ax.set_title(
        "Impacto das Características "
        "na Classificação"
    )

    ax.grid(
        axis="x",
        alpha=0.25,
    )

    fig.tight_layout()

    output_path = os.path.join(
        OUTPUT_DIR,
        "importancia_caracteristicas.png",
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        "\nGráfico salvo em:",
        output_path,
    )


if __name__ == "__main__":
    main()