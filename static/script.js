function show(id){
  document.querySelectorAll('.page').forEach(p=>p.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
}

function troco(){
  const v = parseFloat(document.getElementById("valor").value || 0);
  const r = parseFloat(document.getElementById("recebido").value || 0);
  const p = document.getElementById("pagamento").value;

  if(p === "Dinheiro"){
    document.getElementById("troco").innerText = "Troco: R$ " + (r - v).toFixed(2);
  } else {
    document.getElementById("troco").innerText = "";
  }
}
