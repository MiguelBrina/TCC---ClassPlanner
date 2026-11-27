
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_criar_triggers_auditoria_matriculas"),
    ]

    operations = [

        # Trigger: cadastro de diário de bordo
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_diariodebordo_insert
                AFTER INSERT ON core_diariodebordo
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
                            FROM core_matricula m
                            JOIN core_disciplina d
                                ON d.id = m.disciplina_id
                            WHERE m.id = NEW.matricula_id
                        ),
                        'core_diariodebordo',
                        NEW.id,
                        'INSERT',
                        NULL,
                        json_object(
                            'id', NEW.id,
                            'matricula_id', NEW.matricula_id
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS auditoria_diariodebordo_insert;
            """
        ),

        # Trigger: atualização de diário de bordo
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_diariodebordo_update
                AFTER UPDATE ON core_diariodebordo
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
                            FROM core_matricula m
                            JOIN core_disciplina d
                                ON d.id = m.disciplina_id
                            WHERE m.id = NEW.matricula_id
                        ),
                        'core_diariodebordo',
                        NEW.id,
                        'UPDATE',
                        json_object(
                            'id', OLD.id,
                            'matricula_id', OLD.matricula_id
                        ),
                        json_object(
                            'id', NEW.id,
                            'matricula_id', NEW.matricula_id
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS auditoria_diariodebordo_update;
            """
        ),

        # Trigger: exclusão de diário de bordo
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_diariodebordo_delete
                AFTER DELETE ON core_diariodebordo
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
                            FROM core_matricula m
                            JOIN core_disciplina d
                                ON d.id = m.disciplina_id
                            WHERE m.id = OLD.matricula_id
                        ),
                        'core_diariodebordo',
                        OLD.id,
                        'DELETE',
                        json_object(
                            'id', OLD.id,
                            'matricula_id', OLD.matricula_id
                        ),
                        NULL,
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS auditoria_diariodebordo_delete;
            """
        ),
    ]
