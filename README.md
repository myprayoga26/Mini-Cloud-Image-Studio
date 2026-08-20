# ☁️🖼️ Mini Cloud Image Studio

Aplikasi pembelajaran Cloud Computing menggunakan:

- Python
- Streamlit
- Pillow
- boto3
- LocalStack
- S3
- DynamoDB

## Fitur

1. Upload gambar ke LocalStack S3.
2. Menyimpan metadata ke DynamoDB.
3. Resize gambar dengan slider lebar dan tinggi.
4. Grayscale filter.
5. Menyimpan hasil edit sebagai object baru di S3.
6. Mencatat hasil edit di DynamoDB.
7. Gallery/grid riwayat gambar.
8. Download hasil gambar.
9. Hapus object S3 dan metadata DynamoDB.

## 1. Prasyarat

Pastikan sudah terpasang:

- Python 3.10+
- Docker Desktop
- Git (opsional)

Cek:

```bash
python --version
docker --version
docker compose version
```

## 2. Jalankan LocalStack

Masuk ke folder project:

```bash
cd mini_cloud_image_studio
```

Jalankan:

```bash
docker compose up -d
```

Cek:

```bash
docker compose ps
```

Container LocalStack harus dalam kondisi running.

## 3. Install dependency Python

Sebaiknya gunakan virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

Kemudian:

```bash
pip install -r requirements.txt
```

## 4. Buat S3 dan DynamoDB

Tidak perlu membuat manual.

Saat `app.py` pertama kali dijalankan, fungsi `ensure_resources()` otomatis membuat:

- S3 bucket: `image-studio-bucket`
- DynamoDB table: `ImageMetadata`

## 5. Jalankan Streamlit

```bash
streamlit run app.py
```

Kemudian buka alamat yang diberikan Streamlit, biasanya:

```text
http://localhost:4566
```

## 6. Alur penggunaan

### Upload

1. Buka tab `Upload`.
2. Pilih JPG, JPEG, PNG, atau WebP.
3. Klik `Upload ke S3`.
4. File masuk ke LocalStack S3.
5. Metadata masuk ke DynamoDB.

### Resize

1. Buka tab `Edit Gambar`.
2. Pilih gambar sumber.
3. Atur slider lebar dan tinggi.
4. Klik `Simpan Hasil Resize`.
5. Hasil disimpan sebagai object baru di S3.
6. Metadata hasil resize masuk ke DynamoDB.

### Grayscale

1. Pilih gambar sumber.
2. Klik `Simpan Hasil Grayscale`.
3. Hasil grayscale disimpan sebagai object baru di S3.
4. Metadata hasil masuk ke DynamoDB.

### Gallery

Tab `Gallery` mengambil metadata dari DynamoDB kemudian mengambil object gambar dari S3 untuk preview.

Setiap card menyediakan:

- Preview
- Nama file
- Filter
- Ukuran
- Dimensi
- Download
- Delete

## 7. Melihat data LocalStack

Jika AWS CLI tersedia:

### S3

```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```

Melihat isi bucket:

```bash
aws --endpoint-url=http://localhost:4566 s3 ls s3://image-studio-bucket --recursive
```

### DynamoDB

```bash
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

Melihat metadata:

```bash
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name ImageMetadata
```

Jika AWS CLI meminta credentials, untuk LocalStack dapat menggunakan:

```text
AWS Access Key ID: test
AWS Secret Access Key: test
Region: us-east-1
```

## 8. Struktur project

```text
mini_cloud_image_studio/
│
├── app.py
├── aws_config.py
├── s3_utils.py
├── dynamodb_utils.py
├── image_utils.py
├── requirements.txt
├── docker-compose.yml
└── README.md
```

### Penjelasan singkat

`aws_config.py`
- Endpoint LocalStack.
- Region.
- Dummy credentials.
- Pembuatan S3 bucket.
- Pembuatan DynamoDB table.

`s3_utils.py`
- Upload object.
- Download object.
- List object.
- Delete object.

`dynamodb_utils.py`
- Insert metadata.
- Get metadata.
- Scan/list metadata.
- Delete metadata.

`image_utils.py`
- Resize.
- Grayscale.
- Konversi PIL Image menjadi bytes.

`app.py`
- UI Streamlit.
- Upload.
- Edit.
- Gallery.
- Download.
- Delete.

## 9. Jika port 4566 bentrok

Jika port 4566 sedang digunakan aplikasi lain, ubah:

```yaml
ports:
  - "4566:4566"
```

Kemudian ubah endpoint pada `aws_config.py`:

```python
LOCALSTACK_ENDPOINT = "http://localhost:4566"
```

Keduanya harus sama dengan port host yang digunakan.

## 10. Stop LocalStack

```bash
docker compose down
```

Jika ingin menghapus volume/data LocalStack juga:

```bash
docker compose down -v
```

> Perintah `down -v` akan menghapus data LocalStack yang disimpan di volume.
