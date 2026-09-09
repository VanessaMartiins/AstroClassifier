# 🌌 AstroClassifier

**Classificação de objetos astronômicos com Redes Neurais**

O AstroClassifier é um projeto desenvolvido como Trabalho de Conclusão de Curso em **Física Computacional na Universidade Federal Fluminense (UFF)**.

O projeto utiliza uma rede neural para classificar objetos astronômicos entre **GALAXY**, **STAR** e **QSO (quasar)** a partir de características obtidas nos levantamentos astronômicos **SDSS DR16** e **WISE**.

🔭 **Acesse o projeto:**  
https://astroclassifier.com.br

---

## ✨ Sobre o projeto

Grandes levantamentos astronômicos observam milhões de objetos e produzem enormes volumes de dados.

O AstroClassifier investiga como técnicas de **Machine Learning**, especialmente redes neurais artificiais, podem ser utilizadas para reconhecer padrões nesses dados e auxiliar na classificação de estrelas, galáxias e quasares.

Além do desenvolvimento e avaliação do modelo, o projeto ganhou uma aplicação web voltada à **divulgação científica e apresentação interativa da pesquisa**.

No site é possível:

- entender como dados astronômicos são utilizados pelo modelo;
- explorar exemplos de objetos;
- participar de um quiz de classificação;
- conhecer a arquitetura da rede neural;
- visualizar métricas e resultados do treinamento;
- entender as principais características utilizadas pelo modelo.

> Os exemplos interativos apresentados no site são didáticos e não executam a rede neural em tempo real.

---

## 🛰️ Dados utilizados

O conjunto de dados foi construído utilizando informações do **Sloan Digital Sky Survey (SDSS DR16)** e do **Wide-field Infrared Survey Explorer (WISE)**.

O modelo final utiliza **20 características**:

### SDSS

15 magnitudes distribuídas entre:

- `modelMag_u`, `modelMag_g`, `modelMag_r`, `modelMag_i`, `modelMag_z`
- `cmodelMag_u`, `cmodelMag_g`, `cmodelMag_r`, `cmodelMag_i`, `cmodelMag_z`
- `psfMag_u`, `psfMag_g`, `psfMag_r`, `psfMag_i`, `psfMag_z`

### WISE

4 magnitudes no infravermelho:

- `W1`
- `W2`
- `W3`
- `W4`

### Redshift

- `z`

As classes utilizadas são provenientes das classificações espectroscópicas disponíveis no SDSS.

---

## 🧠 Arquitetura da Rede Neural

O modelo foi desenvolvido em **PyTorch** utilizando uma rede neural do tipo **Multilayer Perceptron (MLP)**.

Arquitetura:

```text
20 características de entrada
        ↓
64 neurônios
ReLU + Dropout (0.3)
        ↓
64 neurônios
ReLU + Dropout (0.3)
        ↓
3 classes
GALAXY | STAR | QSO
```

Configuração do treinamento:

- **Função de perda:** CrossEntropyLoss
- **Otimizador:** Adam
- **Learning rate:** 0.001
- **Normalização:** StandardScaler
- **Batch size:** 64
- **Épocas:** 20

---

## 📊 Resultados

O conjunto utilizado na versão final possui **10.000 objetos astronômicos**, divididos em:

- **8.000 objetos** para treinamento
- **2.000 objetos** para teste

### Desempenho

**Acurácia no conjunto de teste: 90,20%**

ROC-AUC por classe:

| Classe | AUC |
|---|---:|
| GALAXY | 0.961 |
| QSO | 0.994 |
| STAR | 0.957 |

Matriz de confusão:

```text
              Previsto
            GALAXY  QSO  STAR

GALAXY       1308    11    61
QSO            22   193     2
STAR           94     6   303
```

A principal confusão observada ocorreu entre **estrelas e galáxias**, enquanto os quasares apresentaram elevada capacidade de separação.

A análise de importância das características também mostrou forte contribuição das bandas infravermelhas **W1 e W2**, além do **redshift**.

Os gráficos e análises completas podem ser explorados na página **Resultados** do site.

---

## 🌐 Aplicação Web

A interface atual do AstroClassifier foi desenvolvida como uma experiência interativa para apresentar a pesquisa de forma mais acessível.

### Tecnologias

- HTML5
- CSS3
- JavaScript
- Firebase Hosting

A aplicação inclui:

- páginas explicativas sobre Astronomia e Machine Learning;
- exemplos interativos;
- quiz de classificação;
- visualização dos resultados;
- explicação da arquitetura da rede neural;
- formulário de contato.

---

## 🛠️ Tecnologias do projeto

### Machine Learning e análise de dados

- Python
- PyTorch
- Scikit-learn
- Pandas
- NumPy

### Dados astronômicos

- SDSS DR16
- WISE
- SciServer / CasJobs
- Astroquery

### Aplicação Web

- HTML5
- CSS3
- JavaScript
- Firebase Hosting

---

## 📁 Estrutura do projeto

A estrutura do repositório reúne os códigos utilizados durante o desenvolvimento da pesquisa, treinamento e avaliação do modelo, além da aplicação web atual.

```text
AstroClassifier/
│
├── data/
├── notebooks/
├── results/
├── front-end/
└── README.md
```

> A estrutura pode conter arquivos adicionais relacionados às diferentes etapas de desenvolvimento do projeto.

---

## 🎓 Contexto acadêmico

Projeto desenvolvido como **Trabalho de Conclusão de Curso em Física Computacional na Universidade Federal Fluminense (UFF)**.

O AstroClassifier surgiu como uma investigação sobre a aplicação de **redes neurais à classificação de objetos astronômicos** e posteriormente foi expandido para uma plataforma web interativa de divulgação e apresentação dos resultados.

---

## 👩‍🚀 Autora

**Vanessa Gomes Martins da Silva**  
Física Computacional — Universidade Federal Fluminense (UFF)

📧 vanemartiins@gmail.com

🌐 Portfólio:  
https://vanessamartins.github.io

💻 GitHub:  
https://github.com/VanessaMartiins

---

## 🔭 AstroClassifier

https://astroclassifier.com.br

**Transformando dados do Universo através da Inteligência Artificial.**
