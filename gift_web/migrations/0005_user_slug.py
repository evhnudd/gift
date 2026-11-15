"""Добавление слага пользователю: поле -> заполнение -> ограничения.

Слаг добавляется в три шага, так как у существующих записей
значения ещё нет, а итоговое поле должно быть уникальным и обязательным.
"""

from django.db import migrations, models

from gift_web.slugs import make_slug


def fill_slugs(apps, schema_editor):
    User = apps.get_model("gift_web", "User")
    taken: set[str] = set()
    for user in User.objects.order_by("id"):
        user.slug = make_slug(user.name, taken)
        taken.add(user.slug)
        user.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("gift_web", "0004_remove_gift_is_purchased"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="slug",
            field=models.SlugField(
                "слаг", max_length=60, null=True, editable=False
            ),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="slug",
            field=models.SlugField(
                "слаг",
                max_length=60,
                unique=True,
                help_text="Часть адреса страницы получателя, например anna.",
            ),
        ),
    ]
