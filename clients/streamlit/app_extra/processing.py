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
            status.update(label="Extract the text from the document...", expanded=True)
            st.session_state["extracted_data"] = extract_clean_doc(_file)

            status.update(label=f"Embed the text in vector store...", expanded=True)
            st.session_state["vector_store"] = embed_doc(
                st.session_state["extracted_data"]
            )

            if (
                not st.session_state["extracted_data"]
                or not st.session_state["vector_store"]
            ):
                st.stop()
                st.write("Processing of files failed !")
                status.update(
                    label="Processing of files failed !", state="error", expanded=True
                )

            def summarize():
                status.update(label="Summarizing...", state="running", expanded=True)
                _, _summary = summarize_chain_doc_exec(
                    st.session_state["extracted_data"]
                )
                st.subheader("Summary")
                st.write(_summary)
                status.update(label="Summarized!", state="running", expanded=True)
                return _summary

            def answer_question() -> List[Tuple[str, str]]:
                result = []
                for q_id, _question in enumerate(questions):
                    if _question == "":
                        continue
                    status.update(
                        label=f"Answer question... {q_id}/{len(questions)}",
                        expanded=True,
                    )
                    _, _answers = simple_qa_chain(
                        _question, st.session_state["vector_store"]
                    )
                    # docs_2, answers_2 = simple_qa_chain_long(question, st.session_state["extracted_data"])
                    # elif terms_url != "":
                    #    answers = overall_chain_url_exec([question], terms_url)
                    # for k, v in answers.items():
                    #    question_container.markdown(v["emoji"] + v["words"])
                    #    st.markdown(">" + v["output"]["answer"] + " " + v["output"]["excerpts"])
                    st.write(_question)
                    st.caption(_answers["output_text"])
                    # question_container.write(docs_2)
                    # question_container.write(answers_2)
                    result.append((_question, _answers["output_text"]))
                    status.update(
                        label=f"Question answered... {q_id}/{len(questions)}",
                        expanded=True,
                    )
                return result

            metadata = {}
            if summarizing:
                metadata["/Subject"] = summarize()

            if questionning:
                d = []
                for id, q in enumerate(answer_question()):
                    d.append({f"question{id}": q[0], f"answer{id}": q[1]})
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
            status.update(label="Zipping done!", state="running", expanded=True)
        else:
            status.update(label="Zipping failed", state="error", expanded=True)
            return None

        status.update(label="Processing files done!", state="complete", expanded=True)
        return Path(zipped_files)
