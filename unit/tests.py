from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from lokasi.models import Ruangan
from jaringan.models import PerangkatJaringan
from inventaris.models import Aset
from .models import UnitKomputer


class UnitViewTests(TestCase):
    def setUp(self):
        # create a test user and log in
        self.user = User.objects.create_user('tester', password='pass')
        self.client.login(username='tester', password='pass')

        # create related objects (Gedung required for Ruangan)
        from lokasi.models import Gedung
        gedung = Gedung.objects.create(nama='Gedung A')
        self.ruangan = Ruangan.objects.create(gedung=gedung, nama='Lab')
        self.perangkat = PerangkatJaringan.objects.create(
            nama='Switch1',
            jenis='switch',
            ip_address='192.168.100.1',
            status='aktif'
        )
        self.aset = Aset.objects.create(
            kode_aset='CPU001',
            nama_aset='CPU i5',
            kategori='CPU',
            kondisi='baik',
            tanggal_beli='2023-01-01'
        )

    def test_add_and_list_unit(self):
        url = reverse('unit_add')
        resp = self.client.post(url, {
            'nama_unit': 'Unit A',
            'ip_address': '192.168.1.10',
            'status': 'aktif',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(UnitKomputer.objects.filter(nama_unit='Unit A').exists())

        list_url = reverse('unit_list')
        resp = self.client.get(list_url)
        self.assertContains(resp, 'Unit A')

    def test_duplicate_ip_prevention(self):
        UnitKomputer.objects.create(
            nama_unit='Existing',
            ip_address='192.168.1.20',
            status='aktif',
        )
        url = reverse('unit_add')
        resp = self.client.post(url, {
            'nama_unit': 'New',
            'ip_address': '192.168.1.20',
            'status': 'aktif',
        })
        self.assertContains(resp, 'IP Address sudah digunakan')

    def test_edit_unit(self):
        unit = UnitKomputer.objects.create(
            nama_unit='ToEdit',
            ip_address='10.0.0.1',
            status='aktif',
        )
        url = reverse('unit_edit', args=[unit.id])
        resp = self.client.post(url, {
            'nama_unit': 'Edited',
            'ip_address': '10.0.0.1',
            'status': 'rusak',
        })
        self.assertEqual(resp.status_code, 302)
        unit.refresh_from_db()
        self.assertEqual(unit.nama_unit, 'Edited')
        self.assertEqual(unit.status, 'rusak')

    def test_delete_unit(self):
        unit = UnitKomputer.objects.create(
            nama_unit='ToDelete',
            ip_address='10.0.0.2',
            status='aktif',
        )
        url = reverse('unit_delete', args=[unit.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(UnitKomputer.objects.filter(id=unit.id).exists())

    def test_list_search_and_filter(self):
        UnitKomputer.objects.create(nama_unit='Alpha', ip_address='1.2.3.4', status='aktif')
        UnitKomputer.objects.create(nama_unit='Beta', ip_address='5.6.7.8', status='rusak')
        list_url = reverse('unit_list')
        resp = self.client.get(list_url, {'q': 'Alpha'})
        self.assertContains(resp, 'Alpha')
        self.assertNotContains(resp, 'Beta')

        resp = self.client.get(list_url, {'status': 'rusak'})
        self.assertContains(resp, 'Beta')
        self.assertNotContains(resp, 'Alpha')
