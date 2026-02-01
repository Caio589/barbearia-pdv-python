function showPage(pageId) {
  // esconde todas as páginas
  document.querySelectorAll(".page").forEach(page => {
    page.classList.add("hidden");
  });

  // mostra a página clicada
  const page = document.getElementById(pageId);
  if (page) {
    page.classList.remove("hidden");
  }
}

// abre o PDV automaticamente
document.addEventListener("DOMContentLoaded", () => {
  showPage("pdv");
});
