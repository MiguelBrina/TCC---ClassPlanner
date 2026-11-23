from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_criar_triggers_auditoria_alunos"),
    ]

    operations = [

        # Cadastro de disciplina
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_disciplina_insert
                AFTER INSERT ON core_disciplina
                BEGIN
                    INSERT INTO core_auditoria (
                        professor_id,
                        tabela,
                        registro_id,
                        operacao,
                        dados_anteriores,
                        dados_novos,
                        data_hora
                    )
                    VALUES (
                        NEW.professor_id,
                        'core_disciplina',
                        NEW.id,
                        'INSERT',
                        NULL,
                        json_object(
                            'id', NEW.id,
                            'professor_id', NEW.professor_id,
                            'nome', NEW.nome,
                            'cor', NEW.cor
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_disciplina_insert;",
        ),

        # Atualização de disciplina
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_disciplina_update
                AFTER UPDATE ON core_disciplina
                BEGIN
                    INSERT INTO core_auditoria (
                        professor_id,
                        tabela,
                        registro_id,
                        operacao,
                        dados_anteriores,
                        dados_novos,
                        data_hora
                    )
                    VALUES (
                        NEW.professor_id,
                        'core_disciplina',
                        NEW.id,
                        'UPDATE',
                        json_object(
                            'id', OLD.id,
                            'professor_id', OLD.professor_id,
                            'nome', OLD.nome,
                            'cor', OLD.cor
                        ),
                        json_object(
                            'id', NEW.id,
                            'professor_id', NEW.professor_id,
                            'nome', NEW.nome,
                            'cor', NEW.cor
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_disciplina_update;",
        ),

        # Exclusão de disciplina
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_disciplina_delete
                AFTER DELETE ON core_disciplina
                BEGIN
                    INSERT INTO core_auditoria (
                        professor_id,
                        tabela,
                        registro_id,
                        operacao,
                        dados_anteriores,
                        dados_novos,
                        data_hora
                    )
                    VALUES (
                        OLD.professor_id,
                        'core_disciplina',
                        OLD.id,
                        'DELETE',
                        json_object(
                            'id', OLD.id,
                            'professor_id', OLD.professor_id,
                            'nome', OLD.nome,
                            'cor', OLD.cor
                        ),
                        NULL,
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_disciplina_delete;",
        ),
    ]