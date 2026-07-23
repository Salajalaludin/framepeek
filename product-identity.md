# FramePeek

## Project Brief — Exploratory Data Analysis Package for Python

---

## 1. Ringkasan Eksekutif

**FramePeek** adalah package Python untuk melakukan **Exploratory Data Analysis atau EDA secara cepat, terstruktur, dan konsisten pada data tabular**.

Package ini dirancang untuk membantu data analyst, data scientist, mahasiswa, dan peneliti memahami kondisi awal sebuah dataset sebelum melanjutkan ke proses data cleaning, feature engineering, visualisasi lanjutan, analisis statistik, atau pemodelan machine learning.

FramePeek menerima input utama berupa `pandas.DataFrame` dan menghasilkan kumpulan ringkasan analisis yang dapat digunakan kembali dalam bentuk `pandas.DataFrame`, dictionary, atau objek report.

Tujuan utama FramePeek bukan untuk menggantikan proses analisis manusia, melainkan untuk mempercepat tahap pemeriksaan awal dan membantu pengguna menemukan aspek dataset yang membutuhkan perhatian lebih lanjut.

Contoh penggunaan:

```python
import framepeek as fp

report = fp.profile(
    df,
    target="is_churn"
)

report["overview"]
report["columns"]
report["missing"]
report["numeric"]
report["categorical"]
report["outliers"]
report["correlations"]
report["target"]
report["warnings"]
```

---

## 2. Identitas Produk

### Nama package

**FramePeek**

Nama ini berasal dari dua kata:

* **Frame**, merujuk pada DataFrame sebagai struktur data utama;
* **Peek**, berarti melihat atau memeriksa secara cepat.

FramePeek menggambarkan fungsi utama package, yaitu memberikan gambaran awal mengenai sebuah DataFrame sebelum pengguna melakukan analisis lebih mendalam.

### Tagline

**Peek into your data before going deeper.**

---

## 3. Latar Belakang

Exploratory Data Analysis merupakan salah satu tahap penting dalam workflow analisis data.

Sebelum melakukan pemodelan atau pengambilan keputusan, pengguna perlu memahami beberapa karakteristik dasar dataset, seperti:

* ukuran dataset;
* struktur kolom;
* tipe data;
* missing value;
* nilai unik;
* baris duplikat;
* distribusi variabel numerik;
* distribusi variabel kategorik;
* potensi outlier;
* korelasi antarvariabel;
* distribusi variabel target;
* kemungkinan masalah kualitas data.

Pada praktiknya, pemeriksaan tersebut sering dilakukan dengan menulis ulang potongan kode yang sama pada setiap notebook atau proyek.

Contoh proses yang biasanya dilakukan secara manual:

```python
df.shape
df.info()
df.describe()
df.isna().sum()
df.duplicated().sum()
df.nunique()
df.corr()
```

Pendekatan tersebut tetap berguna, tetapi memiliki beberapa keterbatasan:

* kode EDA menjadi repetitif;
* format output berbeda antarproyek;
* pemeriksaan penting dapat terlewat;
* notebook menjadi panjang dan sulit dibaca;
* hasil sulit digunakan kembali;
* pengguna perlu menggabungkan banyak output secara manual;
* dataset dengan banyak kolom membutuhkan waktu pemeriksaan lebih lama.

FramePeek dikembangkan untuk menyederhanakan proses tersebut menjadi workflow yang lebih ringkas, modular, dan terstandarisasi.

---

## 4. Pernyataan Masalah

FramePeek berusaha menyelesaikan beberapa masalah utama berikut.

### 4.1 Kode EDA yang berulang

Data analyst sering menulis kembali fungsi pemeriksaan missing value, outlier, distribusi kategori, dan korelasi pada hampir setiap proyek.

### 4.2 Output yang tidak konsisten

Setiap notebook dapat memiliki format ringkasan yang berbeda sehingga menyulitkan perbandingan, dokumentasi, dan penggunaan kembali.

### 4.3 Pemeriksaan kualitas data yang tidak lengkap

Beberapa masalah seperti kolom konstan, cardinality tinggi, kemungkinan identifier, atau tipe data yang tidak sesuai sering terlewat pada tahap awal.

### 4.4 Dataset berdimensi besar sulit diperiksa

Dataset dengan puluhan hingga ratusan kolom membutuhkan pemeriksaan manual yang cukup panjang.

### 4.5 Hasil EDA sulit diproses ulang

