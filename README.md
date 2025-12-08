# 🌌 AstroClassifier — Classificador Fotométrico de Objetos Astronômicos

Rede neural supervisionada para a classificação de objetos astronômicos em **GALAXY**, **STAR** e **QSO**, utilizando dados fotométricos do **SDSS-DR16** combinados com observações do **WISE**.

---

## 📚 Sobre o Projeto

A distinção entre estrelas, galáxias e quasares a partir apenas de magnitudes fotométricas é um dos principais desafios em Astronomia Observacional devido:

- À enorme quantidade de dados coletados por surveys
- A limitações instrumentais e efeitos de redshift
- A baixa separação entre classes em algumas bandas

Este projeto utiliza **aprendizado profundo** para auxiliar nesta tarefa, com um modelo implementado em **PyTorch**, capaz de aprender relações não lineares entre magnitudes multibanda.

---

## 🧠 Arquitetura do Modelo

- Rede Neural Multicamadas (MLP)
- Função de perda: **Cross-Entropy**
- Otimizador: **Adam**
- Normalização das features com **StandardScaler**
- Dropout para reduzir overfitting
- Treinamento supervisionado com partição **train/test**

---

## 🛰️ Dados Utilizados

| Catálogo | Bandas / Recursos | Finalidade |
|---------|------------------|------------|
| **SDSS-DR16** | u, g, r, i, z (fotometria PSF) | Base da classificação |
| **WISE** | W1–W4 (infravermelho) | Melhor separação entre galáxias e QSOs |

Critérios de qualidade:
- `zWarning = 0` → apenas espectros confiáveis usados como verdade de terreno
- Cruzamento das fontes pelo `objID`

---

## 📊 Resultados

- **Acurácia no conjunto de teste:** ~ **93%**
- Matriz de confusão indica boa separação entre as três classes
- ROC-AUC próximo de **1.0**
- Curva de perda estável e baixo overfitting

> Os resultados estão alinhados com trabalhos recentes de classificação fotométrica utilizando aprendizado profundo.

📌 Gráficos e métricas completos disponíveis em:  
`/results/`

---

## 🗂 Estrutura Recomendada do Projeto

AstroClassifier/
│
├── data/ # Exemplo de dataset de entrada
├── notebooks/ # Notebooks de análise e experimentos
├── src/ # Código-fonte do modelo
│ ├── model.py
│ ├── train.py
│ └── utils.py
├── results/ # Gráficos, métricas e tabelas
├── requirements.txt # Dependências do projeto
└── README.md # Este arquivo


---

## ▶️ Como Executar

```bash
# Clonar o repositório
git clone https://github.com/VanessaMartiins/AstroClassifier.git
cd AstroClassifier

# Instalar dependências
pip install -r requirements.txt

# Treinar o modelo
python src/train.py

🛠 Tecnologias

Python

PyTorch

Pandas, NumPy, Matplotlib, Seaborn

Scikit-Learn

Jupyter Notebook

👩‍🚀 Autora

Vanessa Gomes Martins da Silva
Estudante de Física Computacional — UFF
📧 Contato: vanemartiins@gmail.com
🔗 Portfólio: https://vanessamartins.github.io
