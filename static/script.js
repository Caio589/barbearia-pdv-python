function mostrarTela(id) {
    document.querySelectorAll(".tela").forEach(tela => {
        tela.style.display = "none";
    });

    const tela = document.getElementById(id);
    if (tela) tela.style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
    mostrarTela("inicio");
});