Banyak proses EDA hanya menampilkan hasil melalui `print()` atau plot, sehingga sulit digunakan untuk dashboard, laporan otomatis, atau pipeline berikutnya.

### 4.6 Hambatan bagi pengguna pemula

Pengguna yang baru mempelajari data analysis sering tidak mengetahui pemeriksaan apa saja yang perlu dilakukan sebelum modeling.

---

## 5. Visi Produk

Menjadi package EDA Python yang ringan, modular, mudah digunakan, dan mampu memberikan gambaran awal dataset secara terstruktur tanpa memerlukan konfigurasi yang rumit.

---

## 6. Misi Produk

FramePeek memiliki beberapa misi utama:

1. mempercepat proses pemeriksaan awal dataset;
2. mengurangi penulisan kode EDA yang repetitif;
3. menyediakan format output yang konsisten;
4. membantu mendeteksi potensi masalah kualitas data;
5. menghasilkan output yang dapat diproses kembali;
6. mendukung pengguna pemula maupun berpengalaman;
7. tetap ringan dan tidak memiliki dependensi berlebihan;
8. menyediakan fondasi yang dapat dikembangkan menjadi sistem profiling yang lebih lengkap.

---

## 7. Tujuan Produk

FramePeek bertujuan untuk:

* memberikan gambaran umum dataset dalam satu perintah;
* menyederhanakan pemeriksaan setiap kolom;
* mengidentifikasi missing value dan duplikasi;
* merangkum variabel numerik dan kategorik;
* mendeteksi potensi outlier;
* menganalisis hubungan antarvariabel;
* mengevaluasi distribusi variabel target;
* menghasilkan data quality warnings;
* mendukung workflow eksplorasi yang modular;
* menjaga DataFrame asli tetap tidak berubah.

---

## 8. Target Pengguna

### 8.1 Pengguna utama

* Data analyst
* Data scientist
* Mahasiswa statistika
* Mahasiswa data science
* Machine learning engineer
* Peneliti dengan data tabular

### 8.2 Pengguna sekunder

* Business intelligence analyst
* Data engineer
* Dosen atau pengajar statistika
* Pengguna Python tingkat pemula
* Praktisi yang membutuhkan pemeriksaan cepat terhadap dataset

### 8.3 Kebutuhan pengguna

Pengguna membutuhkan cara untuk:

* memahami dataset tanpa menulis banyak kode;
* mendapatkan hasil yang mudah dibaca;
* mengetahui potensi masalah data;
* memilih analisis lanjutan yang relevan;
* menyimpan atau mengekspor hasil EDA;
* menggunakan output dalam notebook atau aplikasi lain.

---

## 9. Value Proposition

FramePeek memberikan cara yang cepat dan praktis untuk memperoleh gambaran awal dataset melalui satu API yang konsisten.

### Fast

Mengurangi waktu yang dibutuhkan untuk menulis kode EDA dasar.

### Structured

Menghasilkan output dengan struktur dan nama kolom yang konsisten.

### Reusable

Hasil analisis dapat digunakan kembali dalam notebook, dashboard, laporan, atau pipeline data.

### Modular

Setiap fungsi dapat dijalankan secara terpisah tanpa harus membuat report lengkap.

### Lightweight

Versi awal hanya bergantung pada library inti seperti `pandas` dan `numpy`.

### Practical

Fokus pada kebutuhan EDA yang paling sering ditemui dalam proyek data nyata.

### Beginner-friendly

Fungsi, parameter, dan hasil dirancang agar mudah dipahami pengguna pemula.

### Warning-oriented

Tidak hanya menampilkan statistik, tetapi juga menandai potensi masalah kualitas data.

### Non-destructive

FramePeek hanya menganalisis data dan tidak mengubah DataFrame asli.

---

## 10. Positioning Produk

FramePeek diposisikan sebagai package EDA yang berada di antara pemeriksaan manual menggunakan `pandas` dan profiling otomatis yang sangat besar.

FramePeek tidak berusaha menjadi package dengan fitur terbanyak. Fokus utamanya adalah:

* ringan;
* cepat dipasang;
* mudah digunakan;
* output dapat diproses kembali;
* tidak terlalu bergantung pada laporan HTML;
* relevan untuk workflow data analyst;
* mudah dikembangkan secara modular.

FramePeek cocok bagi pengguna yang menginginkan profiling lebih lengkap daripada `df.describe()`, tetapi tetap menginginkan kontrol terhadap setiap hasil analisis.

---

## 11. Prinsip Desain Produk

### 11.1 Simple by default

