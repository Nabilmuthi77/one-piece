
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

Catatan Keras ke 2 : jangan ubah kode apapun tanpa persetujuan dari saya dan jangan ubah kode apapun yang sudah benar.

Yang masih error :
- (Belum ada dan jangan sampe ada)

Yang ingin dibuat fitur baru :
- (Belum ada)

Yang masih ingin diperbarui :
- (Belum ada yang lain)
- Fitur floating arc filter button disempurnakan:
  1. Bulatan kuning (fab_badge) dihapus total sehingga tampilan tombol bersih, rapi, dan simetris di tengah.
  2. Drag gesture floating ball diperbarui dengan anchored pointer coordinate tracking (posisi tombol terkunci 1:1 mengikuti kursor mouse tanpa jitter/drift/stutter).
  3. Animasi spinner ke-1 (dual-arc swirl @ 40 FPS) dan puzzle ke-2 (3x3 dot matrix sliding @ 30 FPS) berjalan berputar terus menerus sangat halus (liquid smooth) dengan warna biru ACCENT (#0ea5e9). Posisi visual puzzle ke-2 telah digeser ke atas dan ke kiri sehingga simetris dan presisi tepat di tengah disc.
  4. Klik/tap biasa langsung memunculkan dan menutup menu filter arc secara instan dan responsif.