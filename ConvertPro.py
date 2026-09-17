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

# ================= CUSTOM CSS (CLEAN, MINIMALIS, SHARP) =================
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
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.25) !important;
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

    /* SIDEBAR CLEAN & MODERN */
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

    /* TOMBOL PROSES & UNDUH */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.75rem 1.4rem !important;
    }
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important;
        color: #FFFFFF !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25) !important;
    }

    /* HUD SPINNER OVERLAY */
    .hud-overlay {
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        width: 100vw !important; height: 100vh !important;
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(5px) !important;
        z-index: 99999999 !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
    }
    .hud-card {
        background: #1E293B !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 24px 32px !important;
        text-align: center;
        min-width: 220px;
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)


# ================= ROOT SLOT HUD =================
hud_slot = st.empty()

def format_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    kb = size_bytes / 1024
    if kb >= 1024: return f"{kb / 1024:.2f} MB"
    return f"{kb:.2f} KB"

def show_download_loading(label="Dokumen"):
    stages = [(20, "Membaca berkas...", 0.3), (60, "Menyusun struktur PDF...", 0.4), (100, "Siap diunduh!", 0.3)]
    for pct, msg, d in stages:
        hud_slot.markdown(f'''<div class="hud-overlay"><div class="hud-card">
            <h3 style="color:#F97316; margin:0 0 8px 0;">{pct}%</h3>
            <p style="margin:0; font-size:0.9rem;">{msg}</p>
        </div></div>''', unsafe_allow_html=True)
        time.sleep(d)
    hud_slot.empty()
    st.toast(f"🎉 {label} berhasil diunduh!", icon="✅")


# ================= HELPER DETEKSI LIBREOFFICE =================
def get_libreoffice_command():
    """Mendeteksi binary LibreOffice di Linux/Cloud atau Windows"""
    if shutil.which("libreoffice"): return "libreoffice"
    if shutil.which("soffice"): return "soffice"
    win_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for p in win_paths:
        if os.path.exists(p): return p
    return None


# ================= FUNGSI KONVERSI ENGINE =================

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
        st.error("⚠️ Mesin LibreOffice belum terpasang di sistem hosting/server. Pada Streamlit Cloud, pastikan sudah membuat file `packages.txt` berisi `libreoffice`.")
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
        st.error("⚠️ Library WeasyPrint belum siap. Pastikan `weasyprint` sudah terpasang di `requirements.txt`.")
        return None
    out_buf = io.BytesIO()
    if url:
        HTML(url=url).write_pdf(out_buf)
    elif html_content:
        HTML(string=html_content).write_pdf(out_buf)
    return out_buf.getvalue()


# ================= STATE NAVIGASI =================
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


# ================= SIDEBAR MENU =================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand-pill">⚡ UNIVERSAL CONVERTER</div>
        <div class="sidebar-brand-title">K-ONE CONVERTPRO</div>
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


