
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_criar_triggers_auditoria_conteudos"),
    ]

    operations = [

        # Trigger: cadastro de matrícula
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_matricula_insert
                AFTER INSERT ON core_matricula
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
                        'core_matricula',
                        NEW.id,
                        'INSERT',
                        NULL,
                        json_object(
                            'id', NEW.id,
                            'aluno_id', NEW.aluno_id,
                            'disciplina_id', NEW.disciplina_id,
                            'data_inicio', NEW.data_inicio
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_matricula_insert;"
        ),

        # Trigger: atualização de matrícula
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_matricula_update
                AFTER UPDATE ON core_matricula
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
                        'core_matricula',
                        NEW.id,
                        'UPDATE',
                        json_object(
                            'id', OLD.id,
                            'aluno_id', OLD.aluno_id,
                            'disciplina_id', OLD.disciplina_id,
                            'data_inicio', OLD.data_inicio
                        ),
                        json_object(
                            'id', NEW.id,
                            'aluno_id', NEW.aluno_id,
                            'disciplina_id', NEW.disciplina_id,
                            'data_inicio', NEW.data_inicio
                        ),
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_matricula_update;"
        ),

        # Trigger: exclusão de matrícula
        migrations.RunSQL(
            sql="""
                CREATE TRIGGER auditoria_matricula_delete
                AFTER DELETE ON core_matricula
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
                        'core_matricula',
                        OLD.id,
                        'DELETE',
                        json_object(
                            'id', OLD.id,
                            'aluno_id', OLD.aluno_id,
                            'disciplina_id', OLD.disciplina_id,
                            'data_inicio', OLD.data_inicio
                        ),
                        NULL,
                        strftime('%Y-%m-%d %H:%M:%f', 'now')
                    );
                END;
            """,
            reverse_sql="DROP TRIGGER IF EXISTS auditoria_matricula_delete;"
        ),
    ]
