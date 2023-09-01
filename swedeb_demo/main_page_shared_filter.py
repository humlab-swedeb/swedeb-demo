"""_summary_: This is the main page of the SweDeb app with a global meta data filter and a tabbed interface for the different tools.
"""
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.kwic_tab import KWICDisplay  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore
from components.whole_speeches_tab import FullSpeechDisplay  # type: ignore
from components.word_trends_tab import WordTrendsDisplay  # type: ignore

st.set_page_config(
    page_title="SweDeb DEMO",
)


def add_banner() -> None:
    """_summary_: Adds a banner to the top of the page containing the title and a dropdown menu for selecting a corpus"""
    other_col, corpus_col = st.columns([2, 1])
    with corpus_col:
        st.selectbox(
            "Välj korpus",
            ("Sample data", "Version x.y.z"),
            key="corpus_box",
            help="Välj vilket korpus du vill arbeta med",
            index=0,
        )
    with other_col:
        st.title("Svenska riksdagsdebatter")


banner = st.container()
with banner:
    add_banner()


SELECT_TEXT = "Välj ett eller flera alternativ"
multi_css = f"""
<style>
.stMultiSelect div div div div div:nth-of-type(2) {{visibility: hidden;}}
.stMultiSelect div div div div div:nth-of-type(2)::before {{visibility: visible; content:"{SELECT_TEXT}";}}
</style>
"""
st.markdown(multi_css, unsafe_allow_html=True)


dummy_api = ADummyApi()


sidebar_container, main_col = st.columns([1, 4])

sidebar_container = st.sidebar.container()
with sidebar_container:
    st.title('Välj vilken data du vill arbeta med:')
    side_expander = st.expander("Visa filtreringsalternativ:", expanded=True)
    with side_expander:
        meta_search = MetaDataDisplay({}, dummy_api)


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
        "...debug",
    ]
)

with tab_WT:
    WTForm = WordTrendsDisplay(dummy_api, shared_meta=meta_search)

with tab_KWIC:
    KFC = KWICDisplay(dummy_api, shared_meta=meta_search)

with tab_NG:
    st.caption("Information om verktyget **N-gram**")

with tab_whole_speeches:
    FSD = FullSpeechDisplay(dummy_api, shared_meta=meta_search)

with tab_topics:
    st.caption("Information om verktyget **Temamodeller**")

with tab_about:
    st.write("om SweDeb")
    faq_expander = st.expander("FAQ")
    with faq_expander:
        st.write("En fråga")
        st.caption("Ett svar")
        st.write("En annan fråga")
        st.caption("Ett annat svar")

with tab_debug:
    st.caption("Session state:")
    st.write(st.session_state)

    col_search, button = st.columns([2, 1])
    with col_search:
        st.text_input("Ful grej")
    with button:
        search_submit = st.button("Knapp")

    st.markdown(
        '<p style="color:#FF0000";>Red paragraph text</p>', unsafe_allow_html=True
    )


