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
        self.ROWS_PER_PAGE_TABLE = "rows_per_page_wt_table"
        self.ROWS_PER_PAGE_SOURCE = "rows_per_page_wt_source"
        self.words_per_year = self.api.get_words_per_year()

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
            self.download_container = st.container()

            self.st_dict_when_button_clicked = {
                self.SEARCH_PERFORMED: True,
                self.CURRENT_PAGE_TAB: 0,
                self.CURRENT_PAGE_SOURCE: 0,
            }
            session_state_initial_values = {
                self.SEARCH_PERFORMED: False,
                self.CURRENT_PAGE_TAB: 0,
                self.CURRENT_PAGE_SOURCE: 0,
                self.ROWS_PER_PAGE_SOURCE: 5,
                self.ROWS_PER_PAGE_TABLE: 5,
            }

            self.init_session_state(session_state_initial_values)
            self.define_displays()

            with self.search_container:
                st.text_input("Skriv sökterm:", key=f"search_box_{self.FORM_KEY}")
                st.radio(
                    "Normalisera resultatet?",
                    ("Frekvens", "Normaliserad frekvens"),
                    key=f"normal_{self.FORM_KEY}",
                    help='Frekvens: antal förekomster av söktermen per år. Normaliserad frekvens: antal förekomster av söktermen delat med totalt antal ord i tal under samma år.'
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
            current_container_key="WT_TABLE",
            current_page_name=self.CURRENT_PAGE_TAB,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key="",
            rows_per_table_key =self.ROWS_PER_PAGE_TABLE
        )
        self.table_display_source = TableDisplay(
            current_container_key="WT_SOURCE",
            current_page_name=self.CURRENT_PAGE_SOURCE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key=self.EXPANDED_SPEECH,
            rows_per_table_key =self.ROWS_PER_PAGE_SOURCE
        )

    @st.cache_data
    def get_data(
        _self,
        search_word: str,
        start_year: int,
        end_year: int,
        selections: dict,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        return _self.api.get_word_trend_results(
            search_word,
            filter_opts=selections,
            start_year=start_year,
            end_year=end_year,
        )

    @st.cache_data
    def get_kwic_like_data(
        _self,
        _api: Any,
        hits: list,
        from_year: int,
        to_year: int,
        selections: dict,
    ) -> pd.DataFrame:
        data = _api.get_kwic_results_for_search_hits(
            hits,
            from_year=from_year,
            to_year=to_year,
            selections=selections,
            words_before=-1,
            words_after=-1,
        )
        if data.empty:
            return data
        return data[
            ["Tal", "Talare", "År", "Kön", "Parti", "Protokoll", "longer", "who"]
        ]
    
    def normalize_word_per_year(self, data: pd.DataFrame) -> pd.DataFrame:

        
        data = data.merge(self.words_per_year, left_index=True, right_index=True)
        data = data.iloc[:,:].div(data.n_raw_tokens, axis=0)
        data.drop(columns=['n_raw_tokens'], inplace=True)

        return data

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
        )
        hits = self.api.get_word_hits(self.get_search_box())

        with self.top_result_container:
            if kwic_like_data.empty:
                self.display_settings_info_no_hits()
            else:
                self.display_settings_info(hits=f": {', '.join(hits)}")

                col_display_select,_, col_page_select = st.columns([2,1, 1])
                with col_display_select:

                    st.radio(
                        "Visa resultat som:",
                        ["Diagram", "Tabell", "Anföranden"],
                        index=0,
                        key="wt_display_select",
                        help=None,
                        horizontal=True,
                    )
                if normalize:
                    data = self.normalize_word_per_year(data)
                self.display_results(data, kwic_like_data, col_page_select)

    def display_results(self, data: pd.DataFrame, kwic_like_data: pd.DataFrame, col_page_select:Any) -> None:
        with self.result_container:

            if st.session_state["wt_display_select"] == "Diagram":
                self.draw_line_figure(data)
                self.add_download_button(file_name='word_trends.csv', data=data)
        
            elif st.session_state["wt_display_select"] == "Tabell":
                with col_page_select:
                    st.selectbox('Antal resultat per sida',  options=[5,10,15], key=self.ROWS_PER_PAGE_TABLE)
                self.table_display_table.show_table(data)
            
        
            else:
                with col_page_select:
                    st.selectbox('Antal resultat per sida',  options=[5,10,15], key=self.ROWS_PER_PAGE_SOURCE)
                self.table_display_source.show_table(data=kwic_like_data, type="source")


            

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
        fig.update_yaxes(exponentformat = 'none')
        fig.update_layout(xaxis_title="År", yaxis_title="Frekvens")
        fig.update_layout(separators= ",   ")
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
