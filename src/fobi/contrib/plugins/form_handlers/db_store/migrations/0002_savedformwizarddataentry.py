# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-15 23:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fobi', '0010_formwizardhandler'),
        ('fobi_contrib_plugins_form_handlers_db_store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedFormWizardDataEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_data_headers', models.TextField(blank=True, null=True, verbose_name='Form data headers')),
                ('saved_data', models.TextField(blank=True, null=True, verbose_name='Plugin data')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('form_wizard_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fobi.FormWizardEntry', verbose_name='Form')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
                'db_table': 'db_store_savedformwizarddataentry',
                'verbose_name': 'Saved form wizard data entry',
                'verbose_name_plural': 'Saved form wizard data entries',
            },
        ),
    ]