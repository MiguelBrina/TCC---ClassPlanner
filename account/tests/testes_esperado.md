# APP: CONTA (`account`)
1. test_professor.py
- [x] Testar a criação automática do perfil Professor vinculado ao User.
- [x] Testar a exibição do nome pelo __str__.
- [ ] Testar os fallbacks de nome de exibição, primeiro nome e e-mail.
- [x] Testar se salvar novamente o User evita perfis duplicados.
- [x] Testar a regra de negócio de não criar perfil Professor para superusuários.
- [ ] Testar a exclusão em cascata do perfil quando o User é excluído.
2. test_disponibilidade.py
- [ ] Criar disponibilidade para um professor em um dia e horário específicos.
- [ ] Testar bloqueio de disponibilidade duplicada (UniqueConstraint).
- [ ] Testar ordenação por dia da semana e horário.
- [ ] Testar a remoção das disponibilidades com a exclusão do professor.
- [ ] Testar as validações de dia e horário nos formulários correspondentes.
3. test_cadastro.py — 7 testes passando
- [x] Testar carregamento da página de cadastro.
- [x] Testar cadastro válido e criação da conta User.
- [x] Testar salvamento do nome informado.
- [x] Testar criação e vínculo do perfil Professor.
- [x] Testar rejeição de e-mail inválido.
- [x] Testar rejeição de e-mail duplicado sem criar outro User ou Professor.
- [x] Testar senhas diferentes.
- [x] Testar senha que não atende aos validadores configurados.
- [x] Testar cadastro sem nome.
- [x] Testar que cadastro inválido não cria usuário ou perfil Professor incompleto.
- [x] Verificar que o cadastro não inicia uma sessão autenticada antes da confirmação do e-mail.
Estado atual: os 7 testes implementados em test_cadastro.py passaram. Alguns testes cobrem mais de um comportamento listado acima.
4. test_login.py — 2 testes passando
- [x] Testar carregamento da página de login personalizada.
- [ ] Testar autenticação com credenciais válidas.
- [ ] Testar login usando e-mail.
- [x] Testar rejeição de senha incorreta.
- [ ] Testar rejeição de usuário inexistente.
- [ ] Testar redirecionamento depois do login bem-sucedido.
- [x] Testar que a tentativa com senha incorreta devolve erros no formulário e não autentica o usuário.
Estado atual: passaram o teste de carregamento da tela e o teste de senha incorreta. A fixture google_social_app cria uma SocialApp fictícia no banco de testes para que o template renderize o botão Google; isso não significa que o fluxo completo de autenticação Google já esteja testado.
5. test_sessao.py
- [ ] Testar persistência da sessão entre requisições depois do login.
- [ ] Testar encerramento da sessão no logout.
- [ ] Testar bloqueio de páginas protegidas após o logout.
- [ ] Testar redirecionamento de usuários anônimos.
- [ ] Testar isolamento entre sessões e dados de usuários diferentes.
6. test_recuperacao_senha.py
- [ ] Testar carregamento da tela de recuperação.
- [ ] Testar envio do e-mail de recuperação.
- [ ] Testar redefinição usando um link válido.
- [ ] Testar token inválido ou expirado.
- [ ] Testar resposta para e-mails inexistentes sem revelar desnecessariamente a existência da conta.
7. test_google_auth.py
- [ ] Testar acesso ao fluxo de login Google.
- [ ] Testar inicialização com o provedor configurado.
- [ ] Testar associação entre conta social e conta local.
- [ ] Testar ausência de perfis Professor duplicados.
- [ ] Testar tratamento de falhas no fluxo de autenticação social.
8. test_configuracao_agenda.py
- [ ] Testar exigência de autenticação na configuração inicial.
- [ ] Testar redirecionamento inicial quando a agenda não está configurada.
- [ ] Testar gravação dos dias e horários selecionados.
- [ ] Testar atualização do nome de exibição e agenda_configurada.
- [ ] Testar edição e substituição das disponibilidades existentes.
- [ ] Testar que dados inválidos não alteram parcialmente a agenda.
- [ ] Testar o redirecionamento de pós-login conforme o estado da agenda.
9. test_exclusao_conta.py
- [ ] Testar exigência de autenticação.
- [ ] Testar que nome de confirmação incorreto não exclui a conta.
- [ ] Testar exclusão após confirmação correta.
- [ ] Testar remoção dos registros relacionados conforme as regras do banco.
- [ ] Testar logout e redirecionamento após exclusão.
10. test_csrf.py — etapa posterior, com o Edu
- [ ] Testar formulários protegidos com token válido.
- [ ] Testar rejeição de POST sem token.
- [ ] Testar rejeição de origens não confiáveis.
- [ ] Testar os casos legítimos de origem HTTPS do Codespace e ambiente local.
- [ ] Testar a página personalizada de falha CSRF sem desativar a proteção global.