Pengguna harus dapat menjalankan analisis tanpa konfigurasi kompleks.

```python
report = fp.profile(df)
```

### 11.2 Configurable when needed

Parameter tambahan tersedia bagi pengguna yang membutuhkan kontrol lebih besar.

```python
report = fp.profile(
    df,
    target="churn",
    correlation_method="spearman",
    outlier_method="iqr",
    outlier_multiplier=1.5,
    top_n_categories=10
)
```

### 11.3 Structured output

Setiap fungsi harus mengembalikan objek yang dapat digunakan kembali, seperti:

* `pandas.DataFrame`;
* dictionary;
* list of dictionaries;
* report object.

Fungsi tidak boleh hanya menampilkan hasil menggunakan `print()`.

### 11.4 Non-destructive

FramePeek tidak boleh mengubah nilai, tipe data, nama kolom, atau urutan DataFrame asli.

### 11.5 Transparent

Metode, threshold, dan asumsi yang digunakan harus dapat diketahui pengguna.

### 11.6 Modular

Pengguna dapat menjalankan pemeriksaan tertentu tanpa menjalankan seluruh profiling.

### 11.7 Predictable

Nama fungsi, parameter, dan struktur output harus konsisten.

### 11.8 Extensible

Arsitektur package harus memungkinkan penambahan:

* metode outlier baru;
* visualisasi;
* exporter;
* dukungan Polars;
* plugin data quality;
* domain-specific checks.

---

## 12. Ruang Lingkup MVP

FramePeek versi awal berfokus pada data tabular dalam bentuk `pandas.DataFrame`.

MVP harus mencakup modul berikut:

1. input validation;
2. dataset overview;
3. column profiling;
4. missing value analysis;
5. duplicate analysis;
6. numeric summary;
7. categorical summary;
8. outlier analysis;
9. correlation analysis;
10. target analysis;
11. data quality warnings;
12. complete profiling;
13. unit testing;
14. dokumentasi dasar.

---

# 13. Spesifikasi Fitur MVP

## 13.1 Input Validation

Semua fungsi harus memvalidasi input sebelum analisis dijalankan.

Pemeriksaan minimal:

* input harus berupa `pandas.DataFrame`;
* DataFrame tidak boleh kosong;
* kolom target harus tersedia jika ditentukan;
* parameter metode harus termasuk dalam opsi yang didukung;
* parameter numerik seperti threshold harus memiliki nilai valid;
* nama kolom tidak boleh ambigu.

Contoh:

```python
fp.validate(df)
```

Contoh error:

```text
TypeError: Expected pandas.DataFrame, received list.

ValueError: DataFrame must contain at least one row and one column.

KeyError: Target column 'is_churn' was not found.
```

---

## 13.2 Dataset Overview

Fungsi overview menghasilkan informasi umum mengenai dataset.

### Informasi yang dihasilkan

* jumlah baris;
* jumlah kolom;
* jumlah seluruh sel;
* jumlah missing cells;
* persentase missing cells;
* jumlah baris duplikat;
* persentase baris duplikat;
* penggunaan memori;
* jumlah kolom numerik;
* jumlah kolom kategorik;
* jumlah kolom boolean;
* jumlah kolom datetime;
* jumlah kolom lainnya.

### Contoh penggunaan

```python
fp.overview(df)
```

### Contoh output

| metric         |   value |
| -------------- | ------: |
| rows           |  100000 |
| columns        |      24 |
| total_cells    | 2400000 |
| missing_cells  |   42310 |
| missing_pct    |    1.76 |
| duplicate_rows |     214 |
| memory_mb      |   36.41 |

---

## 13.3 Column Profile

Fungsi column profile menghasilkan ringkasan untuk setiap kolom.

### Informasi yang dihasilkan

* nama kolom;
* tipe data;
* inferred type;
* jumlah non-null;
* jumlah missing;
* persentase missing;
* jumlah nilai unik;
* persentase nilai unik;
* nilai paling sering muncul;
* frekuensi nilai paling sering muncul;
* persentase nilai paling sering muncul;
* kemungkinan identifier;
* kemungkinan kolom konstan;
* kemungkinan high cardinality.

### Contoh penggunaan

```python
fp.columns(df)
```

### Contoh output

| column      | dtype  | inferred_type | missing_pct | unique | top     | possible_id |
| ----------- | ------ | ------------- | ----------: | -----: | ------- | ----------- |
| customer_id | object | identifier    |         0.0 | 100000 | C0001   | True        |
| age         | int64  | numeric       |         1.2 |     68 | 24      | False       |
| city        | object | categorical   |         4.6 |     32 | Jakarta | False       |

