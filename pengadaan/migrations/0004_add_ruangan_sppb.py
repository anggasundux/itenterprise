from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pengadaan', '0003_remove_sppb_vendor_sppb_unit'),
        ('lokasi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sppb',
            name='ruangan',
            field=models.ForeignKey(
                to='lokasi.ruangan',
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                blank=True,
            ),
        ),
    ]
