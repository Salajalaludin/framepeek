## Yang harus dibenarkan

### Konsistensi hasil analisis

- [x] 1. Teruskan `correlation_method` dari `profile()` ke analisis target numerik agar bagian `target` dan `correlations` memakai metode yang sama.
- [x] 2. Teruskan `outlier_method` dan `outlier_multiplier` dari `profile()` ke `warnings()` agar bagian `outliers` dan `warnings` konsisten.
- [x] 3. Hindari pemanggilan ulang `correlations()` ketika hasil korelasi sudah dihitung oleh `profile()`.
- [x] 4. Hindari pemanggilan ulang `outliers()` ketika hasil outlier sudah dihitung oleh `profile()`.
- [x] 5. Pastikan seluruh konfigurasi yang diberikan ke `profile()` benar-benar diterapkan pada semua bagian report yang terkait.

### Penamaan dan API internal

- [x] 6. Ganti parameter `target` menjadi `target_column`.
- [x] 7. Hapus alias `_target_summary` setelah konflik penamaan parameter diselesaikan.
8. Pertimbangkan mengganti nama fungsi publik `warnings()` menjadi nama yang lebih spesifik seperti `data_quality_warnings()` atau `quality_warnings()`.
9. Bila nama `warnings()` tetap dipertahankan demi kompatibilitas, siapkan alias baru dan lakukan deprecation secara bertahap.
10. Gunakan penamaan parameter yang konsisten di seluruh fungsi, terutama untuk threshold, ratio, method, multiplier, dan column selection.

### Validasi

- [x] 11. Satukan validasi angka positif, integer non-negatif, persentase, rasio, threshold, dan pilihan metode ke helper internal.
- [x] 12. Samakan format dan isi pesan error di seluruh fungsi.
- [x] 13. Perbaiki error duplicate column agar menyebutkan nama kolom yang duplikat beserta jumlah kemunculannya.
- [x] 14. Validasi tipe boolean secara khusus karena `bool` merupakan subclass dari `int` di Python.
- [x] 15. Validasi nilai numerik non-finite seperti `NaN`, `inf`, dan `-inf` pada parameter konfigurasi.
- [x] 16. Pastikan urutan threshold divalidasi secara konsisten.
- [x] 17. Tambahkan validasi untuk DataFrame dengan MultiIndex column jika belum ingin didukung.
- [x] 18. Bedakan error input pengguna, error kolom tidak ditemukan, dan error konfigurasi internal.

## Yang harus ditambahkan

### Reuse hasil dan internal analysis context

- [x] 19. Tambahkan mekanisme internal untuk menyimpan hasil perhitungan yang sudah dilakukan selama satu pemanggilan `profile()`.
20. Simpan daftar kolom numerik, kategorikal, boolean, datetime, dan tipe lainnya sekali saja.
21. Simpan missing count, unique count, non-null count, dan value counts yang digunakan berulang.
22. Izinkan `warnings()` menerima hasil outlier, target, dan metadata kolom yang sudah dihitung.
- [x] 23. Izinkan analisis target numerik menerima hasil korelasi yang sudah dihitung.
- [x] 24. Pastikan cache hanya berlaku dalam satu proses analisis dan tidak menyebabkan state global.

### Struktur package

- [x] 25. Pecah `core.py` berdasarkan tanggung jawab analisis.
- [x] 26. Pisahkan modul validasi dan helper internal.
27. Pisahkan analisis overview dan metadata kolom.
28. Pisahkan missing dan duplicate analysis.
29. Pisahkan numeric, categorical, dan outlier analysis.
30. Pisahkan correlation dan target analysis.
- [x] 31. Pisahkan data-quality warnings.
32. Pisahkan report formatting dan serialization.
- [x] 33. Pertahankan satu public API melalui `framepeek/__init__.py`.
- [x] 34. Hindari terlalu banyak modul kecil yang hanya berisi satu helper sederhana.
35. Tegaskan bahwa modul dengan awalan underscore merupakan API internal.

Struktur logis yang perlu tersedia:

* validasi dan shared utilities
* analysis context
* overview dan columns
* missing dan duplicates
* numeric dan categorical
* outliers
* correlations
* target
* quality warnings
* report formatting
* serialization
* public types