---

## 13.4 Missing Value Analysis

Fungsi ini menganalisis pola missing value pada setiap kolom.

### Informasi yang dihasilkan

* nama kolom;
* jumlah missing;
* persentase missing;
* jumlah non-missing;
* tingkat missing;
* ranking missing value;
* jumlah baris yang memiliki minimal satu missing;
* jumlah baris lengkap;
* persentase baris lengkap.

### Kategori tingkat missing

| Persentase | Kategori |
| ---------: | -------- |
|         0% | none     |
|      >0–5% | low      |
|     >5–20% | moderate |
|    >20–50% | high     |
|       >50% | critical |

Threshold harus dapat dikonfigurasi.

### Contoh penggunaan

```python
fp.missing(df)
```

### Contoh output

| column | missing | missing_pct | severity |
| ------ | ------: | ----------: | -------- |
| income |   32140 |       32.14 | high     |
| gender |    6840 |        6.84 | moderate |
| age    |     420 |        0.42 | low      |

---

## 13.5 Duplicate Analysis

Fungsi duplicate analysis memeriksa duplikasi pada seluruh baris atau subset kolom.

### Informasi yang dihasilkan

* jumlah baris duplikat;
* persentase baris duplikat;
* jumlah duplicate groups;
* jumlah baris unik;
* contoh baris duplikat;
* jumlah kemunculan setiap kelompok duplikat.

### Contoh penggunaan

```python
fp.duplicates(df)
```

Dengan subset:

```python
fp.duplicates(
    df,
    subset=["customer_id", "transaction_date"]
)
```

---

## 13.6 Numeric Summary

Fungsi numeric summary menghasilkan statistik deskriptif untuk kolom numerik.

### Statistik yang dihasilkan

* count;
* missing;
* missing percentage;
* mean;
* median;
* mode;
* standard deviation;
* variance;
* minimum;
* maximum;
* range;
* Q1;
* Q2;
* Q3;
* interquartile range;
* coefficient of variation;
* skewness;
* kurtosis;
* jumlah nilai nol;
* persentase nilai nol;
* jumlah nilai negatif;
* persentase nilai negatif.

### Contoh penggunaan

```python
fp.numeric(df)
```

### Contoh output

| column | mean | median |  std | min |  q1 |  q3 |  max | skewness |
| ------ | ---: | -----: | ---: | --: | --: | --: | ---: | -------: |
| age    | 31.4 |   29.0 | 10.2 |  18 |  23 |  38 |   89 |     1.18 |
| income |  7.2 |    6.5 |  3.1 | 0.5 | 4.8 | 8.9 | 30.0 |     1.72 |

---

## 13.7 Categorical Summary

Fungsi categorical summary menghasilkan informasi mengenai kolom kategorik, string, dan boolean.

### Informasi yang dihasilkan

* jumlah kategori unik;
* missing value;
* missing percentage;
* nilai paling sering muncul;
* frekuensi nilai teratas;
* persentase nilai teratas;
* cardinality ratio;
* top-N categories;
* kategori langka;
* jumlah kategori yang hanya muncul sekali;
* persentase kategori terhadap jumlah observasi.

### Contoh penggunaan

```python
fp.categorical(
    df,
    top_n=5
)
```

### Contoh output

| column  | unique | top     | top_frequency | top_pct | cardinality_ratio |
| ------- | -----: | ------- | ------------: | ------: | ----------------: |
| city    |     32 | Jakarta |         18420 |   18.42 |           0.00032 |
| segment |      4 | Regular |         62340 |   62.34 |           0.00004 |

---

## 13.8 Outlier Analysis

Pada MVP, outlier dideteksi menggunakan metode Interquartile Range.

### Rumus

```text
IQR = Q3 - Q1

Lower Bound = Q1 - multiplier × IQR

Upper Bound = Q3 + multiplier × IQR
```

Nilai yang berada di bawah lower bound atau di atas upper bound ditandai sebagai potential outlier.

### Informasi yang dihasilkan

* nama kolom;
* Q1;
* Q3;
* IQR;
* lower bound;
* upper bound;
* jumlah outlier;
* persentase outlier;
* jumlah lower outlier;
* jumlah upper outlier;
* nilai minimum outlier;
* nilai maksimum outlier.

### Contoh penggunaan

```python
fp.outliers(
    df,
    method="iqr",
    multiplier=1.5
)
```

### Catatan

