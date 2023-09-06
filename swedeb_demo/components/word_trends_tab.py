from typing import Any, Tuple

import pandas as pd
import plotly.graph_objects as go  # type: ignore
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore

from .table_results import TableDisplay
from .tool_tab import ToolTab

from .speech_display_mixin import ExpandedSpeechDisplay


class WordTrendsDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(self, another_api: ADummyApi, shared_meta: MetaDataDisplay) -> None:
        super().__init__(another_api, shared_meta, "wt_form")
        self.SEARCH_PERFORMED = "search_performed_wt"
        self.CURRENT_PAGE_TAB = "current_page_tab"
        self.CURRENT_PAGE_SOURCE = "current_page_source"
        self.EXPANDED_SPEECH = "expanded_speech_wt"

        if (
            self.EXPANDED_SPEECH in st.session_state
            and st.session_state[self.EXPANDED_SPEECH]
        ):
            
            self.display_speech(
                self.get_reset_dict(), self.api, self.FORM_KEY, self.get_current_search_as_str()
            )
        else:
            st.caption(
                "Sök på ett begrepp för att hur det använts över tid. Välj vilka talare ska ingå till vänster."
            )

            self.top_container = st.container()
            self.search_container = st.container()
            self.top_result_container = st.container()
            self.result_container = st.container()

            self.hits_per_page = 5

            self.st_dict_when_button_clicked = {
                self.SEARCH_PERFORMED: True,
                self.CURRENT_PAGE_TAB: 0,
                self.CURRENT_PAGE_SOURCE: 0,
            }
            session_state_initial_values = {
                self.SEARCH_PERFORMED: False,
                self.CURRENT_PAGE_TAB: 0,
                self.CURRENT_PAGE_SOURCE: 0,
            }

            self.init_session_state(session_state_initial_values)
            self.define_displays()

            with self.search_container:
                st.text_input("Skriv sökterm:", key=f"search_box_{self.FORM_KEY}")
                st.radio(
                    "Normalisera resultatet?",
                    ("Frekvens", "Normaliserad frekvens"),
                    key=f"normal_{self.FORM_KEY}",
                )
                st.button(
                    "Sök",
                    key=f"search_button_{self.FORM_KEY}",
                    on_click=self.handle_button_click,
                )
                self.draw_line()

            if st.session_state[self.SEARCH_PERFORMED]:
                self.show_display()

    def get_reset_dict(self) -> dict:
        return {
                self.SEARCH_PERFORMED: True,
                self.CURRENT_PAGE_SOURCE: st.session_state[self.CURRENT_PAGE_SOURCE],
                f"search_box_{self.FORM_KEY}": self.get_current_search_as_str(),
                "wt_display_select": 'Anföranden',
                self.EXPANDED_SPEECH: False,
            }

    def get_current_search_as_str(self) -> str:
        if f"search_box_{self.FORM_KEY}" in st.session_state:
            return st.session_state[f"search_box_{self.FORM_KEY}"]
        return ""
    

    def handle_button_click(self) -> None:
        if not self.handle_search_click(self.st_dict_when_button_clicked):
            st.session_state[self.SEARCH_PERFORMED] = False

    def define_displays(self) -> None:
        self.table_display_table = TableDisplay(
            self.hits_per_page,
            current_container_key="WT_TABLE",
            current_page_name=self.CURRENT_PAGE_TAB,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key="",
        )
        self.table_display_source = TableDisplay(
            self.hits_per_page,
            current_container_key="WT_SOURCE",
            current_page_name=self.CURRENT_PAGE_SOURCE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key=self.EXPANDED_SPEECH,
        )

    @st.cache_data
    def get_data(
        _self,
        search_word: str,
        start_year: int,
        end_year: int,
        selections: dict,
        normalize: bool = False,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:

        return _self.api.get_word_trend_results(
            search_word,
            filter_opts=selections,
            start_year=start_year,
            end_year=end_year,
            normalize=normalize,
        )
    



    def show_display(self) -> None:
        slider = st.session_state["years_slider"]

        selections = self.search_display.get_selections()
        normalize = (
            st.session_state[f"normal_{self.FORM_KEY}"] == "Normaliserad frekvens"
        )

        data, kwic_like_data = self.get_data(
            self.get_search_box(),
            slider[0],
            slider[1],
            selections,
            normalize=normalize,
        )
        hits = self.api.get_word_hits(self.get_search_box())

        with self.top_result_container:
            if kwic_like_data.empty:
                self.display_settings_info_no_hits()
            else:
                self.display_settings_info(hits=f": {', '.join(hits)}")

                st.radio(
                    "Visa resultat som:",
                    ["Diagram", "Tabell", "Anföranden"],
                    index=0,
                    key="wt_display_select",
                    help=None,
                    horizontal=True,
                )
                self.display_results(data, kwic_like_data)

    def display_results(self, data: pd.DataFrame, kwic_like_data: pd.DataFrame) -> None:
        with self.result_container:
            if st.session_state["wt_display_select"] == "Diagram":
                self.draw_line_figure(data)
                self.add_download_button(data, file_name="word_trends.csv")
            elif st.session_state["wt_display_select"] == "Tabell":
                self.table_display_table.show_table(data)
                self.add_download_button(data, file_name="word_trends.csv")
            else:
                self.table_display_source.show_table(data=kwic_like_data, type="source")
                # self.add_download_button(data, file_name="word_trends_with_text.csv")

    def draw_line_figure(self, data: pd.DataFrame) -> None:
        markers = ["circle", "hourglass", "x", "cross", "square", 5]
        lines = ["solid", "dash", "dot", "dashdot", "solid"]
        fig = go.Figure()
        for i, col in enumerate(data.columns):
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[col],
                    mode="lines+markers",
                    name=col,
                    marker=dict(symbol=markers[i % len(markers)], size=8),
                    line=dict(dash=lines[i % len(lines)]),
                    showlegend=True,
                )
            )
        fig.update_layout(xaxis_title="År", yaxis_title="Frekvens")
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
