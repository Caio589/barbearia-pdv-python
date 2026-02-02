function mostrarTela(id) {
    document.querySelectorAll(".tela").forEach(t => t.style.display = "none");
    document.getElementById(id).style.display = "block";
}

document.addEventListener("DOMContentLoaded", () => {
    mostrarTela("clientes");
    carregarClientes();
    carregarServicos();
});

// CLIENTES
function salvarCliente() {
    fetch("/clientes", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            nome: nomeCliente.value,
            telefone: telCliente.value
        })
    }).then(()=>carregarClientes());
}

function carregarClientes() {
    fetch("/clientes")
        .then(r=>r.json())
        .then(lista=>{
            listaClientes.innerHTML="";
            lista.forEach(c=>{
                const li=document.createElement("li");
                li.innerText=`${c[1]} - ${c[2]}`;
                listaClientes.appendChild(li);
            });
        });
}

// SERVIÇOS
function salvarServico() {
    fetch("/servicos", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            nome: nomeServico.value,
            valor: valorServico.value
        })
    }).then(()=>carregarServicos());
}

function carregarServicos() {
    fetch("/servicos")
        .then(r=>r.json())
        .then(lista=>{
            listaServicos.innerHTML="";
            lista.forEach(s=>{
                const li=document.createElement("li");
                li.innerText=`${s[1]} - R$ ${s[2]}`;
                listaServicos.appendChild(li);
            });
        });
}

// CAIXA
function abrirCaixa() {
    fetch("/abrir_caixa", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
       body: JSON.stringify({ valor: valorAbertura.value || 0 })
    }).then(r=>r.json()).then(d=>alert(d.msg));
}

function registrarMov() {
    fetch("/movimentacao", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            valor:valorMov.value,
            forma:formaMov.value
        })
    }).then(r=>r.json()).then(d=>alert(d.msg));
}

function fecharCaixa() {
    fetch("/fechar_caixa")
        .then(r=>r.json())
        .then(d=>{
            let txt=`Abertura: R$ ${d.abertura}\n`;
            for(let k in d){
                if(k!=="abertura" && k!=="total"){
                    txt+=`${k}: R$ ${d[k]}\n`;
                }
            }
            txt+=`\nTOTAL: R$ ${d.total}`;
            resumoCaixa.innerText=txt;
        });
}
function salvarPlano() {
    fetch("/planos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            nome: nomePlano.value,
            valor: valorPlano.value,
            quantidade: qtdPlano.value
        })
    })
    .then(r => r.json())
    .then(d => {
        alert(d.msg);
        nomePlano.value = "";
        valorPlano.value = "";
        qtdPlano.value = "";
        carregarPlanos();
    });
}

function carregarPlanos() {
    fetch("/planos")
        .then(r => r.json())
        .then(lista => {
            if (!Array.isArray(lista)) return;
            listaPlanos.innerHTML = "";
            lista.forEach(p => {
                const li = document.createElement("li");
                li.innerText = `${p[1]} — R$ ${p[2]} (${p[3]} usos)`;
                listaPlanos.appendChild(li);
            });
        });
}

document.addEventListener("DOMContentLoaded", carregarPlanos);

function salvarProduto() {
    fetch("/produtos", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            nome: nomeProduto.value,
            valor: valorProduto.value,
            estoque: estoqueProduto.value
        })
    })
    .then(r => r.json())
    .then(d => {
        alert(d.msg);
        nomeProduto.value = "";
        valorProduto.value = "";
        estoqueProduto.value = "";
        carregarProdutos();
    });
}

function carregarProdutos() {
    fetch("/produtos")
        .then(r=>r.json())
        .then(lista=>{
            if(!Array.isArray(lista)) return;
            listaProdutos.innerHTML="";
            lista.forEach(p=>{
                const li=document.createElement("li");
                li.innerText=`${p[1]} — R$ ${p[2]} (Estoque: ${p[3]})`;
                listaProdutos.appendChild(li);
            });
        });
}

document.addEventListener("DOMContentLoaded", carregarProdutos);

