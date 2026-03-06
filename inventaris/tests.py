from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from .models import Aset, MutasiAset
from lokasi.models import Ruangan, Gedung


class AsetModelTest(TestCase):
    def setUp(self):
        self.gedung = Gedung.objects.create(nama="Gedung A")
        self.ruangan = Ruangan.objects.create(gedung=self.gedung, nama="Ruang IT")

    def test_create_aset(self):
        """Test creating an asset"""
        aset = Aset.objects.create(
            kode_aset="AST001",
            nama_aset="Laptop",
            kategori="Elektronik",
            merek="Dell",
            nomor_seri="SN123456",
            ruangan=self.ruangan,
            kondisi="Baik",
            tanggal_beli=date.today()
        )
        self.assertEqual(aset.kode_aset, "AST001")
        self.assertEqual(aset.nama_aset, "Laptop")
        self.assertEqual(str(aset), "AST001 - Laptop")

    def test_aset_unique_kode(self):
        """Test that kode_aset is unique"""
        Aset.objects.create(
            kode_aset="AST001",
            nama_aset="Laptop",
            kategori="Elektronik",
            ruangan=self.ruangan,
            kondisi="Baik",
            tanggal_beli=date.today()
        )
        with self.assertRaises(Exception):
            Aset.objects.create(
                kode_aset="AST001",
                nama_aset="Monitor",
                kategori="Elektronik",
                ruangan=self.ruangan,
                kondisi="Baik",
                tanggal_beli=date.today()
            )


class MutasiAsetModelTest(TestCase):
    def setUp(self):
        self.gedung = Gedung.objects.create(nama="Gedung A")
        self.ruangan1 = Ruangan.objects.create(gedung=self.gedung, nama="Ruang IT")
        self.ruangan2 = Ruangan.objects.create(gedung=self.gedung, nama="Ruang HRD")
        self.aset = Aset.objects.create(
            kode_aset="AST001",
            nama_aset="Laptop",
            kategori="Elektronik",
            ruangan=self.ruangan1,
            kondisi="Baik",
            tanggal_beli=date.today()
        )

    def test_create_mutasi(self):
        """Test creating asset mutation"""
        mutasi = MutasiAset.objects.create(
            aset=self.aset,
            dari_ruangan=self.ruangan1,
            ke_ruangan=self.ruangan2
        )
        self.assertEqual(mutasi.aset, self.aset)
        self.assertEqual(mutasi.dari_ruangan, self.ruangan1)
        self.assertEqual(mutasi.ke_ruangan, self.ruangan2)


class InventarisViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.gedung = Gedung.objects.create(nama="Gedung A")
        self.ruangan = Ruangan.objects.create(gedung=self.gedung, nama="Ruang IT")
        self.aset = Aset.objects.create(
            kode_aset="AST001",
            nama_aset="Laptop",
            kategori="Elektronik",
            merek="Dell",
            nomor_seri="SN123456",
            ruangan=self.ruangan,
            kondisi="Baik",
            tanggal_beli=date.today()
        )

    def test_list_view_requires_login(self):
        """Test that list view requires login"""
        response = self.client.get(reverse('inventaris_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_list_view_authenticated(self):
        """Test list view for authenticated user"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('inventaris_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AST001')

    def test_list_view_search(self):
        """Test search functionality in list view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('inventaris_list'), {'search': 'Laptop'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')

    def test_list_view_filter_ruangan(self):
        """Test filter by ruangan"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('inventaris_list'), {'ruangan': self.ruangan.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AST001')

    def test_list_view_filter_kondisi(self):
        """Test filter by kondisi"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('inventaris_list'), {'kondisi': 'Baik'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AST001')

    def test_add_view_get(self):
        """Test GET request to add view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('inventaris_add'))
        self.assertEqual(response.status_code, 200)

    def test_add_view_post(self):
        """Test POST request to add new asset"""
        self.client.login(username='testuser', password='testpass')
        data = {
            'kode_aset': 'AST002',
            'nama_aset': 'Monitor',
            'kategori': 'Elektronik',
            'merek': 'LG',
            'nomor_seri': 'M456789',
            'ruangan': self.ruangan.id,
            'kondisi': 'Baik',
            'tanggal_beli': date.today().isoformat(),
            'keterangan': 'Monitor baru'
        }
        response = self.client.post(reverse('inventaris_add'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Aset.objects.filter(kode_aset='AST002').exists())

    def test_edit_view_get(self):
        """Test GET request to edit view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('inventaris_edit', args=[self.aset.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AST001')

    def test_edit_view_post(self):
        """Test POST request to edit asset"""
        self.client.login(username='testuser', password='testpass')
        data = {
            'kode_aset': 'AST001',
            'nama_aset': 'Laptop Updated',
            'kategori': 'Elektronik',
            'merek': 'Dell',
            'nomor_seri': 'SN123456',
            'ruangan': self.ruangan.id,
            'kondisi': 'Rusak',
            'tanggal_beli': date.today().isoformat(),
            'keterangan': 'Laptop rusak'
        }
        response = self.client.post(reverse('inventaris_edit', args=[self.aset.id]), data)
        self.assertEqual(response.status_code, 302)
        updated_aset = Aset.objects.get(id=self.aset.id)
        self.assertEqual(updated_aset.kondisi, 'Rusak')

    def test_delete_view(self):
        """Test delete asset"""
        self.client.login(username='testuser', password='testpass')
        aset_id = self.aset.id
        response = self.client.get(reverse('inventaris_delete', args=[aset_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Aset.objects.filter(id=aset_id).exists())

    def test_detail_view(self):
        """Test asset detail view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('aset_detail', args=['AST001']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AST001')

    def test_mutasi_aset_view(self):
        """Test asset mutation view"""
        self.client.login(username='testuser', password='testpass')
        ruangan2 = Ruangan.objects.create(gedung=self.gedung, nama="Ruang HRD")
        
        data = {'ke_ruangan': ruangan2.id}
        response = self.client.post(reverse('mutasi_aset', args=[self.aset.id]), data)
        self.assertEqual(response.status_code, 302)
        
        # Check that ruangan was updated
        updated_aset = Aset.objects.get(id=self.aset.id)
        self.assertEqual(updated_aset.ruangan, ruangan2)
        
        # Check that mutasi record was created
        self.assertTrue(MutasiAset.objects.filter(aset=self.aset).exists())

    def test_cetak_barcode_view(self):
        """Test print barcode view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('cetak_barcode', args=[self.aset.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AST001')

    def test_pdf_inventaris_view(self):
        """Test export PDF inventaris"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('pdf_inventaris'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_rekap_ruangan_view(self):
        """Test room summary view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('rekap_ruangan'))
        self.assertEqual(response.status_code, 200)

    def test_grafik_dashboard_view(self):
        """Test dashboard graphics view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('grafik_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_mutasi_list_view(self):
        """Test mutation list view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('mutasi_list'))
        self.assertEqual(response.status_code, 200)

    def test_mutasi_list_view_with_date_filter(self):
        """Test mutation list with date filter"""
        self.client.login(username='testuser', password='testpass')
        start = (date.today() - timedelta(days=30)).isoformat()
        end = date.today().isoformat()
        response = self.client.get(reverse('mutasi_list'), {'start': start, 'end': end})
        self.assertEqual(response.status_code, 200)

    def test_rekap_mutasi_bulanan_view(self):
        """Test monthly mutation summary view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('rekap_mutasi_bulanan'))
        self.assertEqual(response.status_code, 200)

    def test_aset_rusak_view(self):
        """Test damaged assets view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('aset_rusak'))
        self.assertEqual(response.status_code, 200)