### Typing

- [x] 36. Tambahkan `py.typed` ke distribution package.
- [x] 37. Pastikan `py.typed` benar-benar masuk ke wheel dan source distribution.
38. Tambahkan tipe hasil terstruktur untuk report, correlations, duplicates, target, dan warnings.
39. Kurangi penggunaan `Any` pada return type publik.
- [x] 40. Gunakan `Literal` untuk metode yang hanya menerima pilihan tertentu.
41. Gunakan tipe khusus untuk correlation method, outlier method, target type, dan severity. *(Correlation method, outlier method, dan severity selesai; target type menunggu item 42.)*
42. Tambahkan `target_type` dengan pilihan otomatis, kategorikal, atau numerik.
- [x] 43. Tambahkan tipe yang jelas untuk nama kolom yang dapat berupa objek hashable selain string.
44. Pastikan overload atau union hasil target dapat dibedakan dari field `type`.
45. Jalankan type checking terhadap public API, bukan hanya implementasi internal.

### Versioning dan metadata runtime

- [x] 46. Tambahkan `framepeek.__version__`.
- [x] 47. Ambil versi dari package metadata agar tidak terjadi duplikasi sumber versi.
- [x] 48. Tambahkan test yang memastikan versi runtime sama dengan versi distribution.
49. Tambahkan informasi versi ke report metadata bila berguna untuk reproducibility.
50. Tambahkan informasi versi pandas dan Python secara opsional untuk debugging report.

### Performa

51. Gunakan sampling untuk heuristik `numeric_as_string`.
52. Gunakan sampling untuk heuristik `datetime_as_string`.
53. Buat ukuran sample dapat dikonfigurasi.
54. Gunakan random state yang konsisten jika sampling dilakukan secara acak.
55. Catat dalam hasil atau metadata ketika analisis menggunakan sample.
56. Hindari parsing datetime seluruh kolom hanya untuk menghasilkan warning.
57. Hindari `value_counts()` berulang untuk kolom yang sama.
58. Hindari `nunique()` berulang untuk kolom yang sama.
59. Hindari penghitungan deep memory bila pengguna tidak membutuhkannya.
60. Tambahkan pilihan subset kolom untuk `correlations()`.
61. Tambahkan batas maksimum kolom numerik untuk analisis korelasi.
62. Tambahkan perilaku yang jelas ketika batas korelasi terlampaui: error, warning, atau skip.
63. Tambahkan opsi hanya menghitung correlation pairs tanpa menyimpan full matrix.
64. Tambahkan opsi membatasi jumlah pasangan korelasi teratas.
65. Beri perlindungan terhadap penggunaan Kendall pada dataset sangat besar.
66. Pertimbangkan sampling baris khusus untuk korelasi.
67. Tambahkan benchmark untuk DataFrame tinggi, lebar, banyak kategorikal, dan banyak missing value.
68. Ukur runtime serta penggunaan memori, bukan hanya test correctness.

### Ketepatan statistik dan data quality

69. Bedakan missing value dari positive dan negative infinity.
70. Tambahkan statistik dan warning untuk non-finite numeric values.
71. Pastikan infinity tidak dihitung sebagai missing.
72. Tangani IQR bernilai nol secara eksplisit.
73. Tandai keterbatasan outlier detection pada kolom constant atau near-constant.
74. Tambahkan minimum sample size untuk skewness, kurtosis, korelasi, dan outlier detection.
75. Jangan otomatis menganggap target numerik dengan sedikit nilai unik sebagai kategorikal tanpa opsi override.
76. Tambahkan deteksi numeric identifier agar nomor telepon, kode pos, NIK, dan kode produk tidak mudah dianggap numeric-as-string.
77. Tambahkan deteksi empty string dan whitespace-only values.
78. Tambahkan deteksi perbedaan kapitalisasi kategori.
79. Tambahkan deteksi leading atau trailing whitespace.
80. Tambahkan deteksi mixed Python object types.
81. Tambahkan analisis missingness pattern antar-kolom.
82. Tambahkan rare-category concentration warning sesuai audit yang sudah dibuat.
83. Pastikan semua warning menyertakan kode, severity, metric, pesan, dan rekomendasi yang stabil.
84. Dokumentasikan bahwa strength label pada korelasi merupakan heuristik, bukan aturan universal.

