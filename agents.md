<!-- bro.. gw pengen migrasi in ini menjadi aplikasi android tapi yg simpel aja ga usah pake framework kalo bisa mah kaya flutter dll
bisa gak pake python doang ? klw datanya mah sama in weh dari api -->

Tulis langkah nya... :

Karena kode kamu menggunakan **Flet**, sebenarnya Flet ini di belakang layar menggunakan mesin Flutter. Namun, kamu **tidak perlu ngoding Flutter/Dart sama sekali** (cukup pakai Python ini saja).

Untuk membuat file `.apk` (Android) tanpa harus install Flutter dan Android Studio yang berat di laptopmu, cara paling mudah adalah menggunakan **GitHub Actions** (Build Online). Tapi jika ingin build lokal di laptop, kamu tetap butuh Flutter SDK.

Berikut adalah 2 pilihan cara membuatnya:

### Opsi 1: Build Online via GitHub Actions (Sangat Disarankan, Tanpa Install Framework Berat)
1. Buka terminal/cmd dan buat file `requirements.txt` yang isinya:
   ```text
   flet
   requests
   ```
2. Buat repository baru di GitHub dan upload file `main.py`, folder `assets/`, dan `requirements.txt` ke repo tersebut.
3. Di dalam repository GitHub, buat file baru dengan path `.github/workflows/build.yml`.
4. Isi file `build.yml` dengan script build APK otomatis dari Flet (kamu bisa cari "Flet GitHub Actions CI" di dokumentasi resmi Flet).
5. Commit dan Push. Buka tab **Actions** di GitHub, tunggu proses build berjalan (sekitar 10-15 menit).
6. Setelah selesai, file `.apk` bisa langsung didownload di bagian *Artifacts* pada halaman build tersebut.

### Opsi 2: Build Lokal di PC (Butuh Install Flutter & Android Studio)
1. Install **Flutter SDK** dan **Android Studio** (hanya untuk mendapatkan Android SDK & toolchain).
2. Jalankan perintah `flutter doctor` di terminal untuk memastikan tidak ada error pada setup Android.
3. Buka terminal di folder project kamu (tempat `main.py` berada).
4. Jalankan perintah build Flet: 
   ```bash
   flet build apk
   ```
5. Tunggu proses build selesai. Flet akan otomatis mendownload template dan membuatkan APK.
6. Hasil `.apk` akan muncul di dalam folder `build/apk/`.

**Kesimpulan:** 
Kamu tetap bisa full ngoding Python 100% menggunakan API persis seperti kodemu saat ini. Untuk mendapatkan APK tanpa perlu install framework Flutter di PC lokalmu, **Opsi 1** adalah jalan pintas terbaik!