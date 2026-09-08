const currentPage = window.location.pathname.split("/").pop() || "index.html";

document.querySelectorAll(".nav-links a").forEach((link) => {
  const href = link.getAttribute("href");
  if (href === currentPage || (currentPage === "" && href === "index.html")) {
    link.classList.add("active");
  }
});

const toggle = document.querySelector(".nav-toggle");
const links = document.querySelector(".nav-links");

if (toggle && links) {
  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });
}

function replaceMissingGraph(img) {
  if (!img || img.dataset.fallbackApplied === "true") return;
  img.dataset.fallbackApplied = "true";
  const file = img.getAttribute("src").split("/").pop();
  const placeholder = document.createElement("div");
  placeholder.className = "graph-placeholder";
  placeholder.textContent = `Grafico aguardando arquivo: ${file}`;
  img.replaceWith(placeholder);
}

document.querySelectorAll("img[data-graph]").forEach((img) => {
  img.addEventListener("error", () => {
    replaceMissingGraph(img);
  });

  if (img.complete && img.naturalWidth === 0) {
    replaceMissingGraph(img);
  }
});

const contactForm = document.querySelector("[data-contact-form]");

if (contactForm) {
  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const status = contactForm.querySelector("[data-form-status]");
    const button = contactForm.querySelector('button[type="submit"]');

    if (status) {
      status.textContent = "";
    }

    if (button) {
      button.disabled = true;
      button.textContent = "Enviando...";
    }

    try {
      const response = await fetch("https://formspree.io/f/xppzoraw", {
        method: "POST",
        body: new FormData(contactForm),
        headers: {
          Accept: "application/json"
        }
      });

      if (!response.ok) {
        throw new Error("Falha no envio da mensagem.");
      }

      contactForm.reset();

      if (status) {
        status.textContent =
          "Mensagem enviada com sucesso! Obrigada pelo contato.";
      }
    } catch (error) {
      console.error("Erro ao enviar formulário:", error);

      if (status) {
        status.textContent =
          "Não foi possível enviar a mensagem. Tente novamente em alguns instantes.";
      }
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = "Enviar mensagem";
      }
    }
  });
}

const featurePills = document.querySelector("[data-feature-pills]");
const featureExplanation = document.querySelector(
  "[data-feature-explanation]"
);

const featureInfo = {
  u: {
    title: "u — Ultravioleta próximo",
    text: "Filtro do SDSS sensível a comprimentos de onda mais curtos, centrado aproximadamente em 355 nm. Ajuda a identificar diferenças na emissão dos objetos na região próxima ao ultravioleta."
  },

  g: {
    title: "g — Banda óptica",
    text: "Filtro do SDSS centrado aproximadamente em 469 nm. Mede parte da luz visível e contribui para caracterizar a distribuição de brilho do objeto."
  },

  r: {
    title: "r — Banda óptica",
    text: "Filtro do SDSS centrado aproximadamente em 617 nm. Observa uma região mais avermelhada do espectro visível e complementa as demais bandas ópticas."
  },

  i: {
    title: "i — Óptico / infravermelho próximo",
    text: "Filtro do SDSS centrado aproximadamente em 748 nm, próximo da transição entre a luz visível e o infravermelho próximo."
  },

  z: {
    title: "z — Infravermelho próximo",
    text: "Filtro do SDSS centrado aproximadamente em 893 nm. Mede a emissão do objeto em comprimentos de onda maiores que as bandas ópticas anteriores."
  },

  W1: {
    title: "W1 — Infravermelho · 3,4 µm",
    text: "Banda do WISE centrada em aproximadamente 3,4 µm. As medições no infravermelho ajudam a distinguir objetos que podem apresentar comportamentos semelhantes nas bandas ópticas."
  },

  W2: {
    title: "W2 — Infravermelho · 4,6 µm",
    text: "Banda do WISE centrada em aproximadamente 4,6 µm. Em conjunto com W1, fornece informações importantes sobre a assinatura infravermelha do objeto."
  },
  W3: {
  title: "W3 — Infravermelho · 12 µm",
  text: "Banda do WISE centrada em aproximadamente 12 µm. Observa uma região do infravermelho em que podem aparecer informações relacionadas, por exemplo, à emissão de poeira."
  },

  W4: {
    title: "W4 — Infravermelho · 22 µm",
    text: "Banda do WISE centrada em aproximadamente 22 µm. É a banda de maior comprimento de onda entre as quatro utilizadas pelo modelo."
  },

  redshift: {
    title: "Redshift — Desvio para o vermelho",
    text: "Representa o deslocamento observado do espectro para comprimentos de onda maiores. É uma característica especialmente útil na análise de objetos extragalácticos e distantes."
  }
};

if (featurePills && featureExplanation) {
featurePills.addEventListener("click", (event) => {
  const button = event.target.closest("[data-feature]");

  if (!button) return;

  const feature = featureInfo[button.dataset.feature];

  if (!feature) return;

  const isActive = button.classList.contains("active");

  featurePills.querySelectorAll("[data-feature]").forEach((item) => {
    item.classList.remove("active");
  });

  if (isActive) {
    featureExplanation.hidden = true;
    featureExplanation.innerHTML = "";
    return;
  }

  button.classList.add("active");

  featureExplanation.innerHTML = `
    <h3>${feature.title}</h3>
    <p>${feature.text}</p>
  `;

  featureExplanation.hidden = false;
});
}

async function carregarFooter() {
  const footer = document.getElementById("footer");

  if (!footer) return;

  const resposta = await fetch("components/footer.html?v=2");

  if (!resposta.ok) {
    console.error(`Erro ao carregar o rodapé: ${resposta.status}`);
    return;
  }

  const html = await resposta.text();
  footer.innerHTML = html;
}

carregarFooter();