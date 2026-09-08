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