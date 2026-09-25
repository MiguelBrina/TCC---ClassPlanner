const modalExclusao = document.getElementById("modal-exclusao");
const abrirExclusao = document.getElementById("abrir-exclusao");
const cancelarExclusao = document.getElementById("cancelar-exclusao");

const diasSelecionados = [];
const horarios = [];

const diasIniciais = JSON.parse(
    document.getElementById("dias-iniciais").textContent
);

const horariosIniciais = JSON.parse(
    document.getElementById("horarios-iniciais").textContent
);


/* MODAL DE EXCLUSÃO */

if (modalExclusao.dataset.temErros === "true") {
    modalExclusao.style.display = "block";
}

abrirExclusao.addEventListener("click", () => {
    modalExclusao.style.display = "block";
});

cancelarExclusao.addEventListener("click", () => {
    modalExclusao.style.display = "none";
});


/* DIAS */

document.querySelectorAll(".dia").forEach(botao => {

    botao.addEventListener("click", () => {

        const dia = botao.dataset.dia;

        const index = diasSelecionados.indexOf(dia);

        if (index === -1) {

            diasSelecionados.push(dia);
            botao.classList.add("selecionado");

        } else {

            diasSelecionados.splice(index, 1);
            botao.classList.remove("selecionado");

        }

        atualizarCampoDias();
    });
});


function atualizarCampoDias() {

    document.getElementById("id_dias").value =
        JSON.stringify(diasSelecionados);

}


/* HORÁRIOS */

function renderizarHorarios() {

    const container =
        document.getElementById("horarios-container");

    container.innerHTML = "";

    horarios.forEach((horario, index) => {

        const linha = document.createElement("div");

        linha.className = "horario";

        linha.innerHTML = `
            <input
                type="time"
                value="${horario.horario}"
                data-index="${index}"
            >

            <button
                type="button"
                data-editar="${index}"
                title="Editar horário"
            >
                ✏️
            </button>

            <button
                type="button"
                data-remover="${index}"
                title="Remover horário"
            >
                ×
            </button>
        `;

        container.appendChild(linha);

    });

    atualizarCampoHorarios();
}


function atualizarCampoHorarios() {

    document.getElementById("id_horarios").value =
        JSON.stringify(horarios);

}


/* ADICIONAR HORÁRIO */

document
    .getElementById("adicionar-horario")
    .addEventListener("click", () => {

        horarios.push({
            horario: ""
        });

        renderizarHorarios();
    });


/* ALTERAR HORÁRIO */

document
    .getElementById("horarios-container")
    .addEventListener("input", event => {

        const input = event.target;

        if (input.dataset.index === undefined) {
            return;
        }

        const index = Number(input.dataset.index);

        horarios[index].horario = input.value;

        atualizarCampoHorarios();
    });


/* REMOVER HORÁRIO */

document
    .getElementById("horarios-container")
    .addEventListener("click", event => {

        const remover = event.target.dataset.remover;

        if (remover === undefined) {
            return;
        }

        horarios.splice(Number(remover), 1);

        renderizarHorarios();
    });


/* CARREGAR DADOS EXISTENTES */

diasIniciais.forEach(dia => {

    diasSelecionados.push(dia);

    const botao =
        document.querySelector(
            `.dia[data-dia="${dia}"]`
        );

    if (botao) {
        botao.classList.add("selecionado");
    }

});


horariosIniciais.forEach(horario => {

    horarios.push({
        horario: horario.horario
    });

});


/* INICIALIZAÇÃO */

atualizarCampoDias();
renderizarHorarios();


/* ENVIO DO FORMULÁRIO */

document
    .getElementById("configuracao-form")
    .addEventListener("submit", () => {

        atualizarCampoDias();
        atualizarCampoHorarios();

    });