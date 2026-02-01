function addCliente(){
  fetch("/clientes",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({nome:cliente.value})
  })
}

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
  })
}
