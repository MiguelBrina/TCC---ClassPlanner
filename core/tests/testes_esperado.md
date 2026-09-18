# APP: CORE Testes Esperados
- [x] **3. test_disciplinas.py**
  - [x] Criar disciplina vinculada ao professor logado (POST)
  - [ ] Acessar página de listar disciplinas (GET retorna status 200)

- [ ] **4. test_temas.py**
  - [ ] Criar tema associado a uma disciplina (POST)
  - [ ] Listar temas de uma disciplina específica (GET)

- [ ] **5. test_conteudos.py**
  - [ ] Criar conteúdo associado a um tema (POST)
  - [ ] Listar conteúdos de um tema específico (GET)

- [ ] **6. test_alunos_matriculas.py**
  - [ ] Criar aluno associado ao professor logado
  - [ ] Criar matrícula do aluno em uma disciplina

- [ ] **7. test_diarios_registros.py**
  - [ ] Validar criação do Diário de Bordo (atrelado à Matrícula)
  - [ ] Criar Registro de aula no Diário (com data e observação)
  - [ ] Adicionar Temas e Conteúdos ao Registro (ManyToManyField)

- [ ] **8. test_aulas_agenda.py**
  - [ ] Agendar Aula (relacionando Professor, Aluno, Disciplina, Data e Hora)

- [ ] **9. test_pagamentos.py**
  - [ ] Gerar pagamento pendente para o aluno
  - [ ] Alterar status de pagamento para "pago"