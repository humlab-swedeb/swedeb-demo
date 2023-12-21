from typing import List

import pandas as pd
import plotly.graph_objects as go  # type: ignore
import streamlit as st

import swedeb_demo.components.component_texts as ct
from swedeb_demo.api.dummy_api import ADummyApi  # type: ignore
from swedeb_demo.components.meta_data_display import MetaDataDisplay  # type: ignore
from swedeb_demo.components.speech_display_mixin import ExpandedSpeechDisplay
from swedeb_demo.components.table_results import TableDisplay
from swedeb_demo.components.tool_tab import ToolTab


class WordTrendsDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(
        self, another_api: ADummyApi, shared_meta: MetaDataDisplay, tab_key: str
    ) -> None:
        super().__init__(another_api, shared_meta, tab_key)

        self.labels = ct.wt_table_labels
        self.column_names = ct.wt_column_names

        self.SEARCH_PERFORMED = f"search_performed_{self.TAB_KEY}"
        self.CURRENT_PAGE_TAB = f"current_page_tab_{self.TAB_KEY}"
        self.CURRENT_PAGE_SOURCE = f"current_page_source_{self.TAB_KEY}"
        self.EXPANDED_SPEECH = f"expanded_speech_{self.TAB_KEY}"
        self.NORMAL_TABLE_WT = f"normalize_table_{self.TAB_KEY}"
        self.NORMAL_DIAGRAM_WT = f"normalize_diagram_{self.TAB_KEY}"
        self.DISPLAY_SELECT = f"display_select_{self.TAB_KEY}"
        self.SORT_KEY = f"sort_key_{self.TAB_KEY}"
        self.ASCENDING_KEY = f"ascending_{self.TAB_KEY}"
        self.DATA_KEY_TABLE = f"data_table_{self.TAB_KEY}"
        self.DATA_KEY_SOURCE = f"data_source_{self.TAB_KEY}"
        self.SEARCH_BOX = f"search_box_{self.TAB_KEY}"
        self.HIT_SELECTOR = f"hit_selector_{self.TAB_KEY}"
        self.words_per_year = self.api.get_words_per_year()
        self.NON_NORMALIZED = "Absolut frekvens"
        self.NORMALIZED = "Normaliserad frekvens"
        self.ANFORANDEN = ct.wt_option_anforanden
        self.TABELL = ct.wt_option_tabell
        self.DIAGRAM = ct.wt_option_diagram

        if self.has_and_is(self.EXPANDED_SPEECH):
            self.display_expanded_speech(
                self.get_reset_dict(),
                self.api,
                self.TAB_KEY,
                st.session_state["selected_hit"],
            )

        else:
            st.caption(ct.word_trend_desc)

            self.top_container = st.container()
            self.search_container = st.container()
            self.top_result_container = st.container()
            self.result_container = st.container()

            self.st_dict_when_button_clicked = {
                self.SEARCH_PERFORMED: True,
                self.CURRENT_PAGE_TAB: 0,
                self.CURRENT_PAGE_SOURCE: 0,
                self.EXPANDED_SPEECH: False,
            }

            self.define_displays()

            with self.search_container:
                self.draw_search_settings()

            if self.has_and_is(self.SEARCH_PERFORMED):
                self.show_display()
            else:
                self.init_session_state(self.get_initial_values())

    def draw_search_settings(self):
        with st.form(key=f"form_{self.TAB_KEY}"):
            st.text_input(ct.wt_text_input, key=self.SEARCH_BOX)
            st.form_submit_button(
                ct.wt_search_button, on_click=self.handle_button_click
            )
        self.draw_line()

    def get_initial_values(self):
        session_state_initial_values = {
            # self.SEARCH_PERFORMED: False,
            self.CURRENT_PAGE_TAB: 0,
            self.CURRENT_PAGE_SOURCE: 0,
            self.NORMAL_TABLE_WT: self.NON_NORMALIZED,
            self.NORMAL_DIAGRAM_WT: self.NON_NORMALIZED,
            self.EXPANDED_SPEECH: False,
        }

        return session_state_initial_values

    def get_reset_dict(self) -> dict:
        return {
            self.SEARCH_PERFORMED: True,
            self.CURRENT_PAGE_SOURCE: st.session_state[self.CURRENT_PAGE_SOURCE],
            self.SEARCH_BOX: self.get_current_search_as_str(),
            self.DISPLAY_SELECT: self.ANFORANDEN,
            self.EXPANDED_SPEECH: False,
            self.HIT_SELECTOR: self.get_selected_hits(),
        }

    def get_current_search_as_str(self) -> str:
        if self.SEARCH_BOX in st.session_state:
            return st.session_state[self.SEARCH_BOX]
        return ""

    def get_selected_hits(self):
        if self.HIT_SELECTOR in st.session_state:
            return st.session_state[self.HIT_SELECTOR]
        return ""

    def handle_button_click(self) -> None:
        if self.get_search_box().strip() == "":
            st.warning("Fyll i en sökterm")
            st.session_state[self.SEARCH_PERFORMED] = False
        else:
            self.handle_search_click(self.st_dict_when_button_clicked)

    def define_displays(self) -> None:
        self.table_display_table = TableDisplay(
            current_container_key=self.TAB_KEY,
            current_page_name=self.CURRENT_PAGE_TAB,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key="",
            table_type=ct.wt_table_type,
            data_key=self.DATA_KEY_TABLE,
        )
        self.table_display = TableDisplay(
            current_container_key=self.TAB_KEY,
            current_page_name=self.CURRENT_PAGE_SOURCE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key=self.EXPANDED_SPEECH,
            table_type=ct.wt_source_type,
            data_key=self.DATA_KEY_SOURCE,
        )

    @st.cache_data
    def get_data(
        _self,
        search_words: List[str],
        start_year: int,
        end_year: int,
        selections: dict,
    ) -> pd.DataFrame:
        st.session_state["word_trend_selections"] = selections
        df = _self.api.get_word_trend_results(
            search_words,
            filter_opts=selections,
            start_year=start_year,
            end_year=end_year,
        )
        total = 0
        if len(df.columns) == 1:
            total = df.sum(axis=0)[0]
        elif len(df.columns) > 1:
            df["Totalt"] = df.sum(axis=1)
            total = df["Totalt"].sum(axis=0)

        df.reset_index(inplace=True)
        df.rename(columns={"year": "År"}, inplace=True)
        df.set_index(df.columns[0], inplace=True)
        return df, total

    @st.cache_data
    def get_anforanden(
        _self,
        search_words: List[str],
        start_year: int,
        end_year: int,
        selections: dict,
    ) -> pd.DataFrame:
        return _self.api.get_anforanden_for_word_trends(
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
        slider = self.search_display.get_slider()
        selections = self.search_display.get_selections()
        search_terms = self.get_search_terms()

        if len(search_terms) > 0:
            with self.search_container:
                st.session_state[self.HIT_SELECTOR] = st.multiselect(
                    label=ct.wt_hit_selector, options=search_terms, default=search_terms
                )
                data, total = self.get_data(
                    self.get_selected_hits(),
                    slider[0],
                    slider[1],
                    selections,
                )

            with self.top_result_container:
                self.draw_line()
                if data.empty:
                    self.display_settings_info_no_hits()
                else:
                    self.draw_result(self.get_selected_hits(), data, total)
        else:
            self.display_settings_info_no_hits()

    def draw_result(self, selected_hits, data, total):
        self.display_settings_info(n_hits=total, hits=f": {', '.join(selected_hits)}")

        col_display_select, down_a, down_b = st.columns([2, 1, 1])
        with col_display_select:
            self.add_radio_buttons()
        with down_a:
            st.write("")
            self.add_download_button(
                data,
                ct.wt_filename,
                button_label="Ladda ner ordfrekvenser",
                index=True,
            )
        """    
        with down_b:
            st.write("")
            self.add_download_button(
                kwic_like_data,
                ct.wt_filename_speeches,
                button_label="Ladda ner anföranden",
            )
        """
        self.draw_line()
        self.display_results(data)

    def add_radio_buttons(self):
        st.radio(
            ct.wt_options_desc,
            ct.wt_result_options,
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
        normalize = st.session_state[normalization_key] == self.NORMALIZED
        if normalize:
            data = self.normalize_word_per_year(data)
        return data

    def display_results(self, data: pd.DataFrame) -> None:
        with self.result_container:
            if st.session_state[self.DISPLAY_SELECT] == self.DIAGRAM:
                data = self.normalize(data, self.NORMAL_DIAGRAM_WT)
                self.draw_line_figure(data)

            elif st.session_state[self.DISPLAY_SELECT] == self.TABELL:
                data = self.normalize(data, self.NORMAL_TABLE_WT)
                st.session_state[self.DATA_KEY_TABLE] = data
                self.table_display_table.write_table()

            else:
                kwic_like_data = self.get_anforanden(
                    st.session_state[self.HIT_SELECTOR],
                    self.search_display.get_slider()[0],
                    self.search_display.get_slider()[1],
                    self.search_display.get_selections(),
                )
                self.add_anforande_display(kwic_like_data)

    def add_anforande_display(self, kwic_like_data):
        st_columns = self.table_display.get_columns(include_hit=True)
        self.add_sort_buttons(self.labels, st_columns[:-1], self.column_names)

        with st_columns[-1]:
            st.write(ct.wt_speech_col)

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
            ct.wt_norm_radio_title,
            (self.NON_NORMALIZED, self.NORMALIZED),
            key=key,
            help=ct.wt_norm_help,
            horizontal=True,
        )

    def draw_line_figure(self, data: pd.DataFrame) -> None:
        markers = ct.wt_plot_markers
        lines = ct.wt_plot_lines
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
        fig.update_layout(xaxis_title=ct.wt_x_axis, yaxis_title=ct.wt_y_asix)
        fig.update_layout(separators=",   ")
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
