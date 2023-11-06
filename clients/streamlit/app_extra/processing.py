import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import streamlit as st
import json
from chains import (
    simple_qa_chain,
    summarize_chain_doc_exec,
)
from process_doc.process import extract_clean_doc, embed_doc
from process_doc.utils import integrated_metadata_in_pdf
from app_extra.display_metadata import display_pdf_metadata


def processing(
    questions,
    questionning,
    summarizing,
    add_metadata,
    data: List[Dict[str, str]],
    output_folder: Path,
) -> Path:
    with st.status("Processing file(s)...", expanded=True) as status:

        def process_file(_file, _id, length) -> str:
            # We process the pdf or photo to extract the text
            # And create a vector store to each paragraph
            st.write(f"Extract the text from {_file}...")
            st.session_state["extracted_data"] = extract_clean_doc(_file)

            st.write(f"Embed the text of {_file} in vector store...")
            st.session_state["vector_store"] = embed_doc(
                st.session_state["extracted_data"]
            )

            if (
                not st.session_state["extracted_data"]
                or not st.session_state["vector_store"]
            ):
                st.stop()
                st.write("Processing of files failed !")

            def summarize():
                st.write(f"Summarizing...")
                _, _summary = summarize_chain_doc_exec(
                    st.session_state["extracted_data"]
                )
                st.write("Summarized!")
                return _summary

            def answer_question() -> List[Tuple[str, str]]:
                result = []
                for q_id, _question in enumerate(questions):
                    if _question == "":
                        continue
                    st.write(f"Answer question... {q_id}/{len(questions)}")
                    _, _answers = simple_qa_chain(
                        _question, st.session_state["vector_store"]
                    )
                    # docs_2, answers_2 = simple_qa_chain_long(question, st.session_state["extracted_data"])
                    # elif terms_url != "":
                    #    answers = overall_chain_url_exec([question], terms_url)
                    # for k, v in answers.items():
                    #    question_container.markdown(v["emoji"] + v["words"])
                    #    st.markdown(">" + v["output"]["answer"] + " " + v["output"]["excerpts"])
                    # question_container.write(docs_2)
                    # question_container.write(answers_2)
                    result.append((_question, _answers["output_text"]))
                    st.write(f"Question answered... {q_id}/{len(questions)}")
                return result

            metadata = {}
            if summarizing:
                metadata["/Subject"] = summarize()

            if questionning:
                d = []
                for _id, q in enumerate(answer_question()):
                    d.append({q[0]: q[1]})
                metadata["/Questions"] = json.dumps(d)

            file_to_return = ""
            if add_metadata:
                file_to_return = integrated_metadata_in_pdf(_file, metadata)
            return file_to_return

        file_to_return = []
        for _id, _file in enumerate(data):
            name = _file["pdf"].name
            st.write(f"Processing file {_id + 1}/{len(data)}: {name}")
            file_to_return.append(process_file(_file, _id + 1, len(data)))
            if _id + 1 != len(data):
                st.divider()
            st.toast(f"File {_id + 1}/{len(data)} processed !")

        # Zip the files
        zipped_files = shutil.make_archive(
            str(output_folder.parent / "zipped_file"),
            "zip",
            str(output_folder.absolute()),
        )
        if Path(zipped_files).exists():
            st.write("Zipping done!")
        else:
            st.write(label="Zipping failed")
            return None

        st.write("Processing files done!")
        return Path(zipped_files)


def display_result(output_dir: Path):
    with st.expander("See results"):
        for file in output_dir.iterdir():
            if file.suffix == ".pdf":
                st.subheader(file.name)
                display_pdf_metadata(file)
            st.divider()
