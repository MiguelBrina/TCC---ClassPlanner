document.addEventListener("DOMContentLoaded", () => {

    document
        .querySelectorAll("[data-password-toggle]")
        .forEach(botao => {

            const input = document.getElementById(
                botao.dataset.passwordToggle
            );

            if (!input) {
                return;
            }

            const olhoAberto =
                botao.querySelector("[data-eye-open]");

            const olhoFechado =
                botao.querySelector("[data-eye-closed]");


            botao.addEventListener("click", () => {

                const senhaOculta =
                    input.type === "password";


                input.type = senhaOculta
                    ? "text"
                    : "password";


                if (olhoAberto) {
                    olhoAberto.hidden = !senhaOculta;
                }

                if (olhoFechado) {
                    olhoFechado.hidden = senhaOculta;
                }


                botao.setAttribute(
                    "aria-label",
                    senhaOculta
                        ? "Ocultar senha"
                        : "Mostrar senha"
                );

                botao.setAttribute(
                    "aria-pressed",
                    senhaOculta
                        ? "true"
                        : "false"
                );

            });

        });

});