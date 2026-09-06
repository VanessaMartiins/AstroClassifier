const quizEl = document.querySelector("[data-quiz]");
const scoreEl = document.querySelector("[data-score]");
const progressEl = document.querySelector("[data-progress]");
const nextButton = document.querySelector("[data-next]");

let examples = [];
let current = 0;
let score = 0;
let locked = false;

const quizLabels = {
  STAR: "STAR — Estrela",
  GALAXY: "GALAXY — Galáxia",
  QSO: "QSO — Quasar"
};

async function getExamples() {
  const response = await fetch("data/exemplos.json");

  if (!response.ok) {
    throw new Error("Não foi possível carregar o quiz.");
  }

  return response.json();
}

function shuffle(items) {
  return [...items].sort(() => Math.random() - 0.5);
}

function formatValue(value) {
  return Number.isInteger(value)
    ? value
    : Number(value).toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
}

function dataGrid(dados) {
  return Object.entries(dados)
    .map(
      ([key, value]) => `
        <div class="data-point">
          <strong>${key}</strong>
          <span>${formatValue(value)}</span>
        </div>
      `
    )
    .join("");
}

function renderQuiz() {
  locked = false;

  const item = examples[current];

  progressEl.textContent = `Objeto ${current + 1} de ${examples.length}`;
  scoreEl.textContent = `Pontuação: ${score}`;
  nextButton.hidden = true;

  quizEl.innerHTML = `
    <div class="card">
      <div class="card-body">

        <p class="eyebrow">Desafio do observador</p>

        <h2>${item.nome}</h2>

        <p class="muted">
          Observe como as magnitudes variam entre as bandas e compare também
          o redshift. Tente identificar qual padrão parece mais compatível
          com uma estrela, uma galáxia ou um quasar.
        </p>

        <div class="section">
          <div class="data-grid">
            ${dataGrid(item.dados)}
          </div>
        </div>

        <div class="answer-grid">
          ${Object.keys(quizLabels)
            .map(
              (label) => `
                <button
                  class="answer-button"
                  type="button"
                  data-answer="${label}"
                >
                  ${quizLabels[label]}
                </button>
              `
            )
            .join("")}
        </div>

        <p class="feedback" data-feedback></p>

      </div>
    </div>
  `;
}

function answer(choice) {
  if (locked) return;

  locked = true;

  const item = examples[current];
  const buttons = quizEl.querySelectorAll("[data-answer]");
  const feedback = quizEl.querySelector("[data-feedback]");

  buttons.forEach((button) => {
    const value = button.dataset.answer;

    if (value === item.tipo) {
      button.classList.add("correct");
    }

    if (value === choice && value !== item.tipo) {
      button.classList.add("wrong");
    }

    button.disabled = true;
  });

  if (choice === item.tipo) {
    score += 1;

    feedback.textContent =
      `Acertou! ${item.explicacao}`;
  } else {
    feedback.textContent =
      `Quase. A resposta correta era ${quizLabels[item.tipo]}. ${item.explicacao}`;
  }

  scoreEl.textContent = `Pontuação: ${score}`;

  nextButton.hidden = false;
  nextButton.textContent =
    current === examples.length - 1
      ? "Ver resultado"
      : "Próximo objeto";
}

if (quizEl) {
  getExamples()
    .then((data) => {
      examples = shuffle(data);
      renderQuiz();
    })
    .catch((error) => {
      quizEl.innerHTML = `
        <div class="card">
          <div class="card-body">
            <h2>Quiz indisponível</h2>

            <p class="muted">
              ${error.message}
            </p>
          </div>
        </div>
      `;
    });

  quizEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-answer]");

    if (button) {
      answer(button.dataset.answer);
    }
  });
}

if (nextButton) {
  nextButton.addEventListener("click", () => {
    if (current < examples.length - 1) {
      current += 1;
      renderQuiz();
      return;
    }

    const percentage = Math.round((score / examples.length) * 100);

    let message = "";

    if (percentage === 100) {
      message =
        "Excelente! Você reconheceu corretamente todos os padrões apresentados.";
    } else if (percentage >= 70) {
      message =
        "Muito bom! Você conseguiu identificar a maior parte dos padrões apresentados.";
    } else if (percentage >= 40) {
      message =
        "Bom começo. Alguns padrões são bem sutis e ficam mais claros com a prática.";
    } else {
      message =
        "Esses padrões podem ser difíceis de identificar apenas olhando os números — e é justamente aí que técnicas de aprendizado de máquina podem ajudar.";
    }

    quizEl.innerHTML = `
      <div class="card">
        <div class="card-body">

          <p class="eyebrow">Resultado do quiz</p>

          <h2>${score} de ${examples.length}</h2>

          <p class="muted">
            ${message}
          </p>

          <p class="muted" style="margin-top: 12px;">
            Neste desafio, você analisou uma versão simplificada de algumas
            das características usadas na classificação. O modelo completo
            trabalha com um conjunto maior de variáveis para reconhecer
            padrões entre STAR, GALAXY e QSO.
          </p>

        </div>
      </div>
    `;

    nextButton.hidden = true;
    progressEl.textContent = "Quiz concluído";
    scoreEl.textContent = `Pontuação final: ${score}`;
  });
}