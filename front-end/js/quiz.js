const quizEl = document.querySelector("[data-quiz]");
const scoreEl = document.querySelector("[data-score]");
const progressEl = document.querySelector("[data-progress]");
const nextButton = document.querySelector("[data-next]");

let examples = [];
let current = 0;
let score = 0;
let locked = false;

const quizLabels = {
  STAR: "STAR",
  GALAXY: "GALAXY",
  QSO: "QSO"
};

async function getExamples() {
  const response = await fetch("data/exemplos.json");
  if (!response.ok) {
    throw new Error("Nao foi possivel carregar o quiz.");
  }
  return response.json();
}

function shuffle(items) {
  return [...items].sort(() => Math.random() - 0.5);
}

function dataGrid(dados) {
  return Object.entries(dados)
    .map(([key, value]) => `
      <div class="data-point">
        <strong>${key}</strong>
        <span>${value}</span>
      </div>
    `)
    .join("");
}

function renderQuiz() {
  locked = false;
  const item = examples[current];
  progressEl.textContent = `Objeto ${current + 1} de ${examples.length}`;
  scoreEl.textContent = `Pontuacao: ${score}`;
  nextButton.hidden = true;

  quizEl.innerHTML = `
    <div class="card">
      <div class="card-body">
        <p class="eyebrow">Desafio do observador</p>
        <h2>${item.nome}</h2>
        <p class="muted">Analise os dados abaixo e escolha a classe mais provavel. Dica: redshift quase zero costuma favorecer STAR; redshift alto pode indicar QSO; galaxias ficam no meio com cores mais avermelhadas.</p>
        <div class="section">
          <div class="data-grid">${dataGrid(item.dados)}</div>
        </div>
        <div class="answer-grid">
          ${Object.keys(quizLabels).map((label) => `<button class="answer-button" type="button" data-answer="${label}">${label}</button>`).join("")}
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
    if (value === item.tipo) button.classList.add("correct");
    if (value === choice && value !== item.tipo) button.classList.add("wrong");
  });

  if (choice === item.tipo) {
    score += 1;
    feedback.textContent = `Acertou. ${item.explicacao}`;
  } else {
    feedback.textContent = `Quase. A resposta era ${item.tipo}. ${item.explicacao}`;
  }

  scoreEl.textContent = `Pontuacao: ${score}`;
  nextButton.hidden = false;
  nextButton.textContent = current === examples.length - 1 ? "Ver resultado" : "Proximo objeto";
}

if (quizEl) {
  getExamples()
    .then((data) => {
      examples = shuffle(data);
      renderQuiz();
    })
    .catch((error) => {
      quizEl.innerHTML = `<div class="card"><div class="card-body"><h2>Quiz indisponivel</h2><p class="muted">${error.message} Abra a pagina por um servidor local para permitir o carregamento do JSON.</p></div></div>`;
    });

  quizEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-answer]");
    if (button) answer(button.dataset.answer);
  });
}

if (nextButton) {
  nextButton.addEventListener("click", () => {
    if (current < examples.length - 1) {
      current += 1;
      renderQuiz();
      return;
    }

    quizEl.innerHTML = `
      <div class="card">
        <div class="card-body">
          <p class="eyebrow">Resultado do quiz</p>
          <h2>${score} de ${examples.length}</h2>
          <p class="muted">Voce comparou cores, brilho e redshift como o modelo faz em escala muito maior. O objetivo nao e decorar: e perceber que dados numericos tambem contam historias sobre o ceu.</p>
        </div>
      </div>
    `;
    nextButton.hidden = true;
    progressEl.textContent = "Quiz concluido";
  });
}
