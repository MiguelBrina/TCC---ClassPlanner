
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_criar_triggers_auditoria_temas"),
    ]

    operations = [

        # Trigger: cadastro de conteúdo
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_conteudo_insert
                AFTER INSERT ON core_conteudo
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
                        (
                            SELECT d.professor_id
                            FROM core_tema t
                            JOIN core_disciplina d ON d.id = t.disciplina_id
                            WHERE t.id = NEW.tema_id
                        ),
                        'core_conteudo',
                        NEW.id,
                        'INSERT',
                        NULL,
                        json_object(
                            'id', NEW.id,
                            'tema_id', NEW.tema_id,
                            'nome', NEW.nome
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_conteudo_insert;"
        ),

        # Trigger: atualização de conteúdo
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_conteudo_update
                AFTER UPDATE ON core_conteudo
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
                        (
                            SELECT d.professor_id
                            FROM core_tema t
                            JOIN core_disciplina d ON d.id = t.disciplina_id
                            WHERE t.id = NEW.tema_id
                        ),
                        'core_conteudo',
                        NEW.id,
                        'UPDATE',
                        json_object(
                            'id', OLD.id,
                            'tema_id', OLD.tema_id,
                            'nome', OLD.nome
                        ),
                        json_object(
                            'id', NEW.id,
                            'tema_id', NEW.tema_id,
                            'nome', NEW.nome
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_conteudo_update;"
        ),

        # Trigger: exclusão de conteúdo
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_conteudo_delete
                AFTER DELETE ON core_conteudo
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
                        (
                            SELECT d.professor_id
                            FROM core_tema t
                            JOIN core_disciplina d ON d.id = t.disciplina_id
                            WHERE t.id = OLD.tema_id
                        ),
                        'core_conteudo',
                        OLD.id,
                        'DELETE',
                        json_object(
                            'id', OLD.id,
                            'tema_id', OLD.tema_id,
                            'nome', OLD.nome
                        ),
                        NULL,
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_conteudo_delete;"
        ),
    ]
