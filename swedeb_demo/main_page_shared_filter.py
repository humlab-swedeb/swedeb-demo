"""_summary_: This is the main page of the SweDeb app with a global meta data filter and
 a tabbed interface for the different tools.
"""
from typing import Any

import click
import streamlit as st

from swedeb_demo.api.dummy_api import ADummyApi  # type: ignore
from swedeb_demo.components import component_texts as ct
from swedeb_demo.components.kwic_tab import KWICDisplay  # type: ignore
from swedeb_demo.components.meta_data_display import \
    MetaDataDisplay  # type: ignore
from swedeb_demo.components.whole_speeches_tab import \
    FullSpeechDisplay  # type: ignore
from swedeb_demo.components.word_trends_tab import \
    WordTrendsDisplay  # type: ignore

st.set_page_config(
    page_title="SweDeb DEMO b",
    layout="wide",
)


def add_banner() -> None:
    """_summary_: Adds a banner to the top of the page containing the title and a 
    dropdown menu for selecting a corpus"""
    banner = st.container()
    with banner:
        header_col, corpus_col = st.columns([3, 2])
        with corpus_col:
            st.selectbox(
                ct.m_corpus_selectbox,
                (ct.m_corpus_selectbox_options),
                key="corpus_box",
                help=ct.m_corpus_selectbox_help,
                index=0,
            )
        with header_col:
            st.title(ct.m_title)


def set_swedish_for_selections() -> None:
    SELECT_TEXT = "Välj ett eller flera alternativ"
    multi_css = f"""
    <style>
    .stMultiSelect div div div div div:nth-of-type(2) {{visibility: hidden;}}
    .stMultiSelect div div div div div:nth-of-type(2)::before {{visibility: visible; content:"{SELECT_TEXT}";}}
    </style>
    """  # noqa: E501
    st.markdown(multi_css, unsafe_allow_html=True)


def add_meta_sidebar(api: ADummyApi) -> Any:
    sidebar_container = st.sidebar.container()

    with sidebar_container:
        st.header(ct.m_meta_header, help=ct.m_meta_help)
        side_expander = st.expander(ct.m_meta_expander)
        st.caption(ct.m_meta_caption)

        with side_expander:
            meta_search = MetaDataDisplay(st_dict={}, api=api)
        st.selectbox(
            ct.m_hits_per_page, ct.m_hits_options, key="hits_per_page_all", index=0
        )

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
        WordTrendsDisplay(api, shared_meta=meta_search, tab_key=ct.m_wt_tab)

    with tab_KWIC:
        KWICDisplay(api, shared_meta=meta_search, tab_key=ct.m_kwic_tab)

    with tab_NG:
        st.caption(ct.m_ngram_caption)

    with tab_whole_speeches:
        FullSpeechDisplay(api, shared_meta=meta_search, tab_key=ct.m_sp_tab)

    with tab_topics:
        st.caption(ct.m_topics_caption)

    with tab_about:
        st.write(ct.m_about_caption)
        faq_expander = st.expander(ct.m_faq)
        with faq_expander:
            st.write(ct.m_faq_Q1)
            st.caption(ct.m_faq_A1)
            st.write(ct.m_faq_Q2)
            st.caption(ct.m_faq_A2)
    if debug:
        with tab_debug:
            st.caption("Session state:")
            st.write(st.session_state)


@click.command()
@click.option(
    "--env_file",
    default=".env_sample_docker",
    help="Path to .env file with environment variables",
)
@click.option("--debug", default=True, help="Show session state info in debug tab")
@click.option(
    "--corpus_dir", default="/usr/local/share/cwb/registry/", 
    help="Path to corpora directory (registry)")
@click.option(
    "--corpus_name", default="RIKSPROT_V090_TEST", help=
    "Corpus name (eg. RIKSPROT_V090_TEST)"
)

def render_main_page(env_file: str, debug: bool, corpus_dir, corpus_name) -> None:
    dummy_api = ADummyApi(env_file, corpus_dir, corpus_name)
    add_banner()
    set_swedish_for_selections()
    meta_search = add_meta_sidebar(dummy_api)
    add_tabs(meta_search, dummy_api, debug)


if __name__ == "__main__":
    render_main_page()  # type: ignore
