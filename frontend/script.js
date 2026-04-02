let features = [];
let csvData = [];
window.linhaSelecionada = null;
let graficoPizza = null;

const API_BASE = "https://astroclassifier-api.onrender.com";

async function carregarFeatures() {
  try {
    const res = await fetch(`${API_BASE}/features`);

    if (!res.ok) {
      throw new Error(`Erro HTTP ao buscar features: ${res.status}`);
    }

    const data = await res.json();
    features = data.features;

    const container = document.getElementById("campos");
    container.innerHTML = "";

    features.forEach(f => {
      const wrapper = document.createElement("div");
      wrapper.className = "campo-item";

      const label = document.createElement("label");
      label.setAttribute("for", f);
      label.textContent = f;

      const input = document.createElement("input");
      input.type = "number";
      input.step = "any";
      input.placeholder = `Digite ${f}`;
      input.id = f;
      input.name = f;

      wrapper.appendChild(label);
      wrapper.appendChild(input);
      container.appendChild(wrapper);
    });

  } catch (erro) {
    console.error("Erro ao carregar features:", erro);
    document.getElementById("resultado").innerText = "Erro ao carregar features.";
    document.getElementById("explicacao").innerText =
      "Verifique se o backend está online e se a rota /features está funcionando.";
  }
}

function carregarExemplo() {
  const exemplo = {
    specObjID: 3.2e17,
    ra: 180.0,
    dec: 0.1,
    mjd: 55000,
    plate: 3000,
    fiberID: 500,
    modelMag_u: 18,
    modelMag_g: 17,
    modelMag_r: 16,
    modelMag_i: 15,
    modelMag_z: 14,
    cmodelMag_u: 18,
    cmodelMag_g: 17,
    cmodelMag_r: 16,
    cmodelMag_i: 15,
    cmodelMag_z: 14,
    psfMag_u: 18,
    psfMag_g: 17,
    psfMag_r: 16,
    psfMag_i: 15,
    psfMag_z: 14,
    w1mpro: 13,
    w2mpro: 12,
    w3mpro: 11,
    w4mpro: 10,
    z: 0.5
  };

  features.forEach(f => {
    const campo = document.getElementById(f);
    if (campo) {
      campo.value = exemplo[f] ?? "";
    }
  });

  window.linhaSelecionada = null;

  document.getElementById("resultado").innerHTML =
    "Exemplo fixo carregado. Agora clique em <strong>Classificar</strong>.";
  document.getElementById("explicacao").innerText =
    "Esse exemplo não vem do CSV, então não haverá comparação com classe real.";
}

function carregarCSV() {
  const fileInput = document.getElementById("csvFile");
  const file = fileInput.files[0];

  if (!file) {
    alert("Selecione um arquivo CSV primeiro.");
    return;
  }

  console.log("Arquivo selecionado:", file.name);

  Papa.parse(file, {
    header: true,
    skipEmptyLines: true,
    delimiter: ";",
    complete: function(results) {
      console.log("PapaParse results:", results);

      if (!results.data || results.data.length === 0) {
        alert("Nenhuma linha válida encontrada no CSV.");
        return;
      }

      csvData = results.data;

      const linhaSelect = document.getElementById("linhaSelect");
      linhaSelect.innerHTML = "";

      csvData.forEach((row, index) => {
        const option = document.createElement("option");
        option.value = index;

        const classe = row.class ? ` | classe real: ${row.class}` : "";
        option.textContent = `Linha ${index}${classe}`;

        linhaSelect.appendChild(option);
      });

      window.linhaSelecionada = null;

      document.getElementById("resultado").innerHTML =
        `CSV carregado com sucesso. <strong>${csvData.length}</strong> linhas encontradas.`;
      document.getElementById("explicacao").innerText =
        "Agora escolha uma linha e clique em 'Preencher com linha selecionada'.";
    },
    error: function(error) {
      console.error("Erro ao ler CSV:", error);
      alert("Erro ao ler o CSV. Veja o console do navegador.");
    }
  });
}

function normalizarValor(valor) {
  if (valor === null || valor === undefined) return "";

  let texto = String(valor).trim();
  if (texto === "") return "";

  texto = texto.replace(/\s+/g, "");

  if (texto.includes(",")) {
    texto = texto.replace(/\./g, "");
    texto = texto.replace(",", ".");
  }

  return texto;
}

