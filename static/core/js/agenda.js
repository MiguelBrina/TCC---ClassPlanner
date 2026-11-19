
/*
 * Controla os campos de aluno e disciplina da agenda.
 *
 * Cada disciplina possui um atributo data-aluno,
 * que identifica o aluno matriculado naquela disciplina.
 */

// Recupera todos os campos de seleção de aluno.
const camposAluno = document.querySelectorAll(".campo-aluno");

// Percorre cada campo de aluno.
camposAluno.forEach((campoAluno) => {

    // Localiza o campo de disciplina do mesmo bloco.
    const bloco = campoAluno.dataset.bloco;

    const campoDisciplina = document.querySelector(
        `.campo-disciplina[data-bloco="${bloco}"]`
    );

    // Ignora caso não exista o campo correspondente.
    if (!campoDisciplina) {
        return;
    }

    // Atualiza as disciplinas disponíveis para o aluno selecionado.
    function atualizarDisciplinas() {

        // Recupera o ID do aluno escolhido.
        const alunoSelecionado = campoAluno.value;

        // Percorre todas as opções de disciplina.
        Array.from(campoDisciplina.options).forEach((opcao) => {

            // A primeira opção é sempre o campo vazio.
            if (!opcao.value) {
                opcao.hidden = false;
                opcao.disabled = false;
                return;
            }

            // Verifica a qual aluno aquela disciplina pertence.
            const alunoDaOpcao = opcao.dataset.aluno;

            // Só deixa disponível uma disciplina matriculada
            // para o aluno selecionado.
            const pertenceAoAluno = (
                alunoSelecionado &&
                alunoDaOpcao === alunoSelecionado
            );

            opcao.hidden = !pertenceAoAluno;
            opcao.disabled = !pertenceAoAluno;

        });

        // Se não houver aluno selecionado, desativa a disciplina.
        campoDisciplina.disabled = !alunoSelecionado;

        // Se a disciplina selecionada não pertencer ao novo aluno,
        // limpa a seleção para evitar uma combinação inválida.
        const opcaoSelecionada = campoDisciplina.selectedOptions[0];

        if (
            opcaoSelecionada &&
            opcaoSelecionada.value &&
            opcaoSelecionada.dataset.aluno !== alunoSelecionado
        ) {
            campoDisciplina.value = "";
        }
    }

    // Atualiza quando o professor troca o aluno.
    campoAluno.addEventListener("change", atualizarDisciplinas);

    // Atualiza também quando a página é carregada.
    atualizarDisciplinas();

});
