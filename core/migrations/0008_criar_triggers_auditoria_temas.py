
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_merge_20261124_1005"),
    ]

    operations = [

        # Cadastro de tema
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_tema_insert
                AFTER INSERT ON core_tema
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
                            SELECT professor_id
                            FROM core_disciplina
                            WHERE id = NEW.disciplina_id
                        ),
                        'core_tema',
                        NEW.id,
                        'INSERT',
                        NULL,
                        json_object(
                            'id', NEW.id,
                            'disciplina_id', NEW.disciplina_id,
                            'nome', NEW.nome
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_tema_insert;",
        ),

        # Atualização de tema
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_tema_update
                AFTER UPDATE ON core_tema
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
                            SELECT professor_id
                            FROM core_disciplina
                            WHERE id = NEW.disciplina_id
                        ),
                        'core_tema',
                        NEW.id,
                        'UPDATE',
                        json_object(
                            'id', OLD.id,
                            'disciplina_id', OLD.disciplina_id,
                            'nome', OLD.nome
                        ),
                        json_object(
                            'id', NEW.id,
                            'disciplina_id', NEW.disciplina_id,
                            'nome', NEW.nome
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_tema_update;",
        ),

        # Exclusão de tema
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_tema_delete
                AFTER DELETE ON core_tema
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
                            SELECT professor_id
                            FROM core_disciplina
                            WHERE id = OLD.disciplina_id
                        ),
                        'core_tema',
                        OLD.id,
                        'DELETE',
                        json_object(
                            'id', OLD.id,
                            'disciplina_id', OLD.disciplina_id,
                            'nome', OLD.nome
                        ),
                        NULL,
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_tema_delete;",
        ),
    ]
