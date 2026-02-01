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

// TROCO AUTOMÁTICO
function calcularTroco() {
    const valor = parseFloat(
        (document.getElementById("valor")?.value || "0").replace(",", ".")
    );

    const recebido = parseFloat(
        (document.getElementById("recebido")?.value || "0").replace(",", ".")
    );

    const pagamento = document.getElementById("pagamento")?.value;
    const trocoEl = document.getElementById("troco");

    if (!trocoEl) return;

    if (pagamento === "Dinheiro" && recebido >= valor && valor > 0) {
        const troco = recebido - valor;
        trocoEl.innerText = "Troco: R$ " + troco.toFixed(2);
    } else {
        trocoEl.innerText = "";
    }
}

// abre o PDV automaticamente ao carregar
document.addEventListener("DOMContentLoaded", () => {
    showPage("pdv");
});
