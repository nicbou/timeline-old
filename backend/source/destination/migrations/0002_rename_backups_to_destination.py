import logging

from django.db import migrations, ProgrammingError, connection
from django.apps import apps
from django.db.backends.utils import truncate_name

logger = logging.getLogger(__name__)


def rename_app(app, schema_editor):
    old_app_name = 'backup'
    new_app_name = 'destination'

    schema_editor.execute(
        "SELECT * FROM django_content_type "
        f"where app_label='{new_app_name}'"
    )

    schema_editor.execute(
        f"UPDATE django_content_type SET app_label='{new_app_name}' "
        f"WHERE app_label='{old_app_name}'"
    )
    schema_editor.execute(
        f"UPDATE django_migrations SET app='{new_app_name}' "
        f"WHERE app='{old_app_name}'"
    )
    models = apps.all_models[new_app_name]
    models.update(apps.all_models[old_app_name])
    with connection.cursor() as cursor:
        for model_name in models:
            old_table_name = truncate_name(f"{old_app_name}_{model_name}", connection.ops.max_name_length())
            new_table_name = truncate_name(f"{new_app_name}_{model_name}", connection.ops.max_name_length())
            cursor.execute(f"SELECT * FROM information_schema.tables "
                           f"WHERE table_schema LIKE 'public'"
                           f"AND table_type LIKE 'BASE TABLE' "
                           f"AND table_name = '{old_table_name}'")
            old_table_exists = cursor.fetchone()
            if old_table_exists:
                logger.info(f"Moving old table {old_table_name} to {new_table_name}")
                delete_query = f"DROP TABLE {new_table_name}"
                try:
                    schema_editor.execute(delete_query)
                except ProgrammingError:
                    logger.error('Query failed: "%s"', delete_query, exc_info=True)

                rename_query = f"ALTER TABLE {old_table_name} RENAME TO {new_table_name}"
                try:
                    schema_editor.execute(rename_query)
                except ProgrammingError:
                    logger.error('Query failed: "%s"', rename_query, exc_info=True)
            else:
                logger.warning(f"Did not find old table {old_table_name}. "
                               f"If you are starting this project for the first time, this is fine. "
                               f"If you are updating the app, something went wrong when renaming tables.")


class Migration(migrations.Migration):
    # Commits 620b36 and c83309 split the /backup app into /source and /destination apps. This migrates the old tables.

    dependencies = [
        ('destination', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_app),
    ]