Outlier yang terdeteksi tidak otomatis dianggap salah. Hasil hanya berfungsi sebagai indikasi untuk pemeriksaan lanjutan.

---

## 13.9 Correlation Analysis

Fungsi correlation analysis menghitung hubungan antarvariabel numerik.

### Metode yang didukung

* Pearson;
* Spearman;
* Kendall.

### Contoh penggunaan

```python
fp.correlations(
    df,
    method="spearman"
)
```

### Output utama

* correlation matrix;
* pasangan variabel;
* nilai korelasi;
* absolute correlation;
* arah hubungan;
* tingkat kekuatan hubungan.

### Contoh fungsi tambahan

```python
fp.top_correlations(
    df,
    method="pearson",
    threshold=0.7
)
```

### Kategori kekuatan korelasi

| Nilai absolut | Interpretasi |
| ------------: | ------------ |
|     0.00–0.19 | very weak    |
|     0.20–0.39 | weak         |
|     0.40–0.59 | moderate     |
|     0.60–0.79 | strong       |
|     0.80–1.00 | very strong  |

Interpretasi harus disampaikan sebagai panduan umum, bukan aturan absolut.

---

## 13.10 Target Analysis

Jika pengguna menentukan kolom target, FramePeek menghasilkan ringkasan khusus.

### Target kategorik

Informasi yang dihasilkan:

* jumlah kelas;
* jumlah observasi setiap kelas;
* persentase setiap kelas;
* kelas mayoritas;
* kelas minoritas;
* majority-to-minority ratio;
* missing value pada target;
* indikasi class imbalance.

### Target numerik

Informasi yang dihasilkan:

* statistik deskriptif;
* distribusi;
* skewness;
* kurtosis;
* missing value;
* potensi outlier;
* hubungan target dengan feature numerik.

### Contoh penggunaan

```python
fp.target(
    df,
    target="is_churn"
)
```

### Contoh output kategorik

| value | count | percentage |
| ----- | ----: | ---------: |
| 0     | 92100 |      92.10 |
| 1     |  7900 |       7.90 |

Peringatan:

```text
Target 'is_churn' may be imbalanced. Majority-to-minority ratio: 11.66.
```

---

## 13.11 Data Quality Warnings

FramePeek tidak hanya menampilkan statistik, tetapi juga memberikan peringatan yang dapat ditindaklanjuti.

### Pemeriksaan yang didukung pada MVP

* kolom seluruhnya missing;
* kolom konstan;
* kolom hampir konstan;
* kemungkinan identifier;
* high-cardinality categorical column;
* missing value tinggi;
* duplicate rows;
* outlier percentage tinggi;
* class imbalance;
* tipe data yang diduga tidak sesuai;
* kolom numerik yang tersimpan sebagai string;
* kolom datetime yang tersimpan sebagai string;
* nama kolom duplikat;
* kolom tanpa variasi;
* kategori langka dalam jumlah besar.

### Struktur warning

Setiap warning memiliki:

* kode warning;
* severity;
* affected column;
* message;
* recommendation;
* supporting metric.

### Severity

* `info`
* `low`
* `medium`
* `high`
* `critical`

### Contoh output

| severity | column      | issue               | message                                 |
| -------- | ----------- | ------------------- | --------------------------------------- |
| high     | income      | missing_values      | Column contains 32.14% missing values   |
| medium   | customer_id | possible_identifier | Column contains 100% unique values      |
| medium   | age         | potential_outliers  | Column contains 4.7% potential outliers |
| high     | is_churn    | class_imbalance     | Majority-to-minority ratio is 11.66     |

### Contoh penggunaan

```python
fp.warnings(df, target="is_churn")
```

---

## 13.12 Complete Profile

Fungsi `profile()` menjalankan seluruh pemeriksaan utama dalam satu proses.

### Contoh penggunaan

```python
report = fp.profile(
    df,
    target="is_churn"
)
```

### Struktur hasil

```python
{
    "overview": ...,
    "columns": ...,
    "missing": ...,
    "duplicates": ...,
    "numeric": ...,
    "categorical": ...,
    "outliers": ...,
    "correlations": ...,
    "target": ...,
    "warnings": ...
}
```

Jika target tidak diberikan, bagian `target` dapat bernilai `None` atau tidak disertakan.

### Contoh akses hasil

```python
report["overview"]
report["missing"]
report["warnings"]
```

---

## 14. Desain API

FramePeek mendukung dua pendekatan penggunaan.

### 14.1 Functional API

Pendekatan utama pada MVP.

