from django.db import migrations, models
import django.db.models.deletion


def copy_category_data(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    # Use raw SQL to copy from old join table
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT product_id, category_id FROM product_categories")
        rows = cursor.fetchall()
    # assign first category found for each product
    product_to_category = {}
    for prod_id, cat_id in rows:
        if prod_id not in product_to_category:
            product_to_category[prod_id] = cat_id
    for prod_id, cat_id in product_to_category.items():
        try:
            product = Product.objects.get(pk=prod_id)
            product.category_id = cat_id
            product.save(update_fields=['category_id'])
        except Product.DoesNotExist:
            pass


def noop_reverse(apps, schema_editor):
    # nothing to do on reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                to='products.Category',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                null=True,
            ),
        ),
        migrations.RunPython(copy_category_data, noop_reverse),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                to='products.Category',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                null=False,
            ),
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS product_categories;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
