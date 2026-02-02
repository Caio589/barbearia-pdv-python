function mostrar(id) {
  document.querySelectorAll(".aba").forEach(a => a.style.display = "none");
  document.getElementById(id).style.display = "block";
}

// mostrar aba inicial
mostrar("clientes");

// CLIENTES
function addCliente(){
  fetch("/clientes",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({nome:cliente.value})
  }).then(()=>carregarClientes());
}

function carregarClientes(){
  fetch("/clientes")
    .then(r=>r.json())
    .then(d=>{
      listaClientes.innerHTML="";
      d.forEach(c=>{
        listaClientes.innerHTML+=`<li>${c[1]}</li>`;
      });
    });
}
carregarClientes();

// AGENDA
function agendar(){
  fetch("/agenda",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      cliente:ag_cliente.value,
      servico:ag_servico.value,
      data:ag_data.value,
      hora:ag_hora.value
    })
  }).then(()=>carregarAgenda());
}

function carregarAgenda(){
  fetch("/agenda")
    .then(r=>r.json())
    .then(d=>{
      listaAgenda.innerHTML="";
      d.forEach(a=>{
        listaAgenda.innerHTML+=
          `<li>${a[1]} - ${a[2]} (${a[3]} ${a[4]})</li>`;
      });
    });
}
carregarAgenda();

// CAIXA (placeholder)
function abrirCaixa(){ alert("Caixa aberto"); }
function criarPlano() {
    fetch("/planos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            nome: nomePlano.value,
            usos: usosPlano.value,
            valor: valorPlano.value
        })
    }).then(r=>r.json()).then(alert);
}

function venderPlano() {
    fetch("/vender_plano", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            cliente_id: clientePlano.value,
            plano_id: planoID.value
        })
    }).then(r=>r.json()).then(alert);
}

function fecharCaixa(){ alert("Caixa fechado"); }