```python
import framepeek as fp

fp.overview(df)
fp.columns(df)
fp.missing(df)
fp.duplicates(df)
fp.numeric(df)
fp.categorical(df)
fp.outliers(df)
fp.correlations(df)
fp.target(df, target="churn")
fp.warnings(df)
```

Keunggulan:

* sederhana;
* mudah dipahami;
* cocok untuk notebook;
* mudah diuji;
* setiap fungsi dapat digunakan secara independen.

### 14.2 Report Object API

Dapat dikembangkan setelah functional API stabil.

```python
from framepeek import FrameReport

report = FrameReport(
    df,
    target="churn"
)

report.overview
report.columns
report.missing
report.outliers
report.correlations
report.target
report.warnings
```

Keunggulan:

* hasil dapat disimpan sebagai state;
* tidak perlu menghitung ulang analisis;
* lebih mudah dikembangkan untuk export;
* cocok untuk workflow yang lebih besar.

---

## 15. Contoh User Journey

Seorang data analyst menerima dataset pelanggan baru.

```python
import pandas as pd
import framepeek as fp

df = pd.read_csv("customers.csv")
```

Pengguna menjalankan:

```python
report = fp.profile(
    df,
    target="churn"
)
```

FramePeek menghasilkan ringkasan:

```text
Dataset contains 125,430 rows and 24 columns.

Three columns contain more than 20% missing values.

Column 'customer_id' may be an identifier because all values are unique.

Column 'monthly_spend' contains 4.7% potential outliers.

Target 'churn' has a majority-to-minority ratio of 8.2.

Dataset contains 214 duplicate rows.
```

Pengguna kemudian memeriksa bagian tertentu:

```python
report["missing"]
report["outliers"]
report["target"]
report["warnings"]
```

Hasil tersebut menjadi dasar untuk menentukan langkah data cleaning, feature engineering, dan modeling.

---

## 16. Batasan MVP

Versi awal FramePeek belum mencakup:

* data cleaning otomatis;
* imputasi missing value;
* encoding variabel kategorik;
* transformasi variabel;
* feature engineering;
* pemilihan feature otomatis;
* machine learning;
* causal inference;
* analisis time series khusus;
* analisis survival;
* analisis geospasial;
* analisis teks;
* laporan HTML interaktif;
* dashboard;
* integrasi database;
* pemrosesan data terdistribusi;
* dukungan Spark;
* dukungan Polars;
* automatic decision making.

FramePeek bertugas menganalisis dan memberi indikasi, bukan memperbaiki data secara otomatis.

---

## 17. Struktur Package

```text
framepeek/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── src/
│   └── framepeek/
│       ├── __init__.py
│       ├── overview.py
│       ├── columns.py
│       ├── missing.py
│       ├── duplicates.py
│       ├── numeric.py
│       ├── categorical.py
│       ├── outliers.py
│       ├── correlations.py
│       ├── target.py
│       ├── warnings.py
│       ├── profile.py
│       ├── exceptions.py
│       ├── constants.py
│       └── utils/
│           ├── validation.py
│           ├── inference.py
│           ├── formatting.py
│           └── types.py
├── tests/
│   ├── conftest.py
│   ├── test_overview.py
│   ├── test_columns.py
│   ├── test_missing.py
│   ├── test_duplicates.py
│   ├── test_numeric.py
│   ├── test_categorical.py
│   ├── test_outliers.py
│   ├── test_correlations.py
│   ├── test_target.py
│   ├── test_warnings.py
│   └── test_profile.py
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── api-reference.md
│   └── examples/
├── examples/
│   ├── basic_profile.ipynb
│   └── churn_analysis.ipynb
└── .github/
    └── workflows/
        ├── tests.yml
        └── publish.yml
```

---

## 18. Dependensi

### 18.1 Dependensi utama

```text
pandas
numpy
```

### 18.2 Dependensi pengembangan

```text
pytest
pytest-cov
ruff
mypy
build
twine
pre-commit
```

### 18.3 Dependensi dokumentasi

```text
mkdocs
mkdocs-material
mkdocstrings
```

### 18.4 Dependensi opsional masa depan

```text
matplotlib
plotly
openpyxl
jinja2
polars
scipy
scikit-learn
```

Dependensi tambahan sebaiknya dibuat opsional agar package utama tetap ringan.

Contoh:

```toml
[project.optional-dependencies]
visual = [
    "matplotlib>=3.8",
    "plotly>=5.0"
]

export = [
    "openpyxl>=3.1",
    "jinja2>=3.1"
]
```

