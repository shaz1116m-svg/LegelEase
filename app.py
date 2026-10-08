
import os

import requests

import streamlit as st

from dotenv import load_dotenv

from services.document_service import (
    format_docx,
    format_pdf,
    format_html_preview,
    sanitize_text
)


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide"

)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(

    """
    <style>

    .block-container {

        max-width: 1200px;

        padding-top: 2rem;

    }

    .hero {

        text-align: center;

        padding: 1rem 0 1.5rem;

    }

    .hero h1 {

        font-size: 3rem;

        margin-bottom: 0.2rem;

    }

    .hero p {

        font-size: 1.05rem;

        opacity: 0.8;

    }

    .preview {

        background: #15171b;

        color: #f1f1f1;

        border: 1px solid #333842;

        border-radius: 14px;

        padding: 24px;

        min-height: 360px;

        max-height: 650px;

        overflow-y: auto;

        line-height: 1.65;

    }

    .legal-section {

        margin: 1rem 0;

    }

    </style>

    """,

    unsafe_allow_html=True

)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(

    """
    <div class="hero">

        <h1>⚖️ LegalEase</h1>

        <p>
        AI-Powered Legal Document Generator
        </p>

    </div>
    """,

    unsafe_allow_html=True

)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "generated" not in st.session_state:

    st.session_state.generated = ""


if "document_type" not in st.session_state:

    st.session_state.document_type = ""


# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------

left, right = st.columns(
    [0.9, 1.1],
    gap="large"
)


# ==================================================
# LEFT SIDE - INPUT FORM
# ==================================================

with left:

    st.subheader("Document Details")

    document_type = st.text_input(

        "Document Type",

        value=st.session_state.document_type,

        placeholder="Freelance Work Contract"

    )

    parties = st.text_area(

        "Parties Involved",

        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),

        height=110

    )

    terms = st.text_area(

        "Terms & Conditions",

        placeholder=(
            "Payment within 30 days; "
            "Confidentiality; "
            "15-day termination notice"
        ),

        help="Separate each term using semicolons.",

        height=150

    )

    effective_date = st.text_input(

        "Effective Date",

        placeholder="October 5, 2026"

    )

    language = st.selectbox(

        "Output Language",

        ["English", "Hindi", "Tamil"]

    )

    logo = st.file_uploader(

        "Upload Company Logo (Optional)",

        type=["png", "jpg", "jpeg"]

    )

    generate_button = st.button(

        "✨ Generate Document",

        type="primary",

        use_container_width=True

    )


    # --------------------------------------------------
    # GENERATE DOCUMENT
    # --------------------------------------------------

    if generate_button:

        missing = []

        if not document_type.strip():

            missing.append("Document Type")

        if not parties.strip():

            missing.append("Parties")

        if not terms.strip():

            missing.append("Terms")

        if not effective_date.strip():

            missing.append("Effective Date")


        if missing:

            st.error(
                "Please fill in: " + ", ".join(missing)
            )

        else:

            payload = {

                "document_type": document_type,

                "parties": parties,

                "terms": terms,

                "effective_date": effective_date,

                "language": language

            }

            try:

                with st.spinner(
                    "Generating your legal document..."
                ):

                    response = requests.post(

                        f"{BACKEND_URL}/generate",

                        json=payload,

                        timeout=130

                    )


                if response.status_code == 200:

                    result = response.json()

                    st.session_state.generated = (
                        result["content"]
                    )

                    st.session_state.document_type = (
                        document_type
                    )

                    if result.get("demo_mode"):

                        st.success(
                            "Document generated in demo mode."
                        )

                    else:

                        st.success(
                            "AI document generated successfully!"
                        )


                else:

                    try:

                        error_message = response.json().get(
                            "detail",
                            response.text
                        )

                    except ValueError:

                        error_message = response.text

                    st.error(
                        f"Backend error: {error_message}"
                    )


            except requests.RequestException as error:

                st.error(
                    "Cannot connect to FastAPI. "
                    "Please start the backend server first."
                )

                st.caption(str(error))


# ==================================================
# RIGHT SIDE - PREVIEW AND DOWNLOAD
# ==================================================

with right:

    st.subheader("Document Preview")


    if st.session_state.generated:

        preview_html = format_html_preview(
            st.session_state.generated
        )

        st.markdown(

            f"""
            <div class="preview">

                {preview_html}

            </div>
            """,

            unsafe_allow_html=True

        )


        # --------------------------------------------------
        # EDIT DOCUMENT
        # --------------------------------------------------

        st.divider()

        st.subheader("Edit Your Document")


        edited_text = st.text_area(

            "Editable Document Content",

            value=st.session_state.generated,

            height=400,

            label_visibility="collapsed"

        )


        st.session_state.generated = edited_text


        # --------------------------------------------------
        # EXPORT DOCUMENT
        # --------------------------------------------------

        logo_bytes = (
            logo.getvalue()
            if logo is not None
            else None
        )


        safe_type = "".join(

            character
            if character.isalnum() or character in " -_"
            else "_"

            for character in document_type.strip()

        ).strip() or "legal_document"


        txt_data = sanitize_text(
            st.session_state.generated
        ).encode("utf-8")


        docx_data = format_docx(

            st.session_state.generated,

            document_type,

            logo_bytes=logo_bytes,

            terms=terms

        )


        pdf_data = format_pdf(

            st.session_state.generated,

            document_type,

            logo_bytes=logo_bytes

        )


        # --------------------------------------------------
        # DOWNLOAD BUTTONS
        # --------------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.download_button(

                "⬇️ TXT",

                data=txt_data,

                file_name=f"{safe_type}.txt",

                mime="text/plain",

                use_container_width=True

            )


        with col2:

            st.download_button(

                "⬇️ DOCX",

                data=docx_data,

                file_name=f"{safe_type}.docx",

                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),

                use_container_width=True

            )


        with col3:

            st.download_button(

                "⬇️ PDF",

                data=pdf_data,

                file_name=f"{safe_type}.pdf",

                mime="application/pdf",

                use_container_width=True

            )


    else:

        st.info(
            "Your generated legal document will appear here."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(

    """
    LegalEase | AI-Powered Legal Document Generator

    AI-generated documents are drafts for informational purposes.
    Consult a qualified legal professional before signing or relying
    on any generated document.
    """

)