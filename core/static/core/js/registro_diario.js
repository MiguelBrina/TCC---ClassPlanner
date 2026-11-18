
document.addEventListener("DOMContentLoaded", function () {
    const areaConteudos = document.getElementById("area-conteudos");

    const temas = document.querySelectorAll(
        '#area-temas input[type="checkbox"]'
    );

    const conteudos = document.querySelectorAll(
        '#area-conteudos input[type="checkbox"]'
    );

    function atualizarConteudos() {
        const temasSelecionados = [];

        temas.forEach(tema => {
            if (tema.checked) {
                temasSelecionados.push(tema.value);
            }
        });

        areaConteudos.style.display =
            temasSelecionados.length > 0 ? "block" : "none";

        conteudos.forEach(conteudo => {
            const temaId = conteudo.dataset.temaId;

            const pertenceAoTema = temasSelecionados.some(id =>
                conteudo.dataset.temaId === id
            );

            conteudo.parentElement.style.display =
                pertenceAoTema ? "block" : "none";

            if (!pertenceAoTema) {
                conteudo.checked = false;
            }
        });
    }

    atualizarConteudos();

    temas.forEach(tema => {
        tema.addEventListener("change", atualizarConteudos);
    });
});
