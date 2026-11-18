
document
    .querySelectorAll(".form-excluir")
    .forEach(formExcluir => {

        formExcluir.addEventListener("submit", event => {

            const mensagem = formExcluir.dataset.mensagem;

            if (mensagem && !window.confirm(mensagem)) {
                event.preventDefault();
            }

        });

    });
