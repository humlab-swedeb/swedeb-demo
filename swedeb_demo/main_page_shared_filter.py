"""_summary_: This is the main page of the SweDeb app with a global meta data filter and a tabbed interface for the different tools.
"""
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.kwic_tab import KWICDisplay  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore
from components.whole_speeches_tab import FullSpeechDisplay  # type: ignore
from components.word_trends_tab import WordTrendsDisplay  # type: ignore
from typing import Any
import click

st.set_page_config(
    page_title="SweDeb DEMO b",
    layout="wide",
)


def add_banner() -> None:
    """_summary_: Adds a banner to the top of the page containing the title and a dropdown menu for selecting a corpus"""
    banner = st.container()
    with banner:
        other_col, corpus_col = st.columns([2, 1])
        with corpus_col:
            st.selectbox(
                "Välj korpus",
                (["Sample data"]),
                key="corpus_box",
                help="Välj vilket korpus du vill arbeta med",
                index=0,
            )
        with other_col:
            st.title("Svenska riksdagsdebatter")


def set_swedish_for_selections() -> None:
    SELECT_TEXT = "Välj ett eller flera alternativ"
    multi_css = f"""
    <style>
    .stMultiSelect div div div div div:nth-of-type(2) {{visibility: hidden;}}
    .stMultiSelect div div div div div:nth-of-type(2)::before {{visibility: visible; content:"{SELECT_TEXT}";}}
    </style>
    """
    st.markdown(multi_css, unsafe_allow_html=True)


def add_meta_sidebar(api: ADummyApi) -> Any:
    sidebar_container = st.sidebar.container()
    with sidebar_container:
        st.header("Filtrera sökresultat")
        side_expander = st.expander("Visa filtreringsalternativ:")
        with side_expander:
            meta_search = MetaDataDisplay(st_dict={}, api=api)
    return meta_search


def add_tabs(meta_search: Any, api: ADummyApi, debug: bool) -> None:
    debug_tab = " "
    if debug:
        debug_tab = "Debug"

    (
        tab_WT,
        tab_KWIC,
        tab_whole_speeches,
        tab_NG,
        tab_topics,
        tab_about,
        tab_debug,
    ) = st.tabs(
        [
            "Ordtrender",
            "KWIC",
            "Anföranden",
            "N-gram",
            "Temamodeller",
            "Om SweDeb",
            debug_tab,
        ]
    )

    with tab_WT:
        WordTrendsDisplay(api, shared_meta=meta_search, tab_key="WT")

    with tab_KWIC:
        KWICDisplay(api, shared_meta=meta_search, tab_key="KWIC")

    with tab_NG:
        st.caption("Här kommer information om verktyget **N-gram**")

    with tab_whole_speeches:
        FullSpeechDisplay(api, shared_meta=meta_search, tab_key="SPEECH")

    with tab_topics:
        st.caption("Här kommer information om verktyget **Temamodeller**")

    with tab_about:
        st.write("Här kommer information om SweDebprojektet och verktygen")
        faq_expander = st.expander("FAQ")
        with faq_expander:
            st.write("Vad är detta?")
            st.caption(
                "En prototyp utvecklad för att undersöka möjligheterna med att tillgängliggöra riksdagsdebatter"
            )
            st.write("Hur använder man den här prototypen?")
            st.caption(
                "I vänsterspalten kan du välja vilken data du vill undersöka. I de olika flikarna kan du välja vilket verktyg du vill använda för att undersöka materialet."
            )
    if debug:
        with tab_debug:
            st.caption("Session state:")
            st.write(st.session_state)


@click.command()
@click.option('--env_file', default='.env_sample_docker', help='Path to .env file with environment variables')
@click.option('--debug', default=True, help='Show session state info in debug tab')
def render_main_page(env_file:str, debug:bool)->None:
    dummy_api = ADummyApi(env_file)
    add_banner()
    set_swedish_for_selections()
    meta_search = add_meta_sidebar(dummy_api)
    add_tabs(meta_search, dummy_api, debug)


if __name__ == "__main__":
    render_main_page()  # type: ignore
