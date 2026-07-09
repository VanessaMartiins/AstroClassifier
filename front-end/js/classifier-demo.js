const listEl = document.querySelector("[data-object-list]");
const detailEl = document.querySelector("[data-object-detail]");

const labels = {
  STAR: "Estrela",
  GALAXY: "Galaxia",
  QSO: "Quasar"
};

async function loadExamples() {
  const response = await fetch("data/exemplos.json");
  if (!response.ok) {
    throw new Error("Nao foi possivel carregar os exemplos.");
  }
  return response.json();
}

function formatValue(value) {
  return Number.isInteger(value) ? value : Number(value).toFixed(4).replace(/0+$/, "").replace(/\.$/, "");
}

function renderDataGrid(dados) {
  return Object.entries(dados)
    .map(([key, value]) => `
      <div class="data-point">
        <strong>${key}</strong>
        <span>${formatValue(value)}</span>
      </div>
    `)
    .join("");
}

function renderObject(obj) {
  detailEl.innerHTML = `
    <div class="card">
      <div class="card-body">
        <p class="eyebrow">Analise fotometrica</p>
        <h2>${obj.nome}</h2>
        <p class="muted">O modelo compara brilhos medidos em filtros como u, g, r, i, z, W1 e W2. Valores menores de magnitude indicam mais brilho naquele filtro.</p>
        <div class="section">
          <div class="data-grid">${renderDataGrid(obj.dados)}</div>
        </div>
        <div class="prediction">
          <div>
            <span class="class-badge">${obj.classePrevista} - ${labels[obj.classePrevista]}</span>
            <h3 style="margin-top: 16px;">Por que essa previsao faz sentido?</h3>
            <p class="muted">${obj.explicacao}</p>
            <p class="muted" style="margin-top: 12px;">Escala didatica de distancia: ${obj.distancia}.</p>
          </div>
          <div class="confidence" aria-label="Confianca da previsao">${obj.confianca}%</div>
        </div>
      </div>
    </div>
  `;
}

function renderList(examples) {
  listEl.innerHTML = examples
    .map((obj, index) => `
      <button class="object-button ${index === 0 ? "active" : ""}" type="button" data-id="${obj.id}">
        ${obj.nome}
        <span>${labels[obj.classePrevista]} previsto com ${obj.confianca}%</span>
      </button>
    `)
    .join("");

  listEl.addEventListener("click", (event) => {
    const button = event.target.closest("[data-id]");
    if (!button) return;
    listEl.querySelectorAll(".object-button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    renderObject(examples.find((obj) => obj.id === button.dataset.id));
  });

  renderObject(examples[0]);
}

if (listEl && detailEl) {
  loadExamples()
    .then(renderList)
    .catch((error) => {
      detailEl.innerHTML = `<div class="card"><div class="card-body"><h2>Exemplos indisponiveis</h2><p class="muted">${error.message} Abra a pagina por um servidor local para permitir o carregamento do JSON.</p></div></div>`;
    });
}
