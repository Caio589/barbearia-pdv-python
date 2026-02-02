function mostrarTela(id) {
    document.querySelectorAll(".tela").forEach(t => t.style.display = "none");
    document.getElementById(id).style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
    mostrarTela("clientes");
});

function criarPlano() {
    fetch("/planos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
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
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            cliente_id: clientePlano.value,
            plano_id: planoID.value
        })
    })
    .then(r => r.json())
    .then(d => alert(d.msg || d.erro));
}

function usarPlano() {
    fetch("/usar_plano", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            cliente_id: clienteUsoPlano.value
        })
    })
    .then(r => r.json())
    .then(d => {
        if (d.erro) alert(d.erro);
        else alert(`✔ ${d.msg}\nUsos restantes: ${d.usos_restantes}`);
    });
}
