function abrirCaixa() {
    fetch("/abrir_caixa", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ valor: valorAbertura.value })
    })
    .then(r => r.json())
    .then(d => alert(d.msg));
}

function registrarMov() {
    fetch("/movimentacao", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            valor: valorMov.value,
            forma: formaMov.value
        })
    })
    .then(r => r.json())
    .then(d => alert(d.msg));
}

function fecharCaixa() {
    fetch("/fechar_caixa")
        .then(r => r.json())
        .then(d => {
            let txt = `Abertura: R$ ${d.abertura}\n`;
            for (let k in d) {
                if (k !== "abertura" && k !== "total") {
                    txt += `${k}: R$ ${d[k]}\n`;
                }
            }
            txt += `\nTOTAL EM CAIXA: R$ ${d.total}`;
            resumoCaixa.innerText = txt;
        });
}
