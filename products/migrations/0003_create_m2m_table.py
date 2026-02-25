from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_remove_product_category_product_categories"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS product_categories (
                product_id bigint NOT NULL,
                category_id bigint NOT NULL,
                PRIMARY KEY (product_id, category_id),
                CONSTRAINT product_categories_product_id_fk FOREIGN KEY (product_id) REFERENCES product (id) ON DELETE CASCADE,
                CONSTRAINT product_categories_category_id_fk FOREIGN KEY (category_id) REFERENCES product_category (id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS product_categories;
            """,
        ),
    ]
