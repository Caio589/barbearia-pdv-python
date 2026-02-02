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
/* ======================
   SERVIÇOS
====================== */

function criarServico() {
    fetch("/servicos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            nome: nomeServico.value,
            valor: valorServico.value,
            duracao: duracaoServico.value
        })
    })
    .then(r => r.json())
    .then(d => {
        alert(d.msg || d.erro);
        carregarServicos();
    });
}

function carregarServicos() {
    fetch("/servicos")
        .then(r => r.json())
        .then(lista => {
            const ul = document.getElementById("listaServicos");
            ul.innerHTML = "";
            lista.forEach(s => {
                const li = document.createElement("li");
                li.innerText = `${s[1]} — R$ ${s[2]} (${s[3]} min)`;
                ul.appendChild(li);
            });
        });
}

/* carrega quando abrir a tela */
document.addEventListener("DOMContentLoaded", () => {
    carregarServicos();
});