---

## 19. Kebutuhan Nonfungsional

### 19.1 Performance

* mampu menangani dataset kecil hingga menengah;
* tidak melakukan salinan DataFrame secara berlebihan;
* korelasi hanya dijalankan pada kolom numerik;
* operasi mahal dapat dinonaktifkan;
* sampling dapat ditambahkan pada versi berikutnya.

### 19.2 Reliability

* semua fungsi utama memiliki unit test;
* error message harus informatif;
* hasil harus konsisten;
* tidak boleh mengubah input asli;
* fungsi harus menangani missing value secara aman.

### 19.3 Maintainability

* setiap modul memiliki tanggung jawab jelas;
* tidak ada duplikasi logika;
* type hint digunakan secara konsisten;
* docstring tersedia pada public API;
* threshold disimpan dalam konfigurasi atau constants.

### 19.4 Compatibility

Target awal:

```text
Python 3.10+
pandas 2.0+
```

### 19.5 Security

FramePeek tidak menjalankan kode dari dataset dan tidak mengirim data ke layanan eksternal.

### 19.6 Privacy

Semua analisis dilakukan secara lokal pada environment pengguna.

---

## 20. Testing Strategy

### 20.1 Unit test

Setiap fungsi utama harus diuji secara independen.

### 20.2 Edge case test

Pengujian harus mencakup:

* DataFrame kosong;
* hanya satu kolom;
* hanya kolom numerik;
* hanya kolom kategorik;
* seluruh nilai missing;
* kolom konstan;
* kolom dengan nilai tak hingga;
* nama kolom duplikat;
* kolom target tidak ditemukan;
* DataFrame dengan MultiIndex;
* dataset dengan banyak kategori.

### 20.3 Mutation safety

Test harus memastikan DataFrame asli tidak berubah setelah fungsi dijalankan.

### 20.4 Output schema test

Nama kolom dan tipe output harus konsisten.

### 20.5 Coverage target

Target awal:

```text
Minimal code coverage: 80%
Target ideal: 90%
```

---

## 21. Dokumentasi

Dokumentasi minimal harus mencakup:

* instalasi;
* quick start;
* daftar fungsi;
* parameter;
* tipe output;
* contoh dataset;
* contoh notebook;
* penjelasan metode;
* interpretasi warning;
* limitations;
* kontribusi;
* changelog.

### Contoh Quick Start

```python
import pandas as pd
import framepeek as fp

df = pd.read_csv("data.csv")

report = fp.profile(df)

print(report["overview"])
print(report["warnings"])
```

---

## 22. Roadmap Pengembangan

### Versi 0.1.0 — Core Profiling

Fokus:

* validasi input;
* dataset overview;
* column profile;
* missing value;
* duplicates;
* numeric summary;
* categorical summary;
* outlier IQR;
* correlations;
* target distribution;
* complete profile;
* unit testing;
* dokumentasi dasar.

### Versi 0.2.0 — Data Quality Intelligence

Fokus:

* possible identifier;
* constant column;
* near-constant column;
* high cardinality;
* rare categories;
* suspected wrong dtype;
* duplicate column names;
* imbalance detection;
* warning severity;
* recommendation message.

### Versi 0.3.0 — Visualization

Fokus:

* histogram;
* boxplot;
* bar chart;
* missing value plot;
* correlation heatmap;
* target distribution plot;
* target versus feature plot;
* optional Plotly support.

### Versi 0.4.0 — Report Export

Fokus:

* HTML report;
* Excel report;
* JSON export;
* Markdown report;
* report metadata;
* customizable templates.

### Versi 0.5.0 — Performance and Scalability

Fokus:

* sampling;
* chunk-based analysis;
* optional parallel processing;
* memory optimization;
* progress indicator;
* Polars support.

### Versi 0.6.0 — Advanced Analysis

Fokus:

* modified Z-score;
* robust outlier analysis;
* association for categorical variables;
* mutual information;
* missing pattern analysis;
* datetime profiling;
* text length profiling.

### Versi 1.0.0 — Stable Release

Fokus:

* stable public API;
* comprehensive documentation;
* compatibility testing;
* semantic versioning;
* package publication;
* contributor guidelines;
* production-ready release.

---

## 23. Risiko Pengembangan

### 23.1 Scope terlalu luas

EDA mencakup banyak metode. Fitur harus diprioritaskan berdasarkan kebutuhan paling umum.

### 23.2 Performa dataset besar

