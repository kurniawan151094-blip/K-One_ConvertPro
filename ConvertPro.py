import streamlit as st
import io
import os
import subprocess
import tempfile
import zipfile
import shutil
from PIL import Image
import requests
from weasyprint import HTML

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="ConvertPro - Universal PDF Converter",
    page_icon="📑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    header[data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stToolbarActions"], [data-testid="stStatusWidget"], .stDeployButton, #MainMenu { display: none !important; }

    /* TOMBOL HAMBURGER SIDEBAR */
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
        background: linear-gradient(135deg, #0284C7, #2563EB) !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4) !important;
    }
    
    .brand-hero { text-align: center; margin: 0.5rem 0 1.2rem 0; }
    .brand-title {
        font-size: 2.3rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        background: linear-gradient(125deg, #0284C7 0%, #6366F1 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-pill {
        display: inline-block;
        padding: 3px 12px;
        font-size: 0.72rem;
        font-weight: 800;
        border-radius: 999px;
        background: rgba(99, 102, 241, 0.12);
        color: #6366F1;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ================= HELPER DETEKSI LIBREOFFICE =================
def get_libreoffice_command():
    """Mendeteksi path LibreOffice di Windows atau Linux/Mac"""
    if shutil.which("libreoffice"):
        return "libreoffice"
    if shutil.which("soffice"):
        return "soffice"
    # Jalur default jika diinstal di Windows
    windows_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for path in windows_paths:
        if os.path.exists(path):
            return path
    return None


# ================= ENGINE KONVERSI =================

# 1. Gambar (JPG, PNG, WebP) ke PDF
def convert_images_to_pdf(images_bytes_list):
    """Bisa mengonversi satu gambar atau menggabungkan banyak gambar jadi 1 PDF"""
    pil_images = []
    for raw in images_bytes_list:
        img = Image.open(io.BytesIO(raw))
        if img.mode != "RGB":
            img = img.convert("RGB")
        pil_images.append(img)
        
    if not pil_images:
        return None
        
    out_buf = io.BytesIO()
    first_img = pil_images[0]
    first_img.save(out_buf, format="PDF", save_all=True, append_images=pil_images[1:])
    return out_buf.getvalue()


# 2. Office (Word, Excel, PPT) ke PDF via LibreOffice
def convert_office_to_pdf(file_bytes, filename):
    lo_cmd = get_libreoffice_command()
    if not lo_cmd:
        st.error("⚠️ Mesin LibreOffice belum terpasang di sistem hosting/server. Diperlukan untuk merender Word/Excel/PPT.")
        return None

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, filename)
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        # Jalankan perintah konversi headless
        cmd = [lo_cmd, "--headless", "--convert-to", "pdf", input_path, "--outdir", temp_dir]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        base_name = os.path.splitext(filename)[0]
        output_pdf_path = os.path.join(temp_dir, f"{base_name}.pdf")

        if os.path.exists(output_pdf_path):
            with open(output_pdf_path, "rb") as f:
                return f.read()
        else:
            st.error(f"Gagal mengonversi file: {result.stderr.decode('utf-8', errors='ignore')}")
            return None


# 3. HTML / Web Blog ke PDF
def convert_html_or_url_to_pdf(html_content=None, url=None):
    out_buf = io.BytesIO()
    if url:
        HTML(url=url).write_pdf(out_buf)
    elif html_content:
        HTML(string=html_content).write_pdf(out_buf)
    return out_buf.getvalue()


# ================= STATE NAVIGASI =================
if "menu" not in st.session_state:
    st.session_state.menu = "🖼️ Gambar ke PDF"

with st.sidebar:
    st.markdown("### 📑 Pilihan Konversi")
    opsi = [
        "🖼️ Gambar ke PDF",
        "📝 Word ke PDF",
        "📊 Excel ke PDF",
        "📽️ PowerPoint ke PDF",
        "🌐 Blog / HTML ke PDF"
    ]
    for opt in opsi:
        tipe = "primary" if st.session_state.menu == opt else "secondary"
        if st.button(opt, key=f"nav_{opt}", use_container_width=True, type=tipe):
            st.session_state.menu = opt
            st.rerun()

# ================= HERO HEADER =================
st.markdown(f"""
<div class="brand-hero">
    <div class="brand-pill">⚡ UNIVERSAL CONVERTER</div>
    <div class="brand-title">Convert<span style="color:#EC4899">PRO</span></div>
    <p style="color: #64748B; font-weight: 600; font-size: 0.9rem;">{st.session_state.menu}</p>
</div>
""", unsafe_allow_html=True)


# ================= MENU 1: GAMBAR KE PDF =================
if st.session_state.menu == "🖼️ Gambar ke PDF":
    files = st.file_uploader("Upload Foto/Gambar (JPG, PNG, WebP)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    if files:
        mode = st.radio("Metode Penggabungan:", ["Satukan Semua Gambar Jadi 1 Dokumen PDF", "Konversi Masing-masing Jadi File PDF Terpisah"])
        
        if st.button("🚀 Mulai Konversi ke PDF", type="primary", use_container_width=True):
            if mode.startswith("Satukan"):
                pdf_bytes = convert_images_to_pdf([f.getvalue() for f in files])
                st.success("🎉 Berhasil disatukan menjadi 1 file PDF!")
                st.download_button(
                    "⬇️ Unduh PDF Gabungan",
                    data=pdf_bytes,
                    file_name="Semua_Gambar_Merged.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
                    for f in files:
                        pdf_data = convert_images_to_pdf([f.getvalue()])
                        z.writestr(f"{os.path.splitext(f.name)[0]}.pdf", pdf_data)
                
                st.download_button(
                    f"⬇️ Unduh Semua PDF ({len(files)} File) - ZIP",
                    data=zip_buf.getvalue(),
                    file_name="Images_Converted_PDF.zip",
                    mime="application/zip",
                    use_container_width=True
                )


# ================= MENU 2: WORD KE PDF =================
elif st.session_state.menu == "📝 Word ke PDF":
    files = st.file_uploader("Upload Dokumen Word (.docx, .doc)", type=["docx", "doc"], accept_multiple_files=True)
    if files and st.button("🚀 Konversi Word ke PDF", type="primary", use_container_width=True):
        with st.spinner("Memproses konversi dokumen Word..."):
            for f in files:
                pdf_data = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_data:
                    out_name = f"{os.path.splitext(f.name)[0]}.pdf"
                    st.download_button(f"⬇️ Unduh {out_name}", data=pdf_data, file_name=out_name, mime="application/pdf", key=f.name)


# ================= MENU 3: EXCEL KE PDF =================
elif st.session_state.menu == "📊 Excel ke PDF":
    files = st.file_uploader("Upload Dokumen Excel (.xlsx, .xls)", type=["xlsx", "xls"], accept_multiple_files=True)
    if files and st.button("🚀 Konversi Excel ke PDF", type="primary", use_container_width=True):
        with st.spinner("Merender lembar kerja Excel ke PDF..."):
            for f in files:
                pdf_data = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_data:
                    out_name = f"{os.path.splitext(f.name)[0]}.pdf"
                    st.download_button(f"⬇️ Unduh {out_name}", data=pdf_data, file_name=out_name, mime="application/pdf", key=f.name)


# ================= MENU 4: PPT KE PDF =================
elif st.session_state.menu == "📽️ PowerPoint ke PDF":
    files = st.file_uploader("Upload Presentasi PPT (.pptx, .ppt)", type=["pptx", "ppt"], accept_multiple_files=True)
    if files and st.button("🚀 Konversi Slide ke PDF", type="primary", use_container_width=True):
        with st.spinner("Mengonversi slide PowerPoint..."):
            for f in files:
                pdf_data = convert_office_to_pdf(f.getvalue(), f.name)
                if pdf_data:
                    out_name = f"{os.path.splitext(f.name)[0]}.pdf"
                    st.download_button(f"⬇️ Unduh {out_name}", data=pdf_data, file_name=out_name, mime="application/pdf", key=f.name)


# ================= MENU 5: BLOG / HTML KE PDF =================
elif st.session_state.menu == "🌐 Blog / HTML ke PDF":
    sub_tab = st.radio("Sumber Input:", ["URL Link Blog / Website", "Upload File HTML"], horizontal=True)
    
    if sub_tab == "URL Link Blog / Website":
        url_input = st.text_input("Masukkan Tautan/URL Artikel (contoh: https://id.wikipedia.org/wiki/Python)", "")
        if st.button("🚀 Cetak Halaman ke PDF", type="primary", use_container_width=True):
            if url_input.strip():
                with st.spinner("Mengunduh halaman dan menyusun PDF..."):
                    try:
                        pdf_data = convert_html_or_url_to_pdf(url=url_input.strip())
                        st.download_button("⬇️ Unduh Halaman Web (PDF)", data=pdf_data, file_name="Web_Article.pdf", mime="application/pdf", use_container_width=True)
                    except Exception as e:
                        st.error(f"Gagal mengambil URL: {e}")
            else:
                st.warning("Silakan masukkan URL yang valid.")
                
    else:
        html_file = st.file_uploader("Upload file .html", type=["html", "htm"])
        if html_file and st.button("🚀 Konversi HTML ke PDF", type="primary", use_container_width=True):
            with st.spinner("Membuat PDF dari kode HTML..."):
                try:
                    pdf_data = convert_html_or_url_to_pdf(html_content=html_file.getvalue().decode("utf-8", errors="ignore"))
                    st.download_button(f"⬇️ Unduh {os.path.splitext(html_file.name)[0]}.pdf", data=pdf_data, file_name=f"{os.path.splitext(html_file.name)[0]}.pdf", mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"Gagal mengonversi HTML: {e}")