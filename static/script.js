function mostrarTela(id) {
    document.querySelectorAll(".tela").forEach(t => t.style.display = "none");
    document.getElementById(id).style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
    mostrarTela("inicio");
    carregarClientes();
    carregarServicos();
});

/* CLIENTES */
function salvarCliente() {
    fetch("/clientes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            nome: nomeCliente.value,
            telefone: telCliente.value
        })
    })
    .then(r => r.json())
    .then(d => {
        alert(d.msg);
        nomeCliente.value = "";
        telCliente.value = "";
        carregarClientes();
    });
}

function carregarClientes() {
    fetch("/clientes")
        .then(r => r.json())
        .then(lista => {
            listaClientes.innerHTML = "";
            lista.forEach(c => {
                const li = document.createElement("li");
                li.innerText = `${c[1]} — ${c[2]}`;
                listaClientes.appendChild(li);
            });
        });
}

/* SERVIÇOS */
function salvarServico() {
    fetch("/servicos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            nome: nomeServico.value,
            valor: valorServico.value
        })
    })
    .then(r => r.json())
    .then(d => {
        alert(d.msg);
        nomeServico.value = "";
        valorServico.value = "";
        carregarServicos();
    });
}

function carregarServicos() {
    fetch("/servicos")
        .then(r => r.json())
        .then(lista => {
            listaServicos.innerHTML = "";
            lista.forEach(s => {
                const li = document.createElement("li");
                li.innerText = `${s[1]} — R$ ${s[2]}`;
                listaServicos.appendChild(li);
            });
        });
}
