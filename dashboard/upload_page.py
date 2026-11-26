
# Streamlit library import karna.
import streamlit as st


# Supported multimodal file formats define karna.
SUPPORTED_FORMATS = [
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "wav",
    "mp3",
    "mp4",
    "avi"
]


# Upload page display karne ke liye function.
def render_upload_page():

    # Page ka main heading display karna.
    st.title("Multimodal Asset Intake Console")

    # Page ka short description display karna.
    st.write("Upload your learning documents and media files.")

    # User ko multiple files upload karne ka option dena.
    uploaded_files = st.file_uploader(
        "Choose your files",
        type=SUPPORTED_FORMATS,
        accept_multiple_files=True
    )

    # Check karna ki user ne files upload ki hain ya nahi.
    if uploaded_files:

        # Upload section ka heading display karna.
        st.subheader("Uploaded Asset Details")

        # Har uploaded file ki details check karna.
        for uploaded_file in uploaded_files:

            # File ka size bytes se KB mein convert karna.
            file_size = uploaded_file.size / 1024

            # Har file ki details ek expandable section mein dikhana.
            with st.expander(uploaded_file.name):

                # File ka original name display karna.
                st.write("File Name:", uploaded_file.name)

                # File ka format display karna.
                st.write("File Type:", uploaded_file.type)

                # File ka size display karna.
                st.write("File Size:", f"{file_size:.2f} KB")

                # File upload interface tak receive hone ka status.
                st.success("File received successfully.")

        # Total uploaded files count display karna.
        st.info(f"Total uploaded files: {len(uploaded_files)}")

        # Abhi permanent storage aur ingestion integration pending hai.
        st.warning(
            "Files are currently available in the upload interface. "
            "Permanent storage will be connected during final integration."
        )

    # Agar koi file upload nahi hui.
    else:

        # User ko upload karne ke liye instruction dena.
        st.info("Please upload at least one file.")

    # Uploaded files ko future integration ke liye return karna.
    return uploaded_files