Operasi seperti korelasi, value count, dan unique count dapat mahal.

Mitigasi:

* optional sampling;
* operation flags;
* memory-efficient implementation;
* configurable limits.

### 23.3 False positive warnings

Kolom unik tidak selalu identifier dan outlier tidak selalu kesalahan data.

Mitigasi:

* gunakan kata seperti `possible`, `potential`, atau `suspected`;
* tampilkan metric pendukung;
* jangan melakukan perubahan otomatis.

### 23.4 Ambiguitas tipe data

Kolom tanggal atau numerik dapat tersimpan sebagai string.

Mitigasi:

* pisahkan `dtype` dan `inferred_type`;
* berikan confidence atau alasan;
* tetap mempertahankan tipe data asli.

### 23.5 Output terlalu banyak

Profil lengkap dapat menghasilkan banyak tabel.

Mitigasi:

* pisahkan hasil berdasarkan section;
* sediakan summary mode;
* sediakan parameter `include` dan `exclude`.

### 23.6 API tidak konsisten

Perubahan nama parameter dapat menyulitkan pengguna.

Mitigasi:

* tetapkan naming convention sejak awal;
* gunakan semantic versioning;
* dokumentasikan breaking changes.

---

## 24. Ukuran Keberhasilan

FramePeek MVP dianggap berhasil apabila:

* dapat dipasang melalui `pip`;
* satu fungsi dapat menghasilkan profil lengkap;
* semua hasil utama berbentuk objek terstruktur;
* DataFrame asli tidak berubah;
* semua fungsi utama memiliki unit test;
* code coverage minimal 80%;
* dokumentasi quick start tersedia;
* error message mudah dipahami;
* package mendukung data numerik dan kategorik campuran;
* warning system mampu menandai masalah dasar;
* package dapat digunakan pada notebook tanpa konfigurasi kompleks.

---

## 25. Acceptance Criteria MVP

MVP dianggap selesai jika pengguna dapat menjalankan:

```python
import framepeek as fp

report = fp.profile(
    df,
    target="target_column"
)
```

dan memperoleh seluruh bagian berikut:

* dataset overview;
* column profile;
* missing value summary;
* duplicate analysis;
* numeric summary;
* categorical summary;
* outlier summary;
* correlation analysis;
* target analysis;
* data quality warnings.

Kriteria teknis:

* tidak mengubah DataFrame asli;
* tidak gagal ketika dataset memiliki missing value;
* tidak gagal ketika salah satu tipe kolom tidak tersedia;
* output setiap fungsi terdokumentasi;
* threshold utama dapat dikonfigurasi;
* unit test berjalan tanpa error;
* package berhasil dibuild;
* package dapat diinstal pada environment baru.

---

## 26. Contoh API Akhir MVP

```python
import pandas as pd
import framepeek as fp

df = pd.read_csv("customers.csv")

report = fp.profile(
    df,
    target="churn",
    correlation_method="spearman",
    outlier_method="iqr",
    outlier_multiplier=1.5,
    top_n_categories=5
)

overview = report["overview"]
missing = report["missing"]
numeric = report["numeric"]
categorical = report["categorical"]
outliers = report["outliers"]
correlations = report["correlations"]
target = report["target"]
warnings = report["warnings"]
```

Pengguna juga dapat menjalankan analisis secara terpisah:

```python
fp.overview(df)
fp.columns(df)
fp.missing(df)
fp.duplicates(df)
fp.numeric(df)
fp.categorical(df)
fp.outliers(df)
fp.correlations(df)
fp.target(df, target="churn")
fp.warnings(df, target="churn")
```

---

## 27. Kesimpulan

FramePeek adalah package Python untuk membantu pengguna memperoleh gambaran awal dataset secara cepat, terstruktur, dan dapat digunakan kembali.

Fokus utama versi awal adalah pemeriksaan data tabular menggunakan `pandas.DataFrame`, meliputi:

* struktur dataset;
* kualitas data;
* statistik deskriptif;
* missing value;
* duplikasi;
* outlier;
* korelasi;
* distribusi target;
* data quality warnings.

FramePeek tidak melakukan data cleaning atau pengambilan keputusan otomatis. Package ini berfungsi sebagai alat observasi awal yang membantu pengguna menentukan langkah analisis berikutnya dengan lebih tepat.

Dengan pendekatan yang ringan, modular, transparan, dan beginner-friendly, FramePeek dapat dikembangkan menjadi package portfolio yang relevan sekaligus memiliki potensi untuk digunakan pada proyek data nyata.
