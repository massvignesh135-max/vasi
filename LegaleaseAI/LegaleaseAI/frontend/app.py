from __future__ import annotations

import io
import os
from datetime import date

import requests
import streamlit as st

# Optional packages for DOCX/PDF export
try:
    from docx import Document
    from docx.shared import Inches, Pt

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ============================================================
# SESSION STATE
# ============================================================

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = ""

if "parties" not in st.session_state:
    st.session_state.parties = ""

if "terms" not in st.session_state:
    st.session_state.terms = ""

if "effective_date" not in st.session_state:
    st.session_state.effective_date = ""


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        max-width: 900px;
        margin: auto;
    }

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777777;
        font-size: 16px;
        margin-bottom: 30px;
    }

    .description {
        text-align: center;
        color: #444444;
        margin-bottom: 25px;
    }

    .footer {
        margin-top: 35px;
        padding-top: 20px;
        border-top: 1px solid #dddddd;
        color: #888888;
        font-size: 13px;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI Legal Document Generator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="description">
    Create an editable legal-document draft from your document requirements.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DOCUMENT INFORMATION
# ============================================================

st.subheader("Document Information")


with st.form("legal_document_form"):

    document_type = st.text_input(
        "Document Type",
        value=st.session_state.document_type,
        placeholder="Example: Freelance Work Contract",
    )

    parties = st.text_area(
        "Parties Involved",
        value=st.session_state.parties,
        placeholder=(
            "Example: Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=100,
    )

    terms = st.text_area(
        "Terms & Conditions",
        value=st.session_state.terms,
        placeholder=(
            "Payment within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=150,
        help="Separate individual terms using semicolons.",
    )

    effective_date = st.text_input(
        "Effective Date",
        value=st.session_state.effective_date,
        placeholder="Example: April 15, 2025",
    )

    logo = st.file_uploader(
        "Optional Logo",
        type=["png", "jpg", "jpeg"],
        help="Optional logo for the document.",
    )

    submitted = st.form_submit_button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# GENERATE DOCUMENT
# ============================================================

if submitted:

    # --------------------------------------------
    # Validate inputs
    # --------------------------------------------

    if not document_type.strip():
        st.error("Please enter a document type.")

    elif not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    elif not effective_date.strip():
        st.error("Please enter the effective date.")

    else:

        # --------------------------------------------
        # Save values in session state
        # --------------------------------------------

        st.session_state.document_type = document_type.strip()
        st.session_state.parties = parties.strip()
        st.session_state.terms = terms.strip()
        st.session_state.effective_date = effective_date.strip()

        # --------------------------------------------
        # Backend payload
        #
        # IMPORTANT:
        # Backend expects "effective_date"
        # NOT "dates"
        # --------------------------------------------

        payload = {
            "document_type": document_type.strip(),
            "parties": parties.strip(),
            "terms": terms.strip(),
            "effective_date": effective_date.strip(),
        }

        # --------------------------------------------
        # Send request to backend
        # --------------------------------------------

        try:

            with st.spinner("Generating your legal document..."):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

            # ----------------------------------------
            # Backend success
            # ----------------------------------------

            if response.ok:

                try:
                    result = response.json()
                except ValueError:
                    result = {}

                generated_document = result.get(
                    "document",
                    "",
                )

                if not generated_document:

                    # Some backends may return text directly
                    generated_document = result.get(
                        "generated_document",
                        "",
                    )

                if not generated_document:

                    st.error(
                        "Backend returned an empty document."
                    )

                else:

                    st.session_state.generated_text = (
                        generated_document
                    )

                    st.success(
                        "Document generated successfully!"
                    )

            # ----------------------------------------
            # Backend error
            # ----------------------------------------

            else:

                try:
                    error_data = response.json()
                    error_message = str(error_data)
                except ValueError:
                    error_message = response.text

                st.error(
                    f"Backend error: {error_message}"
                )

        # --------------------------------------------
        # Connection error
        # --------------------------------------------

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the backend. "
                "Please make sure FastAPI is running on "
                f"{BACKEND_URL}"
            )

        except requests.exceptions.Timeout:

            st.error(
                "Backend request timed out. "
                "Please try again."
            )

        except requests.exceptions.RequestException as exc:

            st.error(
                f"Request failed: {exc}"
            )


# ============================================================
# GENERATED DOCUMENT
# ============================================================

if st.session_state.generated_text:

    st.divider()

    st.subheader("Document Generated")

    # --------------------------------------------
    # Preview
    # --------------------------------------------

    preview_text = st.session_state.generated_text

    st.markdown(
        f"""
        <div style="
            background:#17191f;
            color:white;
            padding:25px;
            border-radius:10px;
            white-space:pre-wrap;
            line-height:1.6;
        ">
        {preview_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # EDIT DOCUMENT
    # ========================================================

    st.divider()

    st.subheader("Edit Document")

    st.caption(
        "Edit the generated document below:"
    )

    edited_document = st.text_area(
        "Document Content",
        value=st.session_state.generated_text,
        height=500,
        label_visibility="collapsed",
    )

    # Save edited content
    st.session_state.generated_text = edited_document


    # ========================================================
    # DOWNLOAD DOCUMENT
    # ========================================================

    st.divider()

    st.subheader("Download Document")


    # ========================================================
    # TXT
    # ========================================================

    txt_data = st.session_state.generated_text.encode(
        "utf-8"
    )

    st.download_button(
        label="Download TXT",
        data=txt_data,
        file_name="legal_document.txt",
        mime="text/plain",
        use_container_width=True,
    )


    # ========================================================
    # DOCX
    # ========================================================

    if DOCX_AVAILABLE:

        try:

            doc = Document()

            # Logo
            if logo is not None:

                try:

                    logo_bytes = logo.getvalue()

                    logo_stream = io.BytesIO(
                        logo_bytes
                    )

                    doc.add_picture(
                        logo_stream,
                        width=Inches(1.5),
                    )

                except Exception:
                    pass

            # Title
            title = doc.add_paragraph()

            run = title.add_run(
                "LEGAL DOCUMENT"
            )

            run.bold = True
            run.font.size = Pt(16)

            # Document information
            doc.add_paragraph(
                f"Document Type: "
                f"{st.session_state.document_type}"
            )

            doc.add_paragraph(
                f"Parties: "
                f"{st.session_state.parties}"
            )

            doc.add_paragraph(
                f"Effective Date: "
                f"{st.session_state.effective_date}"
            )

            doc.add_paragraph("")

            # Generated document
            for line in st.session_state.generated_text.splitlines():

                paragraph = doc.add_paragraph()

                paragraph.add_run(line)

            docx_buffer = io.BytesIO()

            doc.save(docx_buffer)

            docx_buffer.seek(0)

            st.download_button(
                label="Download DOCX",
                data=docx_buffer.getvalue(),
                file_name="legal_document.docx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
                use_container_width=True,
            )

        except Exception as exc:

            st.warning(
                f"DOCX export unavailable: {exc}"
            )

    else:

        st.info(
            "DOCX download requires python-docx."
        )


    # ========================================================
    # PDF
    # ========================================================

    if PDF_AVAILABLE:

        try:

            pdf_buffer = io.BytesIO()

            pdf = canvas.Canvas(
                pdf_buffer,
                pagesize=A4,
            )

            page_width, page_height = A4

            left_margin = 50
            top_position = page_height - 50

            # Title
            pdf.setFont(
                "Helvetica-Bold",
                16,
            )

            pdf.drawString(
                left_margin,
                top_position,
                "LEGAL DOCUMENT",
            )

            y = top_position - 35

            # Information
            pdf.setFont(
                "Helvetica",
                10,
            )

            info_lines = [
                (
                    "Document Type: "
                    + st.session_state.document_type
                ),
                (
                    "Parties: "
                    + st.session_state.parties
                ),
                (
                    "Effective Date: "
                    + st.session_state.effective_date
                ),
            ]

            for line in info_lines:

                # Simple wrapping
                words = line.split()
                current_line = ""

                for word in words:

                    test_line = (
                        current_line + " " + word
                    ).strip()

                    if pdf.stringWidth(
                        test_line,
                        "Helvetica",
                        10,
                    ) < 500:

                        current_line = test_line

                    else:

                        pdf.drawString(
                            left_margin,
                            y,
                            current_line,
                        )

                        y -= 15

                        current_line = word

                if current_line:

                    pdf.drawString(
                        left_margin,
                        y,
                        current_line,
                    )

                    y -= 18

            y -= 10

            pdf.setFont(
                "Helvetica",
                10,
            )

            # Document text
            for line in st.session_state.generated_text.splitlines():

                if y < 50:

                    pdf.showPage()

                    pdf.setFont(
                        "Helvetica",
                        10,
                    )

                    y = page_height - 50

                # Basic text wrapping
                words = line.split()

                current_line = ""

                for word in words:

                    test_line = (
                        current_line + " " + word
                    ).strip()

                    if pdf.stringWidth(
                        test_line,
                        "Helvetica",
                        10,
                    ) < 500:

                        current_line = test_line

                    else:

                        if y < 50:

                            pdf.showPage()

                            pdf.setFont(
                                "Helvetica",
                                10,
                            )

                            y = page_height - 50

                        pdf.drawString(
                            left_margin,
                            y,
                            current_line,
                        )

                        y -= 14

                        current_line = word

                if current_line:

                    if y < 50:

                        pdf.showPage()

                        pdf.setFont(
                            "Helvetica",
                            10,
                        )

                        y = page_height - 50

                    pdf.drawString(
                        left_margin,
                        y,
                        current_line,
                    )

                    y -= 14

            pdf.save()

            pdf_buffer.seek(0)

            st.download_button(
                label="Download PDF",
                data=pdf_buffer.getvalue(),
                file_name="legal_document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as exc:

            st.warning(
                f"PDF export unavailable: {exc}"
            )

    else:

        st.info(
            "PDF download requires reportlab."
        )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    """
    <div class="footer">
    LegalEase is an AI-assisted drafting tool.
    Generated documents should be reviewed for accuracy,
    jurisdiction, facts, and legal sufficiency before
    real-world use.
    </div>
    """,
    unsafe_allow_html=True,
)