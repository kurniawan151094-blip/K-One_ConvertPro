import streamlit as st
import io
import os
import time
import zipfile
import shutil
import tempfile
import subprocess
from PIL import Image
import requests
import streamlit.components.v1 as components

# Import WeasyPrint untuk HTML / Blog ke PDF
try:
    from weasyprint import HTML
    WEASYPRINT_OK = True
except Exception:
    WEASYPRINT_OK = False

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="K-ONE CONVERTPRO PDF",
    page_icon="📑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CUSTOM CSS (THEME: SUNSET FLAME & ELEGAN) =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stToolbarActions"], [data-testid="stStatusWidget"], .stDeployButton, #MainMenu { display: none !important; }

    /* TOMBOL HAMBURGER */
    [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {
        display: flex !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button, [data-testid="collapsedControl"] button {
        width: 48px !important;
        height: 48px !important;
        background: linear-gradient(135deg, #F97316, #EA580C) !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(234, 88, 12, 0.28) !important;
        transition: transform 0.2s ease !important;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover {
        transform: scale(1.05) !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg, [data-testid="collapsedControl"] svg {
        stroke: #ffffff !important;
        fill: #ffffff !important;
    }

    /* CONTAINER UTAMA */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 700px;
    }

    /* SIDEBAR CLEAN */
    .sidebar-brand-pill {
        display: inline-flex;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        border-radius: 999px;
        background: #FFF7ED;
        border: 1px solid #FFEDD5;
        color: #EA580C;
        margin-bottom: 6px;
    }
    .sidebar-brand-title {
        font-size: 1.45rem;
        font-weight: 900;
        background: linear-gradient(125deg, #F97316 0%, #DC2626 50%, #9333EA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.1rem;
    }
    [data-testid="stSidebar"] .stButton > button {
        font-size: 1.12rem !important;
        min-height: 58px !important;
        padding: 0.85rem 1.15rem !important;
        margin-bottom: 0.7rem !important;
        border-radius: 14px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease !important;
        border: 1px solid #E2E8F0 !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }
    [data-testid="stSidebar"] .stButton > button p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        gap: 11px !important;
        color: #334155 !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
        background: #FFF7ED !important;
        border: 1.5px solid #F97316 !important;
        box-shadow: 0 2px 8px rgba(249, 115, 22, 0.12) !important;
        transform: translateX(3px) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] p {
        color: #C2410C !important;
        font-weight: 800 !important;
    }

    /* HERO HEADER */
    .brand-hero { text-align: center; margin: 0.2rem 0 1rem 0; }
    .brand-pill {
        display: inline-block;
        padding: 4px 14px;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        border-radius: 999px;
        background: #FFF7ED;
        border: 1px solid #FFEDD5;
        color: #EA580C;
        margin-bottom: 6px;
    }
    .brand-title {
        font-size: 2.15rem;
        font-weight: 900;
        line-height: 1.15;
        background: linear-gradient(125deg, #F97316 0%, #DC2626 50%, #9333EA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-title .pro-badge {
        font-size: 0.88rem;
        vertical-align: super;
        margin-left: 6px;
        padding: 2px 8px;
        border-radius: 6px;
        background: linear-gradient(135deg, #EA580C, #F97316);
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    .brand-divider {
        width: 44px;
        height: 3.5px;
        background: linear-gradient(90deg, #F97316, #DC2626);
        border-radius: 99px;
        margin: 7px auto 9px auto;
    }
    .brand-sub {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        font-size: 0.84rem;
        color: #64748B;
        font-weight: 600;
        background: #F8FAFC;
        padding: 4px 14px;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
    }

    /* ================= 1. TOMBOL KONVERSI PRO (PRIMARY BUTTON) ================= */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #F97316 0%, #EA580C 50%, #DC2626 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        padding: 0.85rem 1.6rem !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.35) !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(234, 88, 12, 0.45) !important;
        color: #FFFFFF !important;
    }

    /* ================= 2. TOMBOL UNDUH BESAR (DOWNLOAD BUTTON) ================= */
    [data-testid="stDownloadButton"] {
        margin-top: 6px;
        margin-bottom: 10px;
    }
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #EA580C 0%, #C2410C 50%, #991B1B 100%) !important;
        color: #FFFFFF !important;
        font-size: 1.02rem !important;
        font-weight: 800 !important;
        padding: 0.85rem 1.6rem !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(194, 65, 12, 0.32) !important;
        transition: all 0.25s ease !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        letter-spacing: 0.3px !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(194, 65, 12, 0.48) !important;
        color: #FFFFFF !important;
    }

    /* TOMBOL UNDUH SATUAN DI DALAM KARTU */
    .download-card-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* ================= 3. HUD SPINNER MODAL (LOADING MUTER & PERSEN) ================= */
    .hud-overlay {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(6px) !important;
        -webkit-backdrop-filter: blur(6px) !important;
        z-index: 99999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .hud-card {
        background: #1E293B !important;
        border: 1.5px solid rgba(249, 115, 22, 0.35) !important;
        border-radius: 24px !important;
        padding: 28px 36px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 230px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 25px rgba(234, 88, 12, 0.2) !important;
        animation: hudPop 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }

    @keyframes hudPop {
        0% { transform: scale(0.85); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }

    .hud-spinner-wrap {
        position: relative !important;
        width: 84px !important;
        height: 84px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 14px !important;
    }

    .hud-spinner-ring {
        position: absolute !important;
        width: 100% !important;
        height: 100% !important;
        border-radius: 50% !important;
        border: 5px solid rgba(255, 255, 255, 0.08) !important;
        border-top: 5px solid #F97316 !important;
        border-right: 5px solid #EA580C !important;
        border-bottom: 5px solid #DC2626 !important;
        box-shadow: 0 0 14px rgba(249, 115, 22, 0.35) !important;
        animation: hudSpin 0.9s linear infinite !important;
    }

    @keyframes hudSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .hud-pct-text {
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        color: #F8FAFC !important;
        z-index: 2 !important;
    }

    .hud-msg-text {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #CBD5E1 !important;
        text-align: center !important;
        letter-spacing: 0.3px !important;
    }
</style>
""", unsafe_allow_html=True)


# ================= ROOT SLOT HUD SPINNER =================
hud_slot = st.empty()

def format_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    kb = size_bytes / 1024
    if kb >= 1024: return f"{kb / 1024:.2f} MB"
    return f"{kb:.2f} KB"

def show_download_loading(kategori="PDF", file_name=None):
    """Menampilkan lingkaran animasi berputar + persen dengan jeda mulus"""
    nama_item = f"'{file_name}'" if file_name else f"Berkas {kategori}"
    stages = [
        (15, f"Menyiapkan {nama_item}...", 0.35),
        (45, "Menyusun aliran PDF...", 0.45),
        (75, "Mengemas ke format akhir...", 0.5),
        (95, "Mengirim ke perangkat...", 0.4),
        (100, "Selesai!", 0.3)
    ]
    for pct, msg, delay in stages:
        clean_html = f'''
        <div class="hud-overlay">
            <div class="hud-card">
                <div class="hud-spinner-wrap">
                    <div class="hud-spinner-ring"></div>
                    <span class="hud-pct-text">{pct}%</span>
                </div>
                <div class="hud-msg-text">{msg}</div>
            </div>
        </div>'''
        hud_slot.markdown(clean_html, unsafe_allow_html=True)
        time.sleep(delay)
        
    hud_slot.empty()
    st.toast(f"🎉 {kategori} berhasil diunduh ke perangkat!", icon="✅")


# ================= HELPER DETEKSI LIBREOFFICE =================
def get_libreoffice_command():
    """Mendeteksi binary LibreOffice di Linux/Streamlit Cloud atau Windows"""
    if shutil.which("libreoffice"): return "libreoffice"
    if shutil.which("soffice"): return "soffice"
    win_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for p in win_paths:
        if os.path.exists(p): return p
    return None


# ================= FUNGSI ENGINE KONVERSI KE PDF =================

# 1. Gambar ke PDF
def convert_images_to_pdf(images_bytes_list):
    pil_images = []
    for raw in images_bytes_list:
        img = Image.open(io.BytesIO(raw))
        if img.mode != "RGB":
            img = img.convert("RGB")
        pil_images.append(img)
    if not pil_images:
        return None
    out_buf = io.BytesIO()
    pil_images[0].save(out_buf, format="PDF", save_all=True, append_images=pil_images[1:])
    return out_buf.getvalue()

# 2. Dokumen Office (Word, Excel, PPT) ke PDF via LibreOffice
def convert_office_to_pdf(file_bytes, filename):
    lo_cmd = get_libreoffice_command()
    if not lo_cmd:
        st.error("⚠️ Mesin LibreOffice belum terpasang di sistem. Di Streamlit Cloud, pastikan Anda sudah menambahkan `libreoffice` di file `packages.txt`.")
        return None

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, filename)
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        cmd = [lo_cmd, "--headless", "--convert-to", "pdf", input_path, "--outdir", temp_dir]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        base_name = os.path.splitext(filename)[0]
        output_pdf_path = os.path.join(temp_dir, f"{base_name}.pdf")

        if os.path.exists(output_pdf_path):
            with open(output_pdf_path, "rb") as f:
                return f.read()
    return None

# 3. HTML / Web Blog ke PDF
def convert_html_or_url_to_pdf(html_content=None, url=None):
    if not WEASYPRINT_OK:
        st.error("⚠️ Library WeasyPrint belum siap. Pastikan `weasyprint` tertera di file `requirements.txt`.")
        return None
    out_buf = io.BytesIO()
    if url:
        HTML(url=url).write_pdf(out_buf)
    elif html_content:
        HTML(string=html_content).write_pdf(out_buf)
    return out_buf.getvalue()


# ================= STATE MANAGEMENT =================
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "📸  Gambar ke PDF"

if "close_sidebar_trigger" not in st.session_state:
    st.session_state.close_sidebar_trigger = False

if st.session_state.close_sidebar_trigger:
    st.session_state.close_sidebar_trigger = False
    components.html("""
        <script>
            setTimeout(function() {
                try {
                    const parentDoc = window.parent.document;
                    const closeBtn = parentDoc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                                     parentDoc.querySelector('button[aria-label="Close sidebar"]');
                    if (closeBtn) closeBtn.click();
                } catch (e) {}
            }, 50);
        </script>
    """, height=0, width=0)


# ================= MENU SIDEBAR K-ONE =================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand-pill">⚡ UNIVERSAL CONVERTER</div>
        <div class="sidebar-brand-title">K-ONE MENU</div>
    """, unsafe_allow_html=True)

    daftar_menu = [
        ("📸  Gambar ke PDF", "btn_nav_img"),
        ("📝  Word ke PDF", "btn_nav_word"),
        ("📊  Excel ke PDF", "btn_nav_excel"),
        ("📽️  PowerPoint ke PDF", "btn_nav_ppt"),
        ("🌐  Blog & HTML ke PDF", "btn_nav_html")
    ]

    for label, key_btn in daftar_menu:
        is_active = (st.session_state.active_menu == label)
        tipe_tombol = "primary" if is_active else "secondary"
        if st.button(label, key=key_btn, use_container_width=True, type=tipe_tombol):
            st.session_state.active_menu = label
            st.session_state.close_sidebar_trigger = True
            st.rerun()


# ================= HEADER BANNER UTAMA =================
st.markdown(f"""
<div class="brand-hero">
    <div class="brand-pill">⚡ UNIVERSAL PDF CONVERTER</div><br>
    <div class="brand-title">K-ONE <span class="pro-badge">CONVERTPRO PDF</span></div>
    <div class="brand-divider"></div>
    <div class="brand-sub">
        <span>{st.session_state.active_menu} • Maksimal 500 MB per file</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ================= 1. MENU: GAMBAR KE PDF =================
if st.session_state.active_menu == "📸  Gambar ke PDF":
    files_img = st.file_uploader(
        "Upload Foto / Gambar (JPG, PNG, WebP) — Maks. 500 MB",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )
    if files_img:
        mode = st.radio(
            "Metode Konversi PDF:",
            ["Gabungkan SEMUA gambar menjadi 1 Dokumen PDF", "Konversi masing-masing gambar jadi file PDF terpisah (.zip)"]
        )

        if st.button("🚀 Mulai Konversi ke PDF", type="primary", use_container_width=True):
            if mode.startswith("Gabungkan"):
                with st.spinner("Menggabungkan gambar menjadi satu berkas PDF..."):
                    res = convert_images_to_pdf([f.getvalue() for f in files_img])
                    st.session_state.img_merged_pdf = res
                    st.session_state.img_zip_pdf = None
            else:
                with st.spinner("Mengonversi masing-masing gambar ke PDF..."):
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
                        for f in files_img:
                            pdf_b = convert_images_to_pdf([f.getvalue()])
                            z.writestr(f"{os.path.splitext(f.name)[0]}.pdf", pdf_b)
                    st.session_state.img_zip_pdf = zip_buf.getvalue()
                    st.session_state.img_merged_pdf = None

        # Tampilan Unduh Gambar ke PDF
        if st.session_state.get("img_merged_pdf"):
            data_pdf = st.session_state.img_merged_pdf
            st.success(f"🎉 Berhasil menyatukan {len(files_img)} gambar menjadi 1 PDF ({format_size(len(data_pdf))})")
            btn_dl_img = st.download_button(
                label=f"⬇️ UNDUH PDF GABUNGAN ({format_size(len(data_pdf))})",
                data=data_pdf,
                file_name="K-ONE_Gambar_Merged.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_img_merged"
            )
            if btn_dl_img:
                show_download_loading(kategori="PDF", file_name="K-ONE_Gambar_Merged.pdf")

        elif st.session_state.get("img_zip_pdf"):
            data_zip = st.session_state.img_zip_pdf
            st.success(f"🎉 Berhasil mengonversi {len(files_img)} gambar menjadi PDF terpisah!")
            btn_dl_zip = st.download_button(
                label=f"⬇️ UNDUH SEMUA ({len(files_img)} PDF) - ZIP ({format_size(len(data_zip))})",
                data=data_zip,
                file_name="K-ONE_Gambar_Bundle.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_img_zip"
            )
            if btn_dl_zip:
                show_download_loading(kategori="ZIP Bundle", file_name="K-ONE_Gambar_Bundle.zip")


# ================= 2. MENU: WORD KE PDF =================
elif st.session_state.active_menu == "📝  Word ke PDF":
    files_doc = st.file_uploader(
        "Upload Dokumen Word (.docx, .doc) — Maks. 500 MB",
        type=["docx", "doc"],
        accept_multiple_files=True
    )
    if files_doc and st.button("🚀 Konversi Dokumen Word ke PDF", type="primary", use_container_width=True):
        hasil_doc = []
        p_bar = st.progress(0)
        for i, f in enumerate(files_doc):
            with st.spinner(f"Mengonversi '{f.name}'..."):
                pdf_bytes = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_bytes:
                    hasil_doc.append((f"{os.path.splitext(f.name)[0]}.pdf", pdf_bytes))
            p_bar.progress((i + 1) / len(files_doc))
        st.session_state.doc_converted = hasil_doc

    if st.session_state.get("doc_converted"):
        docs = st.session_state.doc_converted
        st.success(f"🎉 Berhasil mengonversi {len(docs)} dokumen Word ke format PDF!")

        if len(docs) > 1:
            zip_buf_doc = io.BytesIO()
            with zipfile.ZipFile(zip_buf_doc, 'w', zipfile.ZIP_DEFLATED) as z:
                for name, d in docs: z.writestr(name, d)
            btn_zip_doc = st.download_button(
                label=f"⬇️ UNDUH SEMUA ({len(docs)} DOKUMEN PDF) - ZIP",
                data=zip_buf_doc.getvalue(),
                file_name="K-ONE_Word_Bundle.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_word_zip"
            )
            if btn_zip_doc:
                show_download_loading(kategori="ZIP Bundle", file_name="K-ONE_Word_Bundle.zip")

        with st.expander("📋 Rincian & Unduh Per File", expanded=True):
            for i, (name, data) in enumerate(docs):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"📄 **{name}**")
                    st.caption(f"Ukuran: {format_size(len(data))}")
                with c2:
                    btn_doc_item = st.download_button(
                        label="⬇️ Unduh",
                        data=data,
                        file_name=name,
                        mime="application/pdf",
                        key=f"dl_word_{i}",
                        use_container_width=True
                    )
                    if btn_doc_item:
                        show_download_loading(kategori="PDF", file_name=name)


# ================= 3. MENU: EXCEL KE PDF =================
elif st.session_state.active_menu == "📊  Excel ke PDF":
    files_xls = st.file_uploader(
        "Upload Dokumen Spreadsheet Excel (.xlsx, .xls) — Maks. 500 MB",
        type=["xlsx", "xls"],
        accept_multiple_files=True
    )
    if files_xls and st.button("🚀 Konversi Spreadsheet Excel ke PDF", type="primary", use_container_width=True):
        hasil_xls = []
        p_bar = st.progress(0)
        for i, f in enumerate(files_xls):
            with st.spinner(f"Merender lembar '{f.name}' ke PDF..."):
                pdf_bytes = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_bytes:
                    hasil_xls.append((f"{os.path.splitext(f.name)[0]}.pdf", pdf_bytes))
            p_bar.progress((i + 1) / len(files_xls))
        st.session_state.xls_converted = hasil_xls

    if st.session_state.get("xls_converted"):
        xlss = st.session_state.xls_converted
        st.success(f"🎉 Berhasil merender {len(xlss)} lembar kerja Excel ke PDF!")

        if len(xlss) > 1:
            zip_buf_xls = io.BytesIO()
            with zipfile.ZipFile(zip_buf_xls, 'w', zipfile.ZIP_DEFLATED) as z:
                for name, d in xlss: z.writestr(name, d)
            btn_zip_xls = st.download_button(
                label=f"⬇️ UNDUH SEMUA ({len(xlss)} PDF EXCEL) - ZIP",
                data=zip_buf_xls.getvalue(),
                file_name="K-ONE_Excel_Bundle.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_xls_zip"
            )
            if btn_zip_xls:
                show_download_loading(kategori="ZIP Bundle", file_name="K-ONE_Excel_Bundle.zip")

        with st.expander("📋 Rincian & Unduh Per File", expanded=True):
            for i, (name, data) in enumerate(xlss):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"📊 **{name}**")
                    st.caption(f"Ukuran: {format_size(len(data))}")
                with c2:
                    btn_xls_item = st.download_button(
                        label="⬇️ Unduh",
                        data=data,
                        file_name=name,
                        mime="application/pdf",
                        key=f"dl_xls_{i}",
                        use_container_width=True
                    )
                    if btn_xls_item:
                        show_download_loading(kategori="PDF", file_name=name)


# ================= 4. MENU: POWERPOINT KE PDF =================
elif st.session_state.active_menu == "📽️  PowerPoint ke PDF":
    files_ppt = st.file_uploader(
        "Upload Slide Presentasi (.pptx, .ppt) — Maks. 500 MB",
        type=["pptx", "ppt"],
        accept_multiple_files=True
    )
    if files_ppt and st.button("🚀 Konversi Slide Presentasi ke PDF", type="primary", use_container_width=True):
        hasil_ppt = []
        p_bar = st.progress(0)
        for i, f in enumerate(files_ppt):
            with st.spinner(f"Mengonversi slide '{f.name}'..."):
                pdf_bytes = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_bytes:
                    hasil_ppt.append((f"{os.path.splitext(f.name)[0]}.pdf", pdf_bytes))
            p_bar.progress((i + 1) / len(files_ppt))
        st.session_state.ppt_converted = hasil_ppt

    if st.session_state.get("ppt_converted"):
        ppts = st.session_state.ppt_converted
        st.success(f"🎉 Berhasil mengonversi {len(ppts)} presentasi PowerPoint ke PDF!")

        if len(ppts) > 1:
            zip_buf_ppt = io.BytesIO()
            with zipfile.ZipFile(zip_buf_ppt, 'w', zipfile.ZIP_DEFLATED) as z:
                for name, d in ppts: z.writestr(name, d)
            btn_zip_ppt = st.download_button(
                label=f"⬇️ UNDUH SEMUA ({len(ppts)} PDF PPT) - ZIP",
                data=zip_buf_ppt.getvalue(),
                file_name="K-ONE_PPT_Bundle.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_ppt_zip"
            )
            if btn_zip_ppt:
                show_download_loading(kategori="ZIP Bundle", file_name="K-ONE_PPT_Bundle.zip")

        with st.expander("📋 Rincian & Unduh Per File", expanded=True):
            for i, (name, data) in enumerate(ppts):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"📽️ **{name}**")
                    st.caption(f"Ukuran: {format_size(len(data))}")
                with c2:
                    btn_ppt_item = st.download_button(
                        label="⬇️ Unduh",
                        data=data,
                        file_name=name,
                        mime="application/pdf",
                        key=f"dl_ppt_{i}",
                        use_container_width=True
                    )
                    if btn_ppt_item:
                        show_download_loading(kategori="PDF", file_name=name)


# ================= 5. MENU: BLOG & HTML KE PDF =================
elif st.session_state.active_menu == "🌐  Blog & HTML ke PDF":
    pilihan_sumber = st.radio("Metode Konversi:", ["Tautan URL Artikel Blog / Web", "Upload File .html"], horizontal=True)

    if pilihan_sumber == "Tautan URL Artikel Blog / Web":
        url_blog = st.text_input("Masukkan URL Halaman / Artikel Web:", placeholder="https://id.wikipedia.org/wiki/Python")
        if st.button("🚀 Cetak Halaman Web ke PDF", type="primary", use_container_width=True):
            if url_blog.strip():
                with st.spinner("Mengunduh tampilan web dan menyusun PDF..."):
                    try:
                        pdf_data = convert_html_or_url_to_pdf(url=url_blog.strip())
                        st.session_state.web_pdf = pdf_data
                    except Exception as e:
                        st.error(f"Gagal memproses URL: {e}")
            else:
                st.warning("Mohon masukkan tautan URL terlebih dahulu.")

        if st.session_state.get("web_pdf"):
            data_web = st.session_state.web_pdf
            st.success(f"🎉 Halaman web berhasil dikonversi ke PDF ({format_size(len(data_web))})!")
            btn_dl_web = st.download_button(
                label=f"⬇️ UNDUH PDF ARTIKEL WEB ({format_size(len(data_web))})",
                data=data_web,
                file_name="K-ONE_Web_Article.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_web_pdf"
            )
            if btn_dl_web:
                show_download_loading(kategori="PDF", file_name="K-ONE_Web_Article.pdf")

    else:
        file_html = st.file_uploader("Upload File HTML (.html, .htm) — Maks. 500 MB", type=["html", "htm"])
        if file_html and st.button("🚀 Konversi File HTML ke PDF", type="primary", use_container_width=True):
            with st.spinner("Menyusun PDF dari kode HTML..."):
                try:
                    html_str = file_html.getvalue().decode("utf-8", errors="ignore")
                    pdf_data = convert_html_or_url_to_pdf(html_content=html_str)
                    st.session_state.html_file_pdf = (f"{os.path.splitext(file_html.name)[0]}.pdf", pdf_data)
                except Exception as e:
                    st.error(f"Gagal mengonversi file HTML: {e}")

        if st.session_state.get("html_file_pdf"):
            out_name, data_html_pdf = st.session_state.html_file_pdf
            st.success(f"🎉 File HTML berhasil dikonversi ke PDF ({format_size(len(data_html_pdf))})!")
            btn_dl_html = st.download_button(
                label=f"⬇️ UNDUH {out_name} ({format_size(len(data_html_pdf))})",
                data=data_html_pdf,
                file_name=out_name,
                mime="application/pdf",
                use_container_width=True,
                key="dl_html_file"
            )
            if btn_dl_html:
                show_download_loading(kategori="PDF", file_name=out_name)