### Report dan serialization

85. Pisahkan proses formatting report dari proses mencetak ke terminal.
86. Tambahkan hasil report dalam bentuk string.
87. Tambahkan batas baris, kolom, dan panjang cell untuk output terminal.
88. Jangan selalu mencetak seluruh isi report tanpa batas.
89. Tambahkan export machine-readable.
90. Pastikan export menangani DataFrame, timestamp, NumPy scalar, missing value, dan infinity.
91. Jangan menyimpan informasi penting hanya di `DataFrame.attrs`.
92. Ubah hasil missing analysis menjadi struktur yang secara eksplisit memisahkan statistik per kolom dan per baris.
93. Tambahkan metadata report mengenai sampling, konfigurasi, versi, dan waktu analisis.
94. Tentukan schema report yang stabil dan terdokumentasi.

## Testing yang harus ditambahkan

- [x] 95. Test bahwa `correlation_method` konsisten antara bagian target dan correlations.
- [x] 96. Test bahwa `outlier_multiplier` konsisten antara bagian outliers dan warnings.
- [x] 97. Test bahwa outlier dan correlation tidak dihitung ulang saat dipanggil melalui `profile()`.
- [x] 98. Test dengan mocking atau instrumentation untuk menghitung jumlah pemanggilan fungsi internal.
- [x] 99. Test seluruh batas threshold tepat di bawah, tepat pada, dan tepat di atas batas.
100. Test tipe pandas nullable seperti `Int64`, `Float64`, `boolean`, dan `string`.
101. Test datetime dengan timezone, timedelta, category, dan Arrow-backed string.
102. Test semua NaN, semua infinity, campuran NaN dan infinity, serta satu nilai valid.
103. Test kolom constant dan IQR nol.
104. Test DataFrame dengan satu baris dan satu kolom.
105. Test nama kolom integer, tuple, dan tipe hashable lain.
- [x] 106. Test duplicate column diagnostics.
107. Test object column berisi campuran string, list, dictionary, dan angka.
108. Test numeric identifier agar tidak salah diklasifikasikan.
109. Test sampling menghasilkan hasil reproducible.
110. Test serialization terhadap seluruh tipe output.
111. Test bahwa input DataFrame tidak berubah setelah semua fungsi dipanggil.
112. Tambahkan branch coverage, bukan hanya statement coverage.
113. Tambahkan property-based testing untuk invariant statistik dan schema.
114. Test wheel yang sudah dibangun, bukan hanya editable installation.
115. Test bahwa `py.typed` tersedia dalam wheel.
116. Test import dan type checking dari project eksternal sederhana.

## Urutan pengerjaan

### Bugfix release terdekat

- [x] 1. Konsistensi correlation method.
- [x] 2. Konsistensi outlier configuration.
- [x] 3. Hilangkan redundant correlation dan outlier computation.
- [x] 4. Perbaiki penamaan `target_column`.
- [x] 5. Tambahkan regression tests untuk ketiga bug.
- [x] 6. Tambahkan `py.typed`.
- [x] 7. Tambahkan `__version__`.

### Refactor berikutnya

- [x] 8. Buat validation helpers.
9. Buat analysis context.
- [x] 10. Pecah `core.py`.
11. Tambahkan typed result.
12. Pisahkan formatting dari printing.
13. Tambahkan serialization.

### Optimasi berikutnya

14. Sampling untuk parsing heuristik.
15. Correlation subset dan safeguards.
16. Benchmark suite.
17. Optimasi reuse metadata per kolom.
18. Tambahkan missing-pattern dan non-finite analysis.

## Refactor struktur package

Struktur minimal yang diterapkan:

```text
src/framepeek/
├── __init__.py
├── types.py
├── validation.py
├── analysis.py
├── warnings.py
└── report.py
```

- [x] Public API tetap diekspor melalui `framepeek/__init__.py`.
- [x] `core.py` dihapus setelah tanggung jawabnya dipindahkan.
- [x] Tidak ada modul satu-fungsi.
- [x] `serialization.py` ditunda sampai fitur serialization dikerjakan.
