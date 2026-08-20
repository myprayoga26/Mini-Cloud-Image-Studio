import io
from datetime import datetime, timezone

import streamlit as st
from PIL import Image

from aws_config import ensure_resources
from dynamodb_utils import delete_metadata, list_metadata, put_metadata
from image_utils import grayscale_image, image_to_bytes, resize_image
from s3_utils import delete_object, download_bytes, upload_bytes


st.set_page_config(
    page_title="Mini Cloud Image Studio",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0');
    :root { --surface:#f8faf8; --white:#fff; --text:#1f2937; --variant:#64748b; --outline:#e2e8e2; --primary:#087a2e; --primary-container:#0a8f3a; --sidebar:#087a2e; --active:#7be495; --accent:#e8f5e9; --success:#22c55e; }
    html, body, [class*="css"] { font-family:'Inter',sans-serif; }
    .stApp { background:var(--surface); color:var(--text); }
    header[data-testid="stHeader"], .stApp > header { display:none !important; }
    .block-container { max-width:1250px; padding-top:24px; padding-bottom:48px; padding-left:32px; padding-right:32px; }
    section[data-testid="stSidebar"] { background:var(--sidebar) !important; min-width:260px !important; max-width:260px !important; }
    section[data-testid="stSidebar"] > div { padding:0 18px 20px; }
    section[data-testid="stSidebar"] * { font-family:'Inter',sans-serif; }
    .sidebar-brand { display:flex; align-items:center; gap:12px; height:70px; padding:0 4px; margin-bottom:18px; white-space:nowrap; }
    .sidebar-logo { width:46px; height:46px; border-radius:8px; background:#fff; display:flex; align-items:center; justify-content:center; font-size:24px; flex:0 0 46px; }
    .sidebar-brand-title { color:#fff !important; font-size:22px; line-height:26px; font-weight:700; white-space:nowrap; }
    .sidebar-brand-subtitle, .sidebar-version { color:#fff !important; opacity:1 !important; font-size:11px; line-height:14px; white-space:nowrap; }
    section[data-testid="stSidebar"] div.stButton { margin:3px 0; }
    section[data-testid="stSidebar"] div.stButton > button { width:100%; min-height:36px; height:36px; border:0 !important; border-radius:8px !important; background:transparent !important; color:#fff !important; text-align:left !important; justify-content:flex-start !important; align-items:center !important; flex-direction:row !important; padding:7px 20px !important; font-size:12px !important; font-weight:500 !important; box-shadow:none !important; opacity:1 !important; gap:12px !important; white-space:nowrap !important; }
    div[data-testid="stSidebar"] button { justify-content:flex-start !important; text-align:left !important; padding-left:1rem !important; }
    div[data-testid="stSidebar"] button > div { justify-content:flex-start !important; width:100% !important; }
    .sidebar-menu-item {
        display:flex;
        align-items:center;
        justify-content:flex-start;
        width:100%;
        text-align:left;
        padding-left:12px;
    }
    .sidebar-menu-item .icon {
        width:18px;
        min-width:18px;
        display:flex;
        justify-content:center;
        flex-shrink:0;
    }
    .sidebar-menu-item .label {
        margin-left:10px;
        text-align:left;
    }
    section[data-testid="stSidebar"] div.stButton > button > div,
    section[data-testid="stSidebar"] div.stButton > button [data-testid="stMarkdownContainer"] {
        display:flex !important;
        align-items:center !important;
        justify-content:flex-start !important;
        width:100% !important;
        text-align:left !important;
    }
    section[data-testid="stSidebar"] div.stButton > button p {
        margin:0 !important;
        text-align:left !important;
        flex:1 1 auto !important;
    }
    section[data-testid="stSidebar"] div.stButton > button [data-testid="stIconMaterial"] { display:inline-flex !important; align-items:center !important; justify-content:center !important; flex:0 0 18px !important; font-family:'Material Symbols Rounded' !important; font-size:18px !important; width:18px !important; min-width:18px !important; color:#fff !important; line-height:1 !important; }
    section[data-testid="stSidebar"] div.stButton > button *, section[data-testid="stSidebar"] div.stButton > button p, section[data-testid="stSidebar"] div.stButton > button span { color:#fff !important; opacity:1 !important; }
    section[data-testid="stSidebar"] div.stButton > button:hover { background:#0a8f3a !important; color:#fff !important; }
    section[data-testid="stSidebar"] div.stButton > button:hover * { color:#fff !important; }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * { color:#fff !important; }
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        display:none !important;
        height:0 !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] span {
        display:none !important;
        visibility:hidden !important;
        opacity:0 !important;
        width:0 !important;
        height:0 !important;
        min-width:0 !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 !important;
        pointer-events:none !important;
    }
    .sidebar-bottom { border-top:1px solid rgba(232,245,233,.35); margin:16px 20px 0; padding-top:12px; }
    .sidebar-version { font-family:'JetBrains Mono',monospace; padding:14px 20px 0; text-align:left; }
    .topbar { height:70px; box-sizing:border-box; background:#fff; border-bottom:1px solid #e2e8e2; display:flex; align-items:center; justify-content:space-between; padding:0 20px; margin:0 -1rem 24px; }
    .dashboard-title { color:var(--primary); font-size:22px; font-weight:700; transition:transform .2s ease,color .2s ease; }
    .dashboard-title:hover { color:var(--primary-container); transform:translateX(4px); }
    .topbar-actions { display:flex; align-items:center; gap:16px; color:var(--variant); }
    .topbar-icon { font-family:'Material Symbols Rounded',sans-serif; font-size:18px; font-weight:400; line-height:1; color:#404040; cursor:pointer; transition:transform 0.2s ease; background:transparent; border:0; }
    .topbar-icon:hover { transform:translateY(-3px); }
    .profile-avatar { width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; background:var(--primary-container); color:#fff; font-size:13px; font-weight:700; transition:transform .2s ease; }
    .profile-avatar:hover { transform:scale(1.1); }
    .upload-section { background:#fff; border:2px dashed var(--outline); border-radius:12px; box-shadow:0 4px 12px rgba(0,60,0,.05); min-height:260px; box-sizing:border-box; padding:40px 32px; text-align:center; margin-bottom:24px; }
    .upload-icon { width:64px; height:64px; border-radius:50%; background:var(--primary-container); color:#e8f5e9; display:flex; align-items:center; justify-content:center; margin:0 auto 16px; font-size:30px; transition:transform .2s ease,box-shadow .2s ease; }
    .upload-icon:hover { transform:translateY(-5px) scale(1.06); box-shadow:0 8px 18px rgba(8,122,46,.25); }
    .upload-title { font-size:24px; line-height:32px; font-weight:600; margin-bottom:8px; }
    .upload-subtitle { color:var(--variant); font-size:14px; line-height:20px; margin-bottom:18px; }
    [data-testid="stFileUploader"] { margin-top:-18px; }
    [data-testid="stFileUploaderDropzone"] { background:transparent !important; border:0 !important; min-height:50px !important; }
    [data-testid="stFileUploaderDropzone"] > div { background:transparent !important; justify-content:center !important; }
    [data-testid="stFileUploaderDropzone"] button { background:var(--primary) !important; color:#fff !important; border:0 !important; border-radius:8px !important; margin:0 auto !important; transition:transform 0.2s ease !important; }
    [data-testid="stFileUploaderDropzone"] button:hover { transform:translateY(-3px); }
    .section-title { font-size:22px; line-height:30px; font-weight:700; }
    .activity-head { display:flex; align-items:center; justify-content:space-between; margin:48px 0 20px; padding-bottom:12px; border-bottom:1px solid #e2e8e2; }
    .activity-link { color:var(--primary); font-size:12px; font-weight:600; }
    .panel { background:#fff; border:1px solid #e2e8e2; border-radius:12px; box-shadow:0 4px 12px rgba(8,122,46,.06); padding:24px; }
    .panel-title { color:var(--primary); font-size:18px; font-weight:700; margin-bottom:12px; }
    .image-card { background:#fff; border:1px solid #e2e8e2; border-radius:10px; overflow:hidden; margin-bottom:24px; box-shadow:0 4px 12px rgba(0,60,0,.05); min-width:0; height:100%; }
    .image-card-title { font-size:14px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    div[data-testid="stHorizontalBlock"] { gap:16px !important; }
    .image-card [data-testid="stImage"] { width:100% !important; height:190px !important; overflow:hidden !important; }
    .image-card [data-testid="stImage"] > div { width:100% !important; height:100% !important; }
    .image-card [data-testid="stImage"] img { display:block !important; width:100% !important; height:190px !important; aspect-ratio:4 / 3; object-fit:cover; border-radius:0; }
    .image-card > div[style*="padding"] { min-height:86px; box-sizing:border-box; }
    @media (max-width:900px) {
        section[data-testid="stSidebar"] { min-width:220px !important; max-width:220px !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { flex:1 1 calc(50% - 8px) !important; min-width:calc(50% - 8px) !important; }
        .image-card [data-testid="stImage"], .image-card [data-testid="stImage"] img { height:170px !important; }
    }
    @media (max-width:640px) {
        section[data-testid="stSidebar"] { min-width:190px !important; max-width:190px !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { flex:1 1 100% !important; min-width:100% !important; }
        .dashboard-title { font-size:18px; }
        .image-card [data-testid="stImage"], .image-card [data-testid="stImage"] img { height:180px !important; }
    }
    .meta-chip { display:inline-block; padding:5px 10px; border-radius:9999px; background:#e8f5e9; color:var(--variant); font-size:13px; margin:8px 6px 0 0; }
    .meta-chip-green { background:var(--primary-container); color:#fff; }
    div.stButton > button, div.stDownloadButton > button { border-radius:8px !important; min-height:40px; font-weight:600; }
    div.stDownloadButton > button { background:#e8f5e9 !important; color:#1f2937 !important; border:1px solid #e2e8e2 !important; transition:transform .2s ease,box-shadow .2s ease,background .2s ease !important; }
    div.stDownloadButton > button *, div.stDownloadButton > button p, div.stDownloadButton > button span { color:#1f2937 !important; opacity:1 !important; }
    div.stDownloadButton > button:hover { background:#d1f2d8 !important; color:#1f2937 !important; transform:translateY(-1px); box-shadow:0 4px 10px rgba(8,122,46,.16); }
    div.stDownloadButton > button:hover *, div.stDownloadButton > button:hover p, div.stDownloadButton > button:hover span { color:#1f2937 !important; }
    div.stButton > button:not([kind="primary"]) { background:#e8f5e9 !important; color:#1f2937 !important; border:1px solid #e2e8e2 !important; }
    div.stButton > button:not([kind="primary"]) *, div.stButton > button:not([kind="primary"]) p, div.stButton > button:not([kind="primary"]) span { color:#1f2937 !important; opacity:1 !important; }
    div.stButton > button:not([kind="primary"]):hover { background:#d1f2d8 !important; color:#1f2937 !important; transform:translateY(-1px); box-shadow:0 4px 10px rgba(8,122,46,.16); }
    div.stButton > button:not([kind="primary"]):hover *, div.stButton > button:not([kind="primary"]):hover p, div.stButton > button:not([kind="primary"]):hover span { color:#1f2937 !important; }
    div.stButton > button[kind="primary"] { background:var(--primary) !important; color:#fff !important; border-color:var(--primary) !important; transition:transform .2s ease,box-shadow .2s ease,background .2s ease !important; }
    div.stButton > button[kind="primary"] *, div.stButton > button[kind="primary"] p, div.stButton > button[kind="primary"] span { color:#fff !important; opacity:1 !important; }
    div.stButton > button[kind="primary"]:hover:not(:disabled) { background:var(--primary-container) !important; transform:translateY(-2px); box-shadow:0 6px 14px rgba(8,122,46,.28); }
    div.stButton > button[kind="primary"]:disabled { opacity:.78; cursor:wait; animation:save-success-zoom .35s ease-out; }
    @keyframes save-success-zoom { 0%{transform:scale(.92)} 70%{transform:scale(1.04)} 100%{transform:scale(1)} }
    .footer { margin-top:48px; padding-top:18px; border-top:1px solid #e2e8e2; color:var(--variant); font-size:13px; display:flex; justify-content:space-between; }
    </style>
    """,
    unsafe_allow_html=True,
)


def human_size(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return "0 B"
    if value < 1024:
        return f"{value} B"
    if value < 1024**2:
        return f"{value / 1024:.1f} KB"
    return f"{value / (1024**2):.2f} MB"


def records():
    try:
        return sorted(list_metadata(), key=lambda item: item.get("timestamp", ""), reverse=True)
    except Exception:
        return []


def save_metadata(image_id, filename, file_size, content_type, filter_type, s3_key, width, height, parent_image_id=None):
    item = {"image_id":image_id, "filename":filename, "file_size":str(file_size), "content_type":content_type, "filter_type":filter_type, "s3_key":s3_key, "timestamp":datetime.now(timezone.utc).isoformat(), "width":str(width), "height":str(height)}
    if parent_image_id:
        item["parent_image_id"] = parent_image_id
    put_metadata(item)


def load_image(item):
    return Image.open(io.BytesIO(download_bytes(item["s3_key"]))).convert("RGB")


def save_processed(source, result, operation, output_format):
    fmt = output_format.upper()
    if fmt == "JPEG":
        result = result.convert("RGB")
    data = image_to_bytes(result, fmt)
    ext, content_type = {"PNG":("png","image/png"),"JPEG":("jpg","image/jpeg"),"WEBP":("webp","image/webp")}[fmt]
    filename = f"{operation}_{source['filename'].rsplit('.', 1)[0]}.{ext}"
    s3_key, image_id = upload_bytes(data, filename, content_type, folder=f"edited/{operation}")
    save_metadata(image_id, filename, len(data), content_type, operation, s3_key, result.width, result.height, source["image_id"])
    return image_id


def upload_original(uploaded):
    image = Image.open(uploaded).convert("RGB")
    s3_key, image_id = upload_bytes(uploaded.getvalue(), uploaded.name, uploaded.type or "application/octet-stream", folder="uploads")
    save_metadata(image_id, uploaded.name, uploaded.size, uploaded.type or "application/octet-stream", "original", s3_key, image.width, image.height)


localstack_ok = True
try:
    ensure_resources()
except Exception:
    localstack_ok = False

if "page" not in st.session_state:
    st.session_state.page = "Studio"

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="sidebar-logo">☁️</div><div><div class="sidebar-brand-title">Cloud Studio</div><div class="sidebar-brand-subtitle">V2.4.0 High-Efficiency</div></div></div>', unsafe_allow_html=True)
    if st.button("Proyek Baru", icon=":material/add:", type="primary", use_container_width=True, key="new_project"):
        st.session_state.page = "Studio"; st.rerun()
    for label, icon, page, key in [
        ("Unggah", ":material/cloud_upload:", "Upload", "nav_upload_short"),
        ("Grayscale gambar", ":material/tune:", "Grayscale", "nav_filter"),
        ("Resize gambar", ":material/diamond:", "Resize", "nav_batch"),
        ("Ekspor", ":material/download:", "History", "nav_export"),
        ("Upload gambar ke S3", ":material/cloud:", "Upload", "nav_upload"),
        ("Daftar Gambar", ":material/list_alt:", "History", "nav_history"),
    ]:
        if st.button(label, icon=icon, use_container_width=True, key=key):
            st.session_state.page = page; st.rerun()
    st.markdown('<div class="sidebar-bottom"></div>', unsafe_allow_html=True)
    if st.button("Bantuan", icon=":material/help_outline:", use_container_width=True, key="nav_help"):
        st.session_state.page = "Help"; st.rerun()
    if st.button("Kembali ke Studio", icon=":material/keyboard_return:", use_container_width=True, key="nav_exit"):
        st.session_state.page = "Studio"; st.rerun()
    st.markdown('<div class="sidebar-version">LOCALSTACK • S3 • DYNAMODB</div>', unsafe_allow_html=True)

st.markdown('<div class="topbar"><div class="dashboard-title">Studio Dashboard</div><div class="topbar-actions"><span class="topbar-icon" aria-label="Notifikasi">notifications</span><span class="topbar-icon" aria-label="Pengaturan">settings</span><span class="profile-avatar">MC</span></div></div>', unsafe_allow_html=True)

if st.session_state.page == "Studio":
    st.markdown('<section class="upload-section"><div class="upload-icon">☁️</div><div class="upload-title">Tarik &amp; Lepas Gambar Disini</div><div class="upload-subtitle">Mendukung JPG, PNG, WEBP hingga 20 MB</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Pilih File", type=["jpg","jpeg","png","webp"], label_visibility="collapsed", key="dashboard_upload")
    st.markdown("</section>", unsafe_allow_html=True)
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        left, right = st.columns([1.4,.8])
        with left: st.image(image, caption=f"{uploaded.name} • {image.width} × {image.height}px", use_container_width=True)
        with right:
            st.markdown('<div class="panel"><div class="panel-title">File siap diproses</div>', unsafe_allow_html=True)
            st.write(f"**Nama:** `{uploaded.name}`"); st.write(f"**Ukuran:** `{human_size(uploaded.size)}`")
            if st.button("☁️ Upload gambar ke S3", type="primary", use_container_width=True, key="dashboard_upload_s3"):
                try:
                    with st.spinner("Menyimpan..."): upload_original(uploaded)
                    st.toast("File berhasil disimpan ke S3", icon="✅"); st.success("Upload berhasil."); st.rerun()
                except Exception as exc: st.error(f"Upload gagal: {exc}")
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="activity-head"><div class="section-title">Aktivitas Studio Terbaru</div><div class="activity-link">Lihat Semua →</div></div>', unsafe_allow_html=True)
    items = records()
    if not items: st.info("Belum ada gambar tersimpan. Upload gambar untuk memulai.")
    else:
        cols = st.columns(3)
        for index, item in enumerate(items[:6]):
            with cols[index % 3]:
                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                try: st.image(download_bytes(item["s3_key"]), use_container_width=True)
                except Exception: st.warning("Preview tidak tersedia.")
                filename = item.get("filename", "-")
                st.markdown(f'<div style="padding:16px"><div class="image-card-title">{filename}</div><span class="meta-chip">{human_size(item.get("file_size",0))}</span><span class="meta-chip meta-chip-green">{item.get("filter_type","original")}</span></div>', unsafe_allow_html=True)
                try: st.download_button("⬇ Download", data=download_bytes(item["s3_key"]), file_name=filename, mime=item.get("content_type","image/png"), key=f"dash_download_{item['image_id']}", use_container_width=True)
                except Exception: st.error("Download gagal.")
                if st.button("🗑 Hapus", type="primary", key=f"dash_delete_{item['image_id']}", use_container_width=True):
                    try: delete_object(item["s3_key"]); delete_metadata(item["image_id"]); st.rerun()
                    except Exception as exc: st.error(f"Gagal menghapus: {exc}")
                st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Upload":
    st.markdown('<div class="section-title">Upload gambar ke S3</div>', unsafe_allow_html=True); st.write("Simpan gambar ke LocalStack S3 dan metadata file ke DynamoDB.")
    uploaded = st.file_uploader("Pilih gambar", type=["jpg","jpeg","png","webp"], key="upload_page")
    if uploaded:
        image = Image.open(uploaded).convert("RGB"); left, right = st.columns([1.2,.8])
        with left: st.image(image, caption=f"{uploaded.name} • {image.width} × {image.height}px", use_container_width=True)
        with right:
            st.markdown('<div class="panel"><div class="panel-title">Informasi File</div>', unsafe_allow_html=True); st.write(f"Nama: `{uploaded.name}`"); st.write(f"Ukuran: `{human_size(uploaded.size)}`"); st.write(f"Format: `{uploaded.type}`"); st.write(f"Dimensi: `{image.width} × {image.height}px`")
            if st.button("☁️ Simpan ke S3", type="primary", use_container_width=True, key="upload_page_save"):
                try:
                    with st.spinner("Menyimpan..."): upload_original(uploaded)
                    st.toast("File berhasil disimpan ke S3", icon="✅"); st.success("✓ Berhasil Disimpan"); st.rerun()
                except Exception as exc: st.toast("Gagal Menyimpan", icon="❌"); st.error(f"Upload gagal: {exc}")
            st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page in {"Grayscale", "Resize"}:
    operation = "grayscale" if st.session_state.page == "Grayscale" else "resize"
    st.markdown(f'<div class="section-title">{operation.title()} gambar</div>', unsafe_allow_html=True); st.write("Ubah gambar tersimpan dan simpan hasilnya sebagai object baru di S3.")
    items = records()
    if not items: st.info("Belum ada gambar. Upload gambar terlebih dahulu.")
    else:
        labels = [f'{x.get("filename","-")} • {x.get("filter_type","original")} • {x.get("image_id","")[:8]}' for x in items]
        selected = items[labels.index(st.selectbox("Pilih gambar", labels))]; source = load_image(selected)
        left, right = st.columns([1.15,.85])
        with left: st.image(source, caption="Gambar sumber", use_container_width=True)
        with right:
            if operation == "grayscale":
                result = grayscale_image(source).convert("RGB"); st.image(result, caption="Preview grayscale", use_container_width=True)
            else:
                keep_ratio = st.checkbox("Pertahankan rasio aspek", value=True); width = st.slider("Lebar", 50, 2000, min(source.width,1200), 10)
                if keep_ratio: height = max(50, int(width * (source.height / source.width if source.width else 1))); st.caption(f"Tinggi otomatis: {height}px")
                else: height = st.slider("Tinggi", 50, 2000, min(source.height,1200), 10)
                result = resize_image(source, width, height); st.image(result, caption=f"Preview {width} × {height}px", use_container_width=True)
            fmt = st.selectbox("Format hasil", ["PNG","JPEG","WEBP"], key=f"{operation}_output")
            label = "⚫ Simpan Grayscale ke S3" if operation == "grayscale" else "📐 Simpan Resize ke S3"
            if st.button(label, type="primary", use_container_width=True, key=f"{operation}_save_s3"):
                try:
                    with st.spinner("Menyimpan..."): save_processed(selected, result, operation, fmt)
                    st.toast(f"File {operation} berhasil disimpan ke S3", icon="✅"); st.success("✓ Berhasil Disimpan"); st.rerun()
                except Exception as exc: st.toast("Gagal Menyimpan", icon="❌"); st.error(f"Gagal menyimpan: {exc}")

elif st.session_state.page == "History":
    st.markdown('<div class="section-title">Daftar Gambar</div>', unsafe_allow_html=True); st.write("Kumpulan gambar yang tersimpan di Cloud Image Studio.")
    items = records(); search = st.text_input("🔎 Cari nama file", placeholder="contoh: foto.png")
    if search: items = [x for x in items if search.lower() in x.get("filename","").lower()]
    if not items: st.info("Belum ada gambar tersimpan.")
    else:
        cols = st.columns(3)
        for index, item in enumerate(items):
            with cols[index % 3]:
                st.markdown('<div class="image-card">', unsafe_allow_html=True); filename = item.get("filename","-")
                try: st.image(download_bytes(item["s3_key"]), use_container_width=True)
                except Exception: st.warning("Preview tidak tersedia.")
                st.markdown(f'<div style="padding:16px"><div class="image-card-title">{filename}</div><span class="meta-chip">{human_size(item.get("file_size",0))}</span><span class="meta-chip meta-chip-green">{item.get("filter_type","original")}</span></div>', unsafe_allow_html=True)
                try: st.download_button("⬇ Download gambar", data=download_bytes(item["s3_key"]), file_name=filename, mime=item.get("content_type","image/png"), key=f"history_download_{item['image_id']}", use_container_width=True)
                except Exception: st.error("Download tidak tersedia.")
                if st.button("🗑 Hapus dari S3 + DynamoDB", type="primary", key=f"history_delete_{item['image_id']}", use_container_width=True):
                    try: delete_object(item["s3_key"]); delete_metadata(item["image_id"]); st.rerun()
                    except Exception as exc: st.error(f"Gagal menghapus: {exc}")
                st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "Help":
    st.markdown('<div class="section-title">Bantuan</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Cara kerja Cloud Image Studio</div><p><b>1. Unggah</b><br>Pilih gambar lalu upload ke LocalStack S3. Metadata gambar otomatis disimpan di DynamoDB.</p><p><b>2. Grayscale gambar</b><br>Ubah gambar menjadi grayscale menggunakan filter, lalu simpan hasilnya sebagai versi baru.</p><p><b>3. Resize gambar</b><br>Atur ukuran lebar dan tinggi gambar, lalu simpan hasil resize sebagai versi baru.</p><p><b>4. Ekspor</b><br>Unduh gambar yang tersimpan dengan format output yang tersedia.</p><p><b>5. Upload gambar ke S3</b><br>Simpan gambar ke LocalStack S3 pada penyimpanan khusus dan catat metadata secara otomatis di DynamoDB.</p><p><b>6. Daftar Gambar</b><br>Lihat seluruh koleksi gambar yang tersimpan di S3 beserta metadata seperti nama file, ukuran, format, dan resolusi.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="footer"><span>☁️ Mini Cloud Image Studio</span><span>S3 + DynamoDB • LocalStack</span><span>Streamlit • Pillow • boto3</span></div>', unsafe_allow_html=True)
