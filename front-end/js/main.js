alert("main.js carregou");
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
  contactForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const status = contactForm.querySelector("[data-form-status]");
    if (status) {
      status.textContent = "Mensagem registrada nesta demonstracao. Conecte um backend para envio real.";
    }
  });
}

async function carregarFooter(){

    const resposta = await fetch("components/footer.html");

    const html = await resposta.text();

    document.getElementById("footer").innerHTML = html;

}

carregarFooter();