function mostrarTela(id) {
    document.querySelectorAll(".tela").forEach(tela => {
        tela.style.display = "none";
    });
    document.getElementById(id).style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
    mostrarTela("inicio");
    carregarClientes();
});

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
            const ul = document.getElementById("listaClientes");
            ul.innerHTML = "";
            lista.forEach(c => {
                const li = document.createElement("li");
                li.innerText = `${c[1]} — ${c[2]}`;
                ul.appendChild(li);
            });
        });
}
