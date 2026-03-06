from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from pengadaan.models import Vendor, SPPB, DetailSPPB
from django.core.files.uploadedfile import SimpleUploadedFile
from lokasi.models import Ruangan, Unit, Gedung
from jaringan.models import PerangkatJaringan
from inventaris.models import Aset
from datetime import date


class PengadaanTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', password='pass')
        self.client.login(username='tester', password='pass')
        # make required related objects
        self.gedung = Gedung.objects.create(nama='Gedung 1')
        self.ruangan = Ruangan.objects.create(gedung=self.gedung, nama='Ruangan 1')
        self.unit = Unit.objects.create(nama='Unit 1')

    def test_vendor_crud(self):
        # create
        url = reverse('pengadaan:create_vendor')
        resp = self.client.post(url, {'nama': 'Vendor A', 'kontak': '0812', 'email': 'a@b.com', 'alamat': 'Jl'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Vendor.objects.filter(nama='Vendor A').exists())
        vendor = Vendor.objects.get(nama='Vendor A')
        # edit
        edit_url = reverse('pengadaan:edit_vendor', args=[vendor.pk])
        resp = self.client.post(edit_url, {'nama': 'Vendor A2', 'kontak': '0813', 'email': 'a2@b.com', 'alamat': 'Jl 2'})
        self.assertEqual(resp.status_code, 302)
        vendor.refresh_from_db()
        self.assertEqual(vendor.nama, 'Vendor A2')
        # delete
        del_url = reverse('pengadaan:delete_vendor', args=[vendor.pk])
        resp = self.client.get(del_url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Vendor.objects.filter(pk=vendor.pk).exists())

    def test_sppb_flow_and_asset_creation(self):
        # create sppb
        url = reverse('pengadaan:create_sppb')
        # SPPB file is required; supply dummy upload
        dummy = SimpleUploadedFile('dummy.pdf', b'PDFDATA', content_type='application/pdf')
        data = {
            'nomor_sppb': 'SPPB1',
            'tanggal_sppb': '2026-03-01',
            'ruangan': self.ruangan.pk,
            'unit': self.unit.pk,
            'keterangan': 'test',
        }
        resp = self.client.post(url, data, files={'file_sppb': dummy})
        self.assertEqual(resp.status_code, 302)
        sppb = SPPB.objects.get(nomor_sppb='SPPB1')
        # add detail
        add_url = reverse('pengadaan:add_detail_barang', args=[sppb.pk])
        resp = self.client.post(add_url, {'nama_barang': 'Item1', 'spesifikasi': '', 'jumlah': 2, 'satuan': 'Unit', 'harga_satuan': '1000'})
        self.assertEqual(resp.status_code, 302)
        detail = sppb.detail_barang.first()
        self.assertEqual(detail.nama_barang, 'Item1')
        # update status to masuk_inventaris and ensure asset created
        status_url = reverse('pengadaan:update_status', args=[sppb.pk])
        resp = self.client.post(status_url, {'status': 'masuk_inventaris', 'tanggal_datang': '', 'tanggal_verifikasi': '', 'catatan': ''})
        self.assertEqual(resp.status_code, 302)
        detail.refresh_from_db()
        self.assertIsNotNone(detail.aset_inventaris)
        aset = detail.aset_inventaris
        self.assertEqual(aset.nama_aset, 'Item1')
        # verify asset kode contains sppb number
        self.assertIn('SPPB1', aset.kode_aset)
