from typing import Any, Tuple, List

import pandas as pd
import plotly.graph_objects as go  # type: ignore
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore

from .table_results import TableDisplay
from .tool_tab import ToolTab

from .speech_display_mixin import ExpandedSpeechDisplay


class WordTrendsDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(
        self, another_api: ADummyApi, shared_meta: MetaDataDisplay, tab_key: str
    ) -> None:
        super().__init__(another_api, shared_meta, tab_key)
        self.SEARCH_PERFORMED = "search_performed_wt"
        self.CURRENT_PAGE_TAB = "current_page_tab"
        self.CURRENT_PAGE_SOURCE = "current_page_source"
        self.EXPANDED_SPEECH = "expanded_speech_wt"
        self.ROWS_PER_PAGE_TABLE = "rows_per_page_wt_table"
        self.ROWS_PER_PAGE_SOURCE = "rows_per_page_wt_source"
        self.NORMAL_TABLE_WT = "normalize_table_wt"
        self.NORMAL_DIAGRAM_WT = "normalize_diagram_wt"
        self.DISPLAY_SELECT = "wt_display_select"
        self.words_per_year = self.api.get_words_per_year()
        self.SORT_KEY = "sort_key_wt_source"
        self.ASCENDING_KEY = "ascending_wt_source"
        self.DATA_KEY_TABLE = "data_wt_table"
        self.DATA_KEY_SOURCE = "data_wt_source"

        if self.has_and_is(self.EXPANDED_SPEECH):
            self.display_expanded_speech(
                self.get_reset_dict(),
                self.api,
                self.TAB_KEY,
                self.get_search_terms(),
            )
        else:
            st.caption(
                "Sök på ett begrepp för att se hur det använts över tid. För att söka på flera termer, skriv dem med kommatecken, t.ex. debatt,information. Sök med * för att få fler varianter, t.ex. debatt*. Välj vilka talare ska ingå till vänster."
            )

            self.top_container = st.container()
            self.search_container = st.container()
            self.top_result_container = st.container()
            self.result_container = st.container()

            self.st_dict_when_button_clicked = {
                self.SEARCH_PERFORMED: True,
                self.CURRENT_PAGE_TAB: 0,
                self.CURRENT_PAGE_SOURCE: 0,
            }

            self.init_session_state(self.get_initial_values())
            self.define_displays()

            with self.search_container:
                st.text_input("Skriv sökterm:", key=f"search_box_{self.TAB_KEY}")

                self.add_search_button("Sök")

            if st.session_state[self.SEARCH_PERFORMED]:
                self.show_display()

    def get_initial_values(self):
        session_state_initial_values = {
            self.SEARCH_PERFORMED: False,
            self.CURRENT_PAGE_TAB: 0,
            self.CURRENT_PAGE_SOURCE: 0,
            self.ROWS_PER_PAGE_SOURCE: 5,
            self.ROWS_PER_PAGE_TABLE: 5,
            self.NORMAL_TABLE_WT: "Frekvens",
            self.NORMAL_DIAGRAM_WT: "Frekvens",
        }

        return session_state_initial_values

    def get_reset_dict(self) -> dict:
        return {
            self.SEARCH_PERFORMED: True,
            self.CURRENT_PAGE_SOURCE: st.session_state[self.CURRENT_PAGE_SOURCE],
            f"search_box_{self.TAB_KEY}": self.get_current_search_as_str(),
            self.DISPLAY_SELECT: "Anföranden",
            self.EXPANDED_SPEECH: False,
        }

    def get_current_search_as_str(self) -> str:
        if f"search_box_{self.TAB_KEY}" in st.session_state:
            return st.session_state[f"search_box_{self.TAB_KEY}"]
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
            rows_per_table_key=self.ROWS_PER_PAGE_TABLE,
            table_type="table",
            data_key=self.DATA_KEY_TABLE,
        )
        self.table_display = TableDisplay(
            current_container_key="WT_SOURCE",
            current_page_name=self.CURRENT_PAGE_SOURCE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key=self.EXPANDED_SPEECH,
            rows_per_table_key=self.ROWS_PER_PAGE_SOURCE,
            table_type="source",
            data_key=self.DATA_KEY_SOURCE,
        )

    @st.cache_data
    def get_data(
        _self,
        search_words: List[str],
        start_year: int,
        end_year: int,
        selections: dict,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:

        return _self.api.get_word_trend_results(
            search_words,
            filter_opts=selections,
            start_year=start_year,
            end_year=end_year,
        )
    


    def normalize_word_per_year(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.merge(self.words_per_year, left_index=True, right_index=True)
        data = data.iloc[:, :].div(data.n_raw_tokens, axis=0)
        data.drop(columns=["n_raw_tokens"], inplace=True)

        return data

    def show_display(self) -> None:
        slider = st.session_state["years_slider"]

        selections = self.search_display.get_selections()
        hits = self.get_search_terms()

        if len(hits) > 0:
            with self.search_container:
                hit_selector = st.multiselect(
                    label="Välj sökord att inkludera", options=hits, default=hits
                )

            data, kwic_like_data = self.get_data(
                hit_selector,
                slider[0],
                slider[1],
                selections,
            )

            with self.top_result_container:
                self.draw_line()
                if kwic_like_data.empty:
                    self.display_settings_info_no_hits()
                else:
                    self.display_settings_info(hits=f": {', '.join(hits)}")

                    col_display_select, _, col_page_select = st.columns([2, 1, 1])
                    with col_display_select:
                        self.add_radio_buttons()
                    self.add_download_button(data, "word_trends.csv")
                    self.draw_line()
                    self.display_results(data, kwic_like_data, col_page_select)
        else:
            st.info(
                f"Inga träffar för **{self.get_search_box()}**, försök med andra sökord."
            )

    def add_radio_buttons(self):
        st.radio(
            "Visa resultat som:",
            ["Diagram", "Tabell", "Anföranden"],
            index=0,
            key=self.DISPLAY_SELECT,
            help=None,
            horizontal=True,
        )

    def get_search_terms(self):
        search_terms = self.get_search_box().split(",")
        search_terms = [term.strip().lower() for term in search_terms]

        hits = self.parse_search_string(search_terms)
        return hits

    def parse_search_string(self, search_terms):
        hits = []
        if len(search_terms) > 0:
            for term in search_terms:
                current_hits = self.api.get_word_hits(term, n_hits=10)
                for hit in current_hits:
                    hits.append(hit)
                hits.extend(current_hits)
        hits = list(set(hits))
        return hits

    def normalize(self, data, normalization_key):
        self.radio_normalize(normalization_key)
        normalize = st.session_state[normalization_key] == "Normaliserad frekvens"
        if normalize:
            data = self.normalize_word_per_year(data)
        return data

    def display_results(
        self, data: pd.DataFrame, kwic_like_data: pd.DataFrame, col_page_select: Any
    ) -> None:
        with self.result_container:
            if st.session_state[self.DISPLAY_SELECT] == "Diagram":
                data = self.normalize(data, self.NORMAL_DIAGRAM_WT)
                self.draw_line_figure(data)

            elif st.session_state[self.DISPLAY_SELECT] == "Tabell":
                data = self.normalize(data, self.NORMAL_TABLE_WT)
                st.session_state[self.DATA_KEY_TABLE] = data
                with col_page_select:
                    self.add_hits_per_page(self.ROWS_PER_PAGE_TABLE)
                self.table_display_table.write_table()

            else:
                with col_page_select:
                    self.add_hits_per_page(self.ROWS_PER_PAGE_SOURCE)

                self.add_anforande_display(kwic_like_data)

    def add_anforande_display(self, kwic_like_data):
        (
            speaker_col,
            gender_col,
            year_col,
            party_col,
            link_col,
            expander_col,
        ) = self.table_display.get_columns()

        with speaker_col:
            st.button(
                "Talare↕", key="sb_t_wt", on_click=self.set_sorting, args=("Talare",)
            )
        with gender_col:
            st.button("Kön↕", key="sb_k_wt", on_click=self.set_sorting, args=("Kön",))
        with year_col:
            st.button("År↕", key="sb_y_wt", on_click=self.set_sorting, args=("År",))
        with party_col:
            st.button(
                "Parti↕", key="sb_p_wt", on_click=self.set_sorting, args=("Parti",)
            )
        with link_col:
            st.button(
                "Källa↕", key="sb_l_wt", on_click=self.set_sorting, args=("Protokoll",)
            )

        with expander_col:
            st.write("Tal")

        if self.SORT_KEY in st.session_state:
            kwic_like_data.sort_values(
                st.session_state[self.SORT_KEY],
                ascending=st.session_state[self.ASCENDING_KEY],
                inplace=True,
            )

        st.session_state[self.DATA_KEY_SOURCE] = kwic_like_data
        self.table_display.write_table()

    def radio_normalize(self, key):
        st.radio(
            "Normalisera resultatet?",
            ("Frekvens", "Normaliserad frekvens"),
            key=key,
            help="Frekvens: antal förekomster av söktermen per år. Normaliserad frekvens: antal förekomster av söktermen delat med totalt antal ord i tal under samma år.",
            horizontal=True,
        )

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
        fig.update_yaxes(exponentformat="none")
        fig.update_layout(xaxis_title="År", yaxis_title="Frekvens")
        fig.update_layout(separators=",   ")
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