# ================= HERO BANNER =================
st.markdown(f"""
<div class="brand-hero">
    <div class="brand-pill">⚡ UNIVERSAL PDF CONVERTER</div><br>
    <div class="brand-title">K-ONE <span class="pro-badge">CONVERTPRO PDF</span></div>
    <div class="brand-divider"></div>
    <div class="brand-sub">
        <span>{st.session_state.active_menu} • Dukung hingga 500 MB</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ================= 1. MENU: GAMBAR KE PDF =================
if st.session_state.active_menu == "📸  Gambar ke PDF":
    files_img = st.file_uploader(
        "Upload Foto / Gambar (JPG, PNG, WebP) — Maks. 500 MB per file",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )
    if files_img:
        mode = st.radio(
            "Pilihan Hasil PDF:",
            ["Gabungkan SEMUA gambar menjadi 1 file PDF", "Konversi masing-masing menjadi file PDF terpisah (.zip)"]
        )

        if st.button("🚀 Mulai Konversi ke PDF", type="primary", use_container_width=True):
            if mode.startswith("Gabungkan"):
                with st.spinner("Menggabungkan seluruh gambar ke dokumen PDF..."):
                    pdf_data = convert_images_to_pdf([f.getvalue() for f in files_img])
                    if pdf_data:
                        st.success(f"🎉 Berhasil menyatukan {len(files_img)} gambar menjadi 1 file PDF ({format_size(len(pdf_data))})")
                        btn_dl = st.download_button(
                            label=f"⬇️ Unduh PDF Gabungan ({format_size(len(pdf_data))})",
                            data=pdf_data,
                            file_name="K-ONE_Gambar_Merged.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        if btn_dl: show_download_loading("PDF")
            else:
                with st.spinner("Mengonversi berkas gambar satu per satu..."):
                    zip_buf = io.BytesIO()
                    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
                        for f in files_img:
                            pdf_bytes = convert_images_to_pdf([f.getvalue()])
                            out_name = f"{os.path.splitext(f.name)[0]}.pdf"
                            z.writestr(out_name, pdf_bytes)

                    st.download_button(
                        label=f"⬇️ DOWNLOAD SEMUA ({len(files_img)} PDF) - ZIP ({format_size(len(zip_buf.getvalue()))})",
                        data=zip_buf.getvalue(),
                        file_name="K-ONE_Images_Converted_PDF.zip",
                        mime="application/zip",
                        use_container_width=True
                    )


# ================= 2. MENU: WORD KE PDF =================
elif st.session_state.active_menu == "📝  Word ke PDF":
    files_doc = st.file_uploader(
        "Upload Dokumen Word (.docx, .doc) — Maks. 500 MB per file",
        type=["docx", "doc"],
        accept_multiple_files=True
    )
    if files_doc and st.button("🚀 Konversi Dokumen Word ke PDF", type="primary", use_container_width=True):
        list_pdf = []
        progress_bar = st.progress(0)
        for idx, f in enumerate(files_doc):
            with st.spinner(f"Mengonversi '{f.name}' ke PDF..."):
                pdf_bytes = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_bytes:
                    list_pdf.append((f"{os.path.splitext(f.name)[0]}.pdf", pdf_bytes))
            progress_bar.progress((idx + 1) / len(files_doc))

        if list_pdf:
            st.success(f"🎉 Berhasil mengonversi {len(list_pdf)} dokumen Word ke PDF!")
            if len(list_pdf) > 1:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
                    for name, data in list_pdf: z.writestr(name, data)
                st.download_button(
                    label=f"⬇️ DOWNLOAD SEMUA ({len(list_pdf)} PDF) - ZIP",
                    data=zip_buf.getvalue(),
                    file_name="K-ONE_Word_Converted_PDF.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            for name, data in list_pdf:
                st.download_button(f"⬇️ Unduh {name} ({format_size(len(data))})", data=data, file_name=name, mime="application/pdf", key=name)


# ================= 3. MENU: EXCEL KE PDF =================
elif st.session_state.active_menu == "📊  Excel ke PDF":
    files_xls = st.file_uploader(
        "Upload Dokumen Spreadsheet Excel (.xlsx, .xls) — Maks. 500 MB",
        type=["xlsx", "xls"],
        accept_multiple_files=True
    )
    if files_xls and st.button("🚀 Konversi Spreadsheet Excel ke PDF", type="primary", use_container_width=True):
        list_pdf = []
        progress_bar = st.progress(0)
        for idx, f in enumerate(files_xls):
            with st.spinner(f"Merender lembar '{f.name}' ke format PDF..."):
                pdf_bytes = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_bytes:
                    list_pdf.append((f"{os.path.splitext(f.name)[0]}.pdf", pdf_bytes))
            progress_bar.progress((idx + 1) / len(files_xls))

        if list_pdf:
            st.success(f"🎉 Berhasil mengonversi {len(list_pdf)} file Excel ke PDF!")
            if len(list_pdf) > 1:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
                    for name, data in list_pdf: z.writestr(name, data)
                st.download_button(
                    label=f"⬇️ DOWNLOAD SEMUA ({len(list_pdf)} PDF) - ZIP",
                    data=zip_buf.getvalue(),
                    file_name="K-ONE_Excel_Converted_PDF.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            for name, data in list_pdf:
                st.download_button(f"⬇️ Unduh {name} ({format_size(len(data))})", data=data, file_name=name, mime="application/pdf", key=name)


# ================= 4. MENU: POWERPOINT KE PDF =================
elif st.session_state.active_menu == "📽️  PowerPoint ke PDF":
    files_ppt = st.file_uploader(
        "Upload Presentasi Slide (.pptx, .ppt) — Maks. 500 MB",
        type=["pptx", "ppt"],
        accept_multiple_files=True
    )
    if files_ppt and st.button("🚀 Konversi Slide Presentasi ke PDF", type="primary", use_container_width=True):
        list_pdf = []
        progress_bar = st.progress(0)
        for idx, f in enumerate(files_ppt):
            with st.spinner(f"Mengonversi slide '{f.name}' ke PDF..."):
                pdf_bytes = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_bytes:
                    list_pdf.append((f"{os.path.splitext(f.name)[0]}.pdf", pdf_bytes))
            progress_bar.progress((idx + 1) / len(files_ppt))

        if list_pdf:
            st.success(f"🎉 Berhasil mengonversi {len(list_pdf)} presentasi PowerPoint ke PDF!")
            if len(list_pdf) > 1:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
                    for name, data in list_pdf: z.writestr(name, data)
                st.download_button(
                    label=f"⬇️ DOWNLOAD SEMUA ({len(list_pdf)} PDF) - ZIP",
                    data=zip_buf.getvalue(),
                    file_name="K-ONE_PPT_Converted_PDF.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            for name, data in list_pdf:
                st.download_button(f"⬇️ Unduh {name} ({format_size(len(data))})", data=data, file_name=name, mime="application/pdf", key=name)


# ================= 5. MENU: BLOG & HTML KE PDF =================
elif st.session_state.active_menu == "🌐  Blog & HTML ke PDF":
    pilihan_sumber = st.radio("Metode Konversi:", ["Tautan URL Artikel Blog / Web", "Upload File .html"], horizontal=True)

    if pilihan_sumber == "Tautan URL Artikel Blog / Web":
        url_blog = st.text_input("Masukkan URL Halaman / Artikel Web:", placeholder="https://id.wikipedia.org/wiki/Python")
        if st.button("🚀 Konversi Halaman Web ke PDF", type="primary", use_container_width=True):
            if url_blog.strip():
                with st.spinner("Mengunduh halaman dan menyusun PDF..."):
                    try:
                        pdf_data = convert_html_or_url_to_pdf(url=url_blog.strip())
                        if pdf_data:
                            st.success(f"🎉 Halaman berhasil dicetak ke PDF ({format_size(len(pdf_data))})")
                            st.download_button("⬇️ Unduh PDF Artikel", data=pdf_data, file_name="K-ONE_Web_Article.pdf", mime="application/pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"Gagal mengonversi URL: {e}")
            else:
                st.warning("Mohon masukkan tautan URL terlebih dahulu.")
    else:
        file_html = st.file_uploader("Upload File HTML (.html, .htm) — Maks. 500 MB", type=["html", "htm"])
        if file_html and st.button("🚀 Konversi File HTML ke PDF", type="primary", use_container_width=True):
            with st.spinner("Memproses kode HTML ke PDF..."):
                try:
                    html_str = file_html.getvalue().decode("utf-8", errors="ignore")
                    pdf_data = convert_html_or_url_to_pdf(html_content=html_str)
                    if pdf_data:
                        out_fname = f"{os.path.splitext(file_html.name)[0]}.pdf"
                        st.success(f"🎉 Berhasil dikonversi ke PDF ({format_size(len(pdf_data))})")
                        st.download_button(f"⬇️ Unduh {out_fname}", data=pdf_data, file_name=out_fname, mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"Gagal mengonversi file HTML: {e}")
