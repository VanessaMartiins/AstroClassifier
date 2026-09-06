const listEl = document.querySelector("[data-object-list]");
const detailEl = document.querySelector("[data-object-detail]");

const labels = {
  STAR: "Estrela",
  GALAXY: "Galáxia",
  QSO: "Quasar"
};

async function loadExamples() {
  const response = await fetch("data/exemplos.json");

  if (!response.ok) {
    throw new Error("Não foi possível carregar os exemplos.");
  }

  return response.json();
}

function formatValue(value) {
  return Number.isInteger(value)
    ? value
    : Number(value)
        .toFixed(4)
        .replace(/0+$/, "")
        .replace(/\.$/, "");
}

function renderDataGrid(dados) {
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

function renderObject(obj) {
  detailEl.innerHTML = `
    <div class="card">
      <div class="card-body">

        <p class="eyebrow">Exemplo fotométrico</p>

        <h2>${obj.nome}</h2>

        <p class="muted">
          Esta visualização apresenta algumas características fotométricas de
          forma simplificada. Magnitudes menores correspondem a maior brilho
          naquela banda.
        </p>

        <div class="section">
          <div class="data-grid">
            ${renderDataGrid(obj.dados)}
          </div>
        </div>

        <div class="prediction">
          <div>

            <span class="class-badge">
              ${obj.classePrevista} — ${labels[obj.classePrevista]}
            </span>

            <h3 style="margin-top: 16px;">
              Como interpretar este exemplo?
            </h3>

            <p class="muted">
              ${obj.explicacao}
            </p>

            <p class="muted" style="margin-top: 12px;">
              Esta explicação é didática e foi preparada para ajudar a
              interpretar o padrão apresentado. Ela não é gerada pela rede
              neural.
            </p>

          </div>

          <div
            class="confidence"
            aria-label="Confiança ilustrativa"
            title="Valor ilustrativo usado nesta demonstração"
          >
            ${obj.confianca}%
          </div>
        </div>

        <p class="muted" style="margin-top: 16px;">
          <strong>Confiança ilustrativa:</strong>
          o percentual exibido nesta demonstração é pré-definido e não
          corresponde a uma inferência executada em tempo real.
        </p>

      </div>
    </div>
  `;
}

function renderList(examples) {
  listEl.innerHTML = examples
    .map(
      (obj, index) => `
        <button
          class="object-button ${index === 0 ? "active" : ""}"
          type="button"
          data-id="${obj.id}"
        >
          ${obj.nome}

          <span>
            Classe didática: ${labels[obj.classePrevista]} · ${obj.confianca}%
          </span>
        </button>
      `
    )
    .join("");

  listEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-id]");

    if (!button) return;

    listEl
      .querySelectorAll(".object-button")
      .forEach((item) => item.classList.remove("active"));

    button.classList.add("active");

    const selectedObject = examples.find(
      (obj) => obj.id === button.dataset.id
    );

    if (selectedObject) {
      renderObject(selectedObject);
    }
  });

  renderObject(examples[0]);
}

if (listEl && detailEl) {
  loadExamples()
    .then(renderList)
    .catch((error) => {
      detailEl.innerHTML = `
        <div class="card">
          <div class="card-body">
            <h2>Exemplos indisponíveis</h2>

            <p class="muted">
              ${error.message}
            </p>
          </div>
        </div>
      `;
    });
}