function preencherLinhaSelecionada() {
  const linhaSelect = document.getElementById("linhaSelect");
  const index = linhaSelect.value;

  if (index === "") {
    alert("Selecione uma linha primeiro.");
    return;
  }

  const row = csvData[index];
  window.linhaSelecionada = row;

  features.forEach(f => {
    const campo = document.getElementById(f);
    if (campo) {
      campo.value = normalizarValor(row[f]);
    }
  });

  const classeReal = row.class ? row.class : "não informada";

  document.getElementById("resultado").innerHTML =
    `Linha <strong>${index}</strong> carregada. Classe real do CSV: <strong>${classeReal}</strong>`;
  document.getElementById("explicacao").innerText =
    "Agora clique em Classificar para testar o modelo nessa linha.";
}

document.getElementById("form").addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    const dados = {};

    features.forEach(f => {
      dados[f] = document.getElementById(f).value.trim();
    });

    const res = await fetch(`${API_BASE}/classificar`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(dados)
    });

    const resultado = await res.json();

    if (!res.ok) {
      throw new Error(resultado.erro || "Erro ao classificar.");
    }

    let resultadoHTML = `
      <strong>Classe prevista:</strong> ${resultado.classe} <br>
      <strong>Confiança:</strong> ${Number(resultado.confianca).toFixed(2)}%
    `;

    if (window.linhaSelecionada && window.linhaSelecionada.class) {
      const classeReal = String(window.linhaSelecionada.class).trim().toUpperCase();
      const classePrevista = String(resultado.classe).trim().toUpperCase();

      resultadoHTML += `<br><br><strong>Classe real:</strong> ${classeReal}`;

      if (classeReal === classePrevista) {
        resultadoHTML += `<br>✅ Acertou`;
      } else {
        resultadoHTML += `<br>❌ Errou`;
      }
    }

    document.getElementById("resultado").innerHTML = resultadoHTML;
    document.getElementById("explicacao").innerText = resultado.explicacao;

  } catch (erro) {
    console.error("Erro ao classificar:", erro);
    document.getElementById("resultado").innerText = "Erro na classificação.";
    document.getElementById("explicacao").innerText = erro.message;
  }
});

async function testarLote() {
  try {
    if (!csvData.length) {
      alert("Carregue um CSV antes de testar em lote.");
      return;
    }

    const qtd = parseInt(document.getElementById("qtdLinhas").value, 10);

    if (!qtd || qtd < 1) {
      alert("Informe uma quantidade válida de linhas.");
      return;
    }

    const quantidadeFinal = Math.min(qtd, csvData.length);

    const embaralhado = [...csvData].sort(() => Math.random() - 0.5);
    const linhasSelecionadas = embaralhado.slice(0, quantidadeFinal);

    const res = await fetch(`${API_BASE}/classificar_lote`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ linhas: linhasSelecionadas })
    });

    const resultado = await res.json();

    if (!res.ok) {
      throw new Error(resultado.erro || "Erro no teste em lote.");
    }

    document.getElementById("m-total").innerText = resultado.total;
    document.getElementById("m-acertos").innerText = resultado.acertos;
    document.getElementById("m-erros").innerText = resultado.erros;
    document.getElementById("m-acuracia").innerText = `${Number(resultado.acuracia).toFixed(2)}%`;

    renderizarMatrizConfusao(resultado.matriz_confusao);
    renderizarGraficoPizza(resultado.matriz_confusao);

    document.getElementById("textoLote").innerText =
      `Teste em lote aleatório concluído com ${resultado.total} linhas.`;

  } catch (erro) {
    console.error("Erro no teste em lote:", erro);
    document.getElementById("textoLote").innerText = erro.message;
  }
}

function mostrarSecao(secao) {
  const modelo = document.getElementById("secao-modelo");
  const sobre = document.getElementById("secao-sobre");

  if (secao === "modelo") {
    modelo.style.display = "block";
    sobre.style.display = "none";
  } else {
    modelo.style.display = "none";
    sobre.style.display = "block";
  }
}

