const modal = document.getElementById(
    "conteudo-modal"
);

const form = document.getElementById(
    "conteudo-form-edicao"
);

const nome = document.getElementById(
    "conteudo-nome"
);

const fechar = document.getElementById(
    "fechar-conteudo-modal"
);

const cancelar = document.getElementById(
    "cancelar-conteudo-modal"
);

const excluir = document.getElementById(
    "excluir-conteudo-modal"
);


function abrirEdicao(card) {

    form.action =
        card.dataset.editarUrl;

    nome.value =
        card.querySelector(
            ".card-title"
        ).textContent.trim();


    excluir.dataset.excluirUrl =
        card.dataset.editarUrl.replace(
            "/editar/",
            "/excluir/"
        );


    excluir.style.display =
        "inline-block";

    modal.style.display =
        "block";

    nome.focus();
}


function fecharModal() {

    modal.style.display =
        "none";

}


document
    .querySelectorAll(".conteudo-card")
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

                abrirEdicao(card);

            }
        );

    });


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


excluir.addEventListener(
    "click",
    () => {

        const action =
            excluir.dataset.excluirUrl;


        if (
            !action ||
            !window.confirm(
                "Tem certeza que deseja excluir este conteúdo?"
            )
        ) {
            return;
        }


        const formulario =
            document.createElement(
                "form"
            );

        formulario.method =
            "post";

        formulario.action =
            action;


        const csrf =
            form.querySelector(
                "input[name='csrfmiddlewaretoken']"
            );


        if (csrf) {

            const token =
                document.createElement(
                    "input"
                );

            token.type =
                "hidden";

            token.name =
                "csrfmiddlewaretoken";

            token.value =
                csrf.value;

            formulario.appendChild(
                token
            );

        }


        document.body.appendChild(
            formulario
        );

        formulario.submit();

    }
);


if (
    modal.dataset.autoOpen === "true"
) {

    if (modal.dataset.editarUrl) {

        form.action =
            modal.dataset.editarUrl;

        excluir.dataset.excluirUrl =
            modal.dataset.editarUrl.replace(
                "/editar/",
                "/excluir/"
            );

        excluir.style.display =
            "inline-block";
    }

    modal.style.display =
        "block";

    nome.focus();
}