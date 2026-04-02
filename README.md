# 🌌 AstroClassifier — Classificador Fotométrico de Objetos Astronômicos

Aplicação completa (frontend + backend) para classificação automática de objetos astronômicos em **GALAXY**, **STAR** e **QSO**, utilizando Machine Learning com dados do **SDSS-DR16** + **WISE**.

---

## 🌐 Acesse o Projeto

🔗 Frontend: https://astroclassifier-frontend.onrender.com  
⚙️ API (Backend): https://astroclassifier.onrender.com  

---

## 📚 Sobre o Projeto

A distinção entre estrelas, galáxias e quasares a partir de magnitudes fotométricas é um desafio clássico da Astronomia Observacional devido a:

- Grande volume de dados  
- Sobreposição entre classes  
- Efeitos de redshift  

O **AstroClassifier** resolve esse problema utilizando uma rede neural capaz de aprender relações não lineares entre múltiplas bandas espectrais.

---

## 🖥️ Funcionalidades da Aplicação

A aplicação web permite:

- 🔹 Classificação manual de objetos  
- 🔹 Upload de arquivos CSV  
- 🔹 Dataset de demonstração integrado  
- 🔹 Avaliação em lote com cálculo de acurácia  
- 🔹 Matriz de confusão  
- 🔹 Visualização gráfica das previsões  

---

## 🧠 Arquitetura do Modelo

- Rede Neural Multicamadas (MLP)  
- Função de perda: **Cross-Entropy**  
- Otimizador: **Adam**  
- Normalização com **StandardScaler**  
- Dropout para regularização  

Implementado em **Python (PyTorch)**

---

## 🏗️ Arquitetura do Sistema
Frontend (HTML, CSS, JS)
↓
Fetch API
↓
Backend (Flask + PyTorch)
↓
Modelo treinado (.pth)



---

## 🛰️ Dados Utilizados

| Catálogo | Bandas / Recursos | Finalidade |
|---------|------------------|------------|
| **SDSS-DR16** | u, g, r, i, z (fotometria PSF) | Base da classificação |
| **WISE** | W1–W4 (infravermelho) | Melhor separação entre galáxias e QSOs |

Critérios:

- `zWarning = 0` → espectros confiáveis  
- Crossmatch entre catálogos  

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

## 🗂 Estrutura do Projeto
AstroClassifier/
│
├── backend/
│ ├── app.py
│ ├── model/
│ └── requirements.txt
│
├── frontend/
│ ├── index.html
│ ├── script.js
│ └── style.css
│
├── data/
├── results/
├── notebooks/
└── README.md

---

## ▶️ Como Executar

### 🔹 Backend

```markdown
git clone https://github.com/VanessaMartiins/AstroClassifier.git
cd AstroClassifier/backend
pip install -r requirements.txt
python app.py


🔹 Frontend

Abra:
frontend/index.html

☁️ Deploy
Backend hospedado no Render (Web Service)
Frontend hospedado no Render (Static Site)

🛠 Tecnologias
Python
PyTorch
Flask
Scikit-learn
Pandas, NumPy
JavaScript (Fetch API, Chart.js, PapaParse)
HTML5 + CSS3
Render

🎓 Contexto Acadêmico

Projeto desenvolvido como Trabalho de Conclusão de Curso (TCC) em Física Computacional — UFF.

👩‍🚀 Autora

Vanessa Gomes Martins da Silva
🎓 Física Computacional — UFF

📧 vanemartiins@gmail.com

🔗 https://vanessamartins.github.io

🔗 https://github.com/VanessaMartiins
