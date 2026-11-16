document.addEventListener("DOMContentLoaded", () => {
    // 1. Busca o elemento principal
    const modal = document.getElementById("tema-modal");

    // 2. Trava de segurança: Se o modal não existe nesta página, o script para aqui.
    // Isso evita todos aqueles erros de "null" e conflitos.
    if (!modal) return;

    // 3. Seleção dos demais elementos
    const form = document.getElementById("tema-form-edicao");
    const nome = document.getElementById("tema-nome");
    const fechar = document.getElementById("fechar-tema-modal");
    const cancelar = document.getElementById("cancelar-tema-modal");
    const excluir = document.getElementById("excluir-tema-modal");

    // 4. Funções
    function abrirEdicao(card) {
        form.action = card.dataset.editarUrl;

        // Adicionada uma pequena checagem para evitar erro se o 'a' não for encontrado
        const tituloLink = card.querySelector(".card-title a");
        if (tituloLink) {
            nome.value = tituloLink.textContent.trim();
        }

        if (excluir) {
            excluir.dataset.excluirUrl = card.dataset.editarUrl.replace("/editar/", "/excluir/");
            excluir.style.display = "inline-block";
        }

        modal.style.display = "block";
        nome.focus();
    }

    function fecharModal() {
        modal.style.display = "none";
    }

    // 5. Evento de duplo clique nos cards
    document.querySelectorAll(".tema-card").forEach(card => {
        card.addEventListener("dblclick", event => {
            if (event.target.closest("a, button, form")) {
                return;
            }
            abrirEdicao(card);
        });
    });

    // 6. Eventos de fechar o modal
    if (fechar) fechar.addEventListener("click", fecharModal);
    if (cancelar) cancelar.addEventListener("click", fecharModal);

    window.addEventListener("click", event => {
        if (event.target === modal) {
            fecharModal();
        }
    });

    // 7. Confirmação nos formulários de exclusão em lista
    document.querySelectorAll(".form-excluir").forEach(formExcluir => {
        formExcluir.addEventListener("submit", event => {
            const mensagem = formExcluir.dataset.mensagem;
            if (mensagem && !window.confirm(mensagem)) {
                event.preventDefault();
            }
        });
    });

    // 8. Evento de exclusão pelo modal
    if (excluir) {
        excluir.addEventListener("click", () => {
            const action = excluir.dataset.excluirUrl;

            if (!action || !window.confirm("Tem certeza que deseja excluir este tema? Todos os conteúdos também serão excluídos.")) {
                return;
            }

            const formulario = document.createElement("form");
            formulario.method = "post";
            formulario.action = action;

            const csrf = form.querySelector("input[name='csrfmiddlewaretoken']");
            if (csrf) {
                const token = document.createElement("input");
                token.type = "hidden";
                token.name = "csrfmiddlewaretoken";
                token.value = csrf.value;
                formulario.appendChild(token);
            }

            document.body.appendChild(formulario);
            formulario.submit();
        });
    }

    // 9. Lógica de auto-open (quando retorna erro do backend)
    if (modal.dataset.autoOpen === "true") {
        if (modal.dataset.editarUrl) {
            form.action = modal.dataset.editarUrl;
            
            if (excluir) {
                excluir.dataset.excluirUrl = modal.dataset.editarUrl.replace("/editar/", "/excluir/");
                excluir.style.display = "inline-block";
            }
        }
        modal.style.display = "block";
        nome.focus();
    }
});