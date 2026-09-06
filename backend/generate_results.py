import os

import joblib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    auc,
)
from sklearn.preprocessing import label_binarize


MODEL_DIR = "model"
OUTPUT_DIR = "Resultados"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("Carregando dados da execução...")

    encoder = joblib.load(
        os.path.join(MODEL_DIR, "encoder.pkl")
    )

    y_test = np.load(
        os.path.join(MODEL_DIR, "y_test.npy")
    )

    predictions = np.load(
        os.path.join(MODEL_DIR, "predictions.npy")
    )

    probabilities = np.load(
        os.path.join(MODEL_DIR, "probabilities.npy")
    )

    train_losses = np.load(
        os.path.join(MODEL_DIR, "train_losses.npy")
    )

    classes = encoder.classes_

    print("Classes:", classes.tolist())
    print("Amostras de teste:", len(y_test))

    # =====================================================
    # 1. RELATÓRIO DE CLASSIFICAÇÃO
    # =====================================================

    report = classification_report(
        y_test,
        predictions,
        target_names=classes,
        digits=4,
    )

    report_path = os.path.join(
        OUTPUT_DIR,
        "relatorio_classificacao.txt",
    )

    with open(
        report_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(report)

    print(
        "Relatório salvo em:",
        report_path,
    )

    # =====================================================
    # 2. MATRIZ DE CONFUSÃO
    # =====================================================

    cm = confusion_matrix(
        y_test,
        predictions,
    )

    fig, ax = plt.subplots(
        figsize=(7, 6)
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=classes,
    )

    display.plot(
        cmap="Blues",
        ax=ax,
        colorbar=False,
    )

    ax.set_title(
        "Matriz de Confusão"
    )

    fig.tight_layout()

    confusion_path = os.path.join(
        OUTPUT_DIR,
        "matriz_confusao.png",
    )

    fig.savefig(
        confusion_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        "Matriz de confusão salva em:",
        confusion_path,
    )

    # =====================================================
    # 3. DISTRIBUIÇÃO DE CONFIANÇA
    # =====================================================

    confidences = np.max(
        probabilities,
        axis=1,
    )

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    ax.hist(
        confidences,
        bins=30,
        alpha=0.75,
    )

    ax.set_title(
        "Distribuição das probabilidades de previsão"
    )

    ax.set_xlabel(
        "Probabilidade máxima prevista"
    )

    ax.set_ylabel(
        "Número de amostras"
    )

    ax.grid(
        True,
        alpha=0.25,
    )

    fig.tight_layout()

    confidence_path = os.path.join(
        OUTPUT_DIR,
        "distribuicao_confianca.png",
    )

    fig.savefig(
        confidence_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        "Distribuição de confiança salva em:",
        confidence_path,
    )

    # =====================================================
    # 4. CURVA DE LOSS
    # =====================================================

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    epochs = np.arange(
        1,
        len(train_losses) + 1,
    )

    ax.plot(
        epochs,
        train_losses,
        marker="o",
    )

    ax.set_title(
        "Evolução da Loss durante o Treinamento"
    )

    ax.set_xlabel(
        "Época"
    )

    ax.set_ylabel(
        "Loss"
    )

    ax.grid(
        True,
        alpha=0.25,
    )

    fig.tight_layout()

    loss_path = os.path.join(
        OUTPUT_DIR,
        "curva_loss.png",
    )

    fig.savefig(
        loss_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        "Curva de loss salva em:",
        loss_path,
    )

    # =====================================================
    # 5. CURVAS ROC E AUC
    # =====================================================

    y_test_bin = label_binarize(
        y_test,
        classes=range(len(classes)),
    )

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    auc_values = {}

    for index, class_name in enumerate(classes):
        fpr, tpr, _ = roc_curve(
            y_test_bin[:, index],
            probabilities[:, index],
        )

        roc_auc = auc(
            fpr,
            tpr,
        )

        auc_values[class_name] = roc_auc

        ax.plot(
            fpr,
            tpr,
            linewidth=2,
            label=f"{class_name} (AUC = {roc_auc:.3f})",
        )

    ax.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        linewidth=1,
    )

    ax.set_xlabel(
        "Taxa de Falsos Positivos (FPR)"
    )

    ax.set_ylabel(
        "Taxa de Verdadeiros Positivos (TPR)"
    )

    ax.set_title(
        "Curvas ROC por Classe"
    )

    ax.legend(
        loc="lower right"
    )

    ax.grid(
        True,
        alpha=0.25,
    )

    fig.tight_layout()

    roc_path = os.path.join(
        OUTPUT_DIR,
        "curvas_ROC.png",
    )

    fig.savefig(
        roc_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        "Curvas ROC salvas em:",
        roc_path,
    )

    # =====================================================
    # 6. RESUMO DAS MÉTRICAS
    # =====================================================

    accuracy = (
        predictions == y_test
    ).mean()

    summary_path = os.path.join(
        OUTPUT_DIR,
        "metricas_resumo.txt",
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            f"Acurácia: {accuracy * 100:.2f}%\n"
        )

        file.write(
            f"Amostras de teste: {len(y_test)}\n"
        )

        file.write(
            f"Classes: {', '.join(classes)}\n"
        )

        file.write("\nAUC por classe:\n")

        for class_name, auc_value in auc_values.items():
            file.write(
                f"{class_name}: {auc_value:.4f}\n"
            )

        file.write(
            "\nMatriz de confusão:\n"
        )

        file.write(
            np.array2string(cm)
        )

    print(
        "Resumo das métricas salvo em:",
        summary_path,
    )

    # =====================================================
    # FINAL
    # =====================================================

    print("\nResultados gerados com sucesso.")
    print(
        f"Acurácia desta execução: "
        f"{accuracy * 100:.2f}%"
    )

    print("\nAUC por classe:")

    for class_name, auc_value in auc_values.items():
        print(
            f"{class_name}: {auc_value:.4f}"
        )

    print("\nMatriz de confusão:")
    print(cm)


if __name__ == "__main__":
    main()