function renderizarMatrizConfusao(matriz) {
  const container = document.getElementById("matrizConfusao");

  const classes = ["STAR", "GALAXY", "QSO"];

  let html = `
    <table class="tabela-matriz">
      <thead>
        <tr>
          <th>Real \\ Previsto</th>
          ${classes.map(c => `<th>${c}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
  `;

  classes.forEach(real => {
    html += `<tr>`;
    html += `<th>${real}</th>`;

    classes.forEach(previsto => {
      const valor = matriz[real][previsto];
      const classeCelula = real === previsto ? "diagonal" : "fora-diagonal";
      html += `<td class="${classeCelula}">${valor}</td>`;
    });

    html += `</tr>`;
  });

  html += `
      </tbody>
    </table>
  `;

  container.innerHTML = html;
}

function renderizarGraficoPizza(matriz) {
  const ctx = document.getElementById("graficoPizza");
  const infoBox = document.getElementById("infoGrafico");

  const previsoes = {
    STAR: 0,
    GALAXY: 0,
    QSO: 0
  };

  Object.keys(matriz).forEach(real => {
    Object.keys(matriz[real]).forEach(prev => {
      previsoes[prev] += matriz[real][prev];
    });
  });

  const totalPrevisoes = previsoes.STAR + previsoes.GALAXY + previsoes.QSO;

  const data = {
    labels: ["STAR", "GALAXY", "QSO"],
    datasets: [{
      data: [
        previsoes.STAR,
        previsoes.GALAXY,
        previsoes.QSO
      ],
      backgroundColor: [
        "#4cc9f0",
        "#4361ee",
        "#b5179e"
      ],
      borderColor: "#081225",
      borderWidth: 2
    }]
  };

  if (graficoPizza) {
    graficoPizza.destroy();
  }

  graficoPizza = new Chart(ctx, {
    type: "pie",
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          labels: {
            color: "#ffffff"
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const valor = context.raw;
              const porcentagem = totalPrevisoes > 0
                ? ((valor / totalPrevisoes) * 100).toFixed(2)
                : "0.00";
              return `${context.label}: ${valor} (${porcentagem}%)`;
            }
          }
        }
      },
      onHover: (event, elements) => {
        if (!elements.length) {
          infoBox.innerHTML = "Passe o mouse no gráfico para ver detalhes.";
          return;
        }

        const index = elements[0].index;
        const classePrevista = data.labels[index];
        const totalDaClasse = previsoes[classePrevista];

        const porcentagemNoGrafico = totalPrevisoes > 0
          ? ((totalDaClasse / totalPrevisoes) * 100).toFixed(2)
          : "0.00";

        let maiorOrigem = null;
        let maiorValor = -1;

        Object.keys(matriz).forEach(classeReal => {
          const valor = matriz[classeReal][classePrevista];
          if (valor > maiorValor) {
            maiorValor = valor;
            maiorOrigem = classeReal;
          }
        });

        let texto = `<strong>${classePrevista}</strong> corresponde a <strong>${porcentagemNoGrafico}%</strong> das previsões totais.`;

        if (totalDaClasse > 0) {
          const porcentagemOrigem = ((maiorValor / totalDaClasse) * 100).toFixed(2);

          if (maiorOrigem === classePrevista) {
            texto += ` A maior parte dessas previsões foi correta: <strong>${porcentagemOrigem}%</strong>.`;
          } else {
            texto += ` A principal confusão foi com objetos reais da classe <strong>${maiorOrigem}</strong>, representando <strong>${porcentagemOrigem}%</strong> das previsões de ${classePrevista}.`;
          }
        }

        infoBox.innerHTML = texto;
      }
    }
  });
}

function resetarAnalise() {
  window.linhaSelecionada = null;

  features.forEach(f => {
    const campo = document.getElementById(f);
    if (campo) campo.value = "";
  });

  const csvFile = document.getElementById("csvFile");
  if (csvFile) csvFile.value = "";

  csvData = [];

  const linhaSelect = document.getElementById("linhaSelect");
  if (linhaSelect) {
    linhaSelect.innerHTML = `<option value="">Nenhuma linha carregada</option>`;
  }

  const qtdLinhas = document.getElementById("qtdLinhas");
  if (qtdLinhas) qtdLinhas.value = 50;

  document.getElementById("resultado").innerHTML = "Nenhuma classificação realizada ainda.";
  document.getElementById("explicacao").innerHTML = "A explicação aparecerá aqui.";

  document.getElementById("m-total").innerText = "0";
  document.getElementById("m-acertos").innerText = "0";
  document.getElementById("m-erros").innerText = "0";
  document.getElementById("m-acuracia").innerText = "0%";
  document.getElementById("textoLote").innerText = "Nenhum teste em lote executado ainda.";

  const matriz = document.getElementById("matrizConfusao");
  if (matriz) {
    matriz.innerHTML = `<div class="matriz-vazia">Nenhum teste em lote executado ainda.</div>`;
  }

  const infoGrafico = document.getElementById("infoGrafico");
  if (infoGrafico) {
    infoGrafico.innerHTML = "Passe o mouse no gráfico para ver detalhes.";
  }

  if (graficoPizza) {
    graficoPizza.destroy();
    graficoPizza = null;
  }
}

carregarFeatures();