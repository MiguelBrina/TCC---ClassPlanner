const diasSelecionados = [];
const horarios = [];

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

        document.getElementById("id_dias").value =
            JSON.stringify(diasSelecionados);

    });

});


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
                data-tipo="horario"
            >

            <button
                type="button"
                data-remover="${index}"
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


document
    .getElementById("adicionar-horario")
    .addEventListener("click", () => {

        horarios.push({
            horario: ""
        });

        renderizarHorarios();

    });


document
    .getElementById("horarios-container")
    .addEventListener("input", event => {

        const input = event.target;

        if (input.dataset.index === undefined) {
            return;
        }

        const index = Number(input.dataset.index);
        const tipo = input.dataset.tipo;

        horarios[index][tipo] = input.value;

        atualizarCampoHorarios();

    });


document
    .getElementById("horarios-container")
    .addEventListener("click", event => {

        const index = event.target.dataset.remover;

        if (index === undefined) {
            return;
        }

        horarios.splice(Number(index), 1);

        renderizarHorarios();

    });


document
    .getElementById("configuracao-form")
    .addEventListener("submit", () => {

        document.getElementById("id_dias").value =
            JSON.stringify(diasSelecionados);

        document.getElementById("id_horarios").value =
            JSON.stringify(horarios);

    });