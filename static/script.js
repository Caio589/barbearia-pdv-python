function mostrarTela(id) {
    document.querySelectorAll(".tela").forEach(tela => {
        tela.style.display = "none";
    });

    document.getElementById(id).style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
    mostrarTela("clientes");
});

/* PLANOS */
function criarPlano() {
    fetch("/planos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            nome: nomePlano.value,
            usos: usosPlano.value,
            valor: valorPlano.value
        })
    })
    .then(r => r.json())
    .then(d => alert(d.msg || d.erro));
}

function venderPlano() {
    fetch("/vender_plano", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            cliente_id: clientePlano.value,
            plano_id: planoID.value
        })
    })
    .then(r => r.json())
    .then(d => alert(d.msg || d.erro));
}
