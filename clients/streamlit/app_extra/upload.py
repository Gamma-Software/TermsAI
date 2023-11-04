import streamlit as st


def upload():
    choice = st.radio(
        "How do you want to retrieve the Terms of the contract ?",
        ("Upload a file", "Enter the raw text"),
    )

    data = None
    if choice == "Upload a file":
        uploaded_file = st.file_uploader(
            "Upload contract PDFs",
            # ["pdf", "png", "jpg", "jpeg", "txt", "md"],
            ["pdf"],
            accept_multiple_files=True,
            help="could be a picture or a pdf",
        )
        # write the stream in a file
        if uploaded_file is not None:

            def treat_file(file):
                # Write it into a temp file
                temp_file = f"/tmp/{file.name}"
                with open(temp_file, "wb") as f:
                    f.write(file.getvalue())
                # get extension
                extension = file.name.split(".")[-1]
                if extension in ["png", "jpg", "jpeg"]:
                    return {"pic": temp_file}
                elif extension == "pdf":
                    return {"pdf": temp_file}
                elif extension == ["txt", "md"]:
                    with open(temp_file, "r", encoding="utf-8") as f:
                        text = f.read()
                    return {"text": text}

            data = [treat_file(f) for f in uploaded_file]

    else:
        text = st.text_area(
            "Enter the raw text",
            st.session_state["extracted_data"]
            if "extracted_data" in st.session_state
            else "",
        )
        if text:
            data = [{"text": text}]
    return data
