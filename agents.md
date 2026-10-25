
fitur khusus ketika masuk mode lock fullscreen :
1. tidak bisa scroll
2. tidak bisa zoom gambar
3. wakelock aktif
4. layar full screen
5. tidak bisa keluar/kembali dari mode fullscreen selain tombol unlock


fitur yang sudah bisa dan jangan dirubah :
1. search bar ketika ngetik karakter langsung muncul tanpa pencet enter
2. grid view card
3. theme toggle
4. pagination
5. footer
6. modal gambar karakter dan deskripsinya
7. mode tombol lock fullscreen untuk mengunci fitur khusus dan tombol unlock fullscreen untuk melepas kunci fitur khusus
8. wakelock
9. tombol close modal gambar karakter yang ada deskripsinya
10. ketika klik tombol unlock fullscreen maka akan kembali ke modal gambar karakter dan deskripsinya yang tadi dipencet 
11. android back button sudah terkunci/tertahan ketika sudah masuk ke mode fullscreen
12. tombol bulat floating filter arc di halaman utama (style mobile-sidebar.js) untuk memfilter karakter berdasarkan story arc

Yang udah bener error nya :
1. pas di search bar ketika ngetik itu harus nya ketika klik apapun itu kan kelepas dari search bar nya (typing gw maksudnya) nahh ini bug nya terus munculin keyboard bro karena sedang ngetik mau itu setelah klik tombol unlock view full screen masih tetep munculin keyboard njir..
2. Nama karakter di mode Lock Fullscreen malah hilang setelah update APK.
3. logic tipe haki hanya muncul none untuk yang punya tipe haki jenis tertentu contohnya luffy dia memiliki 3 tipe haki tapi di aplikasi dia hanya muncul none pada saat mode popup gambar karakter
4. AttributeError: BLACK26 pada Flet diperbaiki ke ft.Colors.BLACK_26 dan ft.Colors.BLACK_12.



catatan keras ke 1 : jangan git add, commit dan push tanpa disuruh.
pengembangan aplikasi masih jauh...

Catatan Keras ke 2 : jangan ubah kode apapun yang sudah benar.

Yang masih error :
- (Belum ada dan jangan sampe ada)

Yang ingin dibuat fitur baru :
- Buat tampilan suggest di kanan story arc dengan masing - masing memiliki kotak chip terpisah dengan border dan background aksen sendiri.
- Munculkan satu per satu suggest saat diklik.
- kondisi awal : sudah ada kotak/border default (semua arc).
- buatkan tombol hapus cepat contoh: [Baratie X] dan tombol hapus cepat ini hapus satu per satu suggest.
- Tambah fitur clear di kiri closebar jangan terlalu deket atau terlalu jauh.
- tombolnya berupa icon putaran reset.
- dan fungsi tombol clear ini untuk clear suggest.

tambahan fitur baru
- di bagian filter tambahkan kategori Game Mode yang berisi 3 game mode.
- easy, medium, hard.
- gw pengen mengelompkan sesuai entry journey bro jika si karakter muncul misal  di 6-40 kemunculan masuk ke easy, jika si karater muncul di 2-5 kemunculan masuk ke medium, jika si karakter muncul di 1 kemunculan masuk ke hard.

perbaikan
- bagian kategori sama persiskan ukurannya dengan suggest agar terlihat rapih.

tambahan fitur baru bagian 2 :
- dropdown filter di modal karakter tolong ubah background nya bro sesuai background tema (ubah juga warna border nya) dan kasih jarak 2px biar keliatan kaya ngambang hehee