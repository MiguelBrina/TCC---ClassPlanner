const modal = document.getElementById(
    "disciplina-modal"
);

const form = document.getElementById(
    "disciplina-form"
);

const titulo = document.getElementById(
    "disciplina-modal-titulo"
);

const nome = document.getElementById(
    "disciplina-nome"
);

const cor = document.getElementById(
    "disciplina-cor"
);

const abrirNova = document.getElementById(
    "abrir-nova-disciplina"
);

const fechar = document.getElementById(
    "fechar-disciplina-modal"
);

const cancelar = document.getElementById(
    "cancelar-disciplina-modal"
);

const excluirModal = document.getElementById(
    "excluir-disciplina-modal"
);

const formularioExcluirModal =
    document.getElementById(
        "disciplina-form-excluir"
    );


function abrirModalNovo() {

    titulo.textContent = "Nova disciplina";

    form.action =
        form.dataset.novaUrl ||
        form.action;

    nome.value = "";

    cor.value = "#3b82f6";

    excluirModal.style.display = "none";

    modal.style.display = "block";

    nome.focus();
}


function abrirModalEdicao(card) {

    titulo.textContent = "Editar disciplina";

    form.action =
        card.dataset.editarUrl;

    nome.value =
        card.querySelector(
            ".card-title a"
        ).textContent.trim();


    const corAtual =
        card.querySelector(
            ".disciplina-color-tag"
        );

    const valorCor =
        corAtual?.style.backgroundColor;


    if (valorCor) {

        if (valorCor.startsWith("rgb")) {

            const valores =
                valorCor.match(/\d+/g);

            if (
                valores &&
                valores.length >= 3
            ) {

                cor.value =
                    "#" +
                    valores
                        .slice(0, 3)
                        .map(
                            valor =>
                                Number(valor)
                                    .toString(16)
                                    .padStart(2, "0")
                        )
                        .join("");

            }

        } else {

            cor.value = valorCor;

        }

    }


    formularioExcluirModal.action =
        form.action.replace(
            "/editar/",
            "/excluir/"
        );


    excluirModal.style.display =
        "inline-block";

    modal.style.display =
        "block";

    nome.focus();
}


function fecharModal() {

    modal.style.display = "none";

}


abrirNova.addEventListener(
    "click",
    abrirModalNovo
);


fechar.addEventListener(
    "click",
    fecharModal
);


cancelar.addEventListener(
    "click",
    fecharModal
);


window.addEventListener(
    "click",
    event => {

        if (event.target === modal) {
            fecharModal();
        }

    }
);


document
    .querySelectorAll(".disciplina-card")
    .forEach(card => {

        card.addEventListener(
            "dblclick",
            event => {

                if (
                    event.target.closest(
                        "a, button, form"
                    )
                ) {
                    return;
                }

                abrirModalEdicao(card);

            }
        );

    });


document
    .querySelectorAll(".form-excluir")
    .forEach(formExcluir => {

        formExcluir.addEventListener(
            "submit",
            event => {

                const mensagem =
                    formExcluir.dataset.mensagem;

                if (
                    mensagem &&
                    !window.confirm(mensagem)
                ) {
                    event.preventDefault();
                }

            }
        );

    });


excluirModal.addEventListener(
    "click",
    () => {

        if (
            formularioExcluirModal.action &&
            window.confirm(
                "Tem certeza que deseja excluir esta disciplina? Todos os seus temas e conteúdos também serão excluídos."
            )
        ) {

            formularioExcluirModal.submit();

        }

    }
);


if (
    modal.dataset.autoOpen === "true"
) {

    titulo.textContent =
        "Editar disciplina";

    if (
        modal.dataset.editarUrl
    ) {
        form.action =
            modal.dataset.editarUrl;

        formularioExcluirModal.action =
            modal.dataset.editarUrl.replace(
                "/editar/",
                "/excluir/"
            );

        excluirModal.style.display =
            "inline-block";
    }

    modal.style.display =
        "block";

    nome.focus();
}