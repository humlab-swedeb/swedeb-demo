from typing import Any, List

import pandas as pd
import streamlit as st

import swedeb_demo.components.component_texts as ct
from swedeb_demo.api.dummy_api import ADummyApi  # type: ignore
from swedeb_demo.components.meta_data_display import \
    MetaDataDisplay  # type: ignore
from swedeb_demo.components.speech_display_mixin import ExpandedSpeechDisplay
from swedeb_demo.components.table_results import TableDisplay
from swedeb_demo.components.tool_tab import ToolTab


class KWICDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(
        self, another_api: ADummyApi, shared_meta: MetaDataDisplay, tab_key: str
    ) -> None:
        super().__init__(another_api, shared_meta, tab_key)
        self.labels = ct.kwic_labels
        self.column_names = ct.kwic_col_names

        self.CURRENT_PAGE = f"current_page_{self.TAB_KEY}"
        self.SEARCH_PERFORMED = f"search_performed__{self.TAB_KEY}"
        self.EXPANDED_SPEECH = f"expanded_speech__{self.TAB_KEY}"
        self.DATA_KEY = f"data_{self.TAB_KEY}"
        self.SORT_KEY = f"sort_key_{self.TAB_KEY}"
        self.ASCENDING_KEY = f"ascending_{self.TAB_KEY}"
        self.SEARCH_BOX = f"search_box_{self.TAB_KEY}"
        self.N_WORDS_BEFORE = f"n_words_before_{self.TAB_KEY}"
        self.N_WORDS_AFTER = f"n_words_after_{self.TAB_KEY}"
        self.LEMMA_WORD_TOGGLE = f"lemma_word_toggle_{self.TAB_KEY}"
        st.caption(ct.kwic_desc)

        if self.has_and_is(self.EXPANDED_SPEECH):
            self.display_expanded_speech(
                self.get_reset_dict(), self.api, self.TAB_KEY, search_terms=None
            )
        else:
            self.add_containers()
            self.define_displays()

            with self.top_container:
                self.draw_search_settings()

            self.init_session_state(self.get_initial_values())
            if st.session_state[self.SEARCH_PERFORMED]:
                self.show_display()

    def draw_search_settings(self):
        st.text_input(ct.kwic_text_input, key=self.SEARCH_BOX)
        self.add_window_size()
        self.add_lemma_word_toggle()
        self.add_search_button(ct.kwic_search_button)
        self.draw_line()

    def get_st_dict_when_button_clicked(self) -> dict:
        return {
            self.SEARCH_PERFORMED: True,
            self.CURRENT_PAGE: 0,
            self.EXPANDED_SPEECH: False,
        }

    def add_containers(self):
        self.top_container = st.container()
        self.result_desc_container = st.container()
        self.n_hits_container = st.container()
        self.result_container = st.container()

    def add_lemma_word_toggle(self) -> None:
        st.toggle(ct.kwic_lemma_toggle, key=self.LEMMA_WORD_TOGGLE)

    def get_initial_values(self) -> dict:
        return {
            self.SEARCH_PERFORMED: False,
            self.CURRENT_PAGE: 0,
        }

    def handle_button_click(self) -> None:
        if not self.handle_search_click(self.get_st_dict_when_button_clicked()):
            st.session_state[self.SEARCH_PERFORMED] = False

    def add_window_size(self) -> None:
        cols_before, cols_after, _ = st.columns([2, 2, 2])
        with cols_before:
            self.add_window_select(ct.kwic_word_before, self.N_WORDS_BEFORE)
        with cols_after:
            self.add_window_select(ct.kwic_words_after, self.N_WORDS_AFTER)

    def add_window_select(self, message: str, key: str):
        st.number_input(
            message,
            key=key,
            min_value=0,
            max_value=5,
            value=2,
        )

    def define_displays(self) -> None:
        self.table_display = TableDisplay(
            current_container_key=self.TAB_KEY,
            current_page_name=self.CURRENT_PAGE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key=self.EXPANDED_SPEECH,
            table_type=ct.kwic_table_type,
            data_key=self.DATA_KEY,
        )

    def get_reset_dict(self) -> dict:
        reset = {
            self.SEARCH_PERFORMED: True,
            self.CURRENT_PAGE: st.session_state[self.CURRENT_PAGE],
            self.EXPANDED_SPEECH: False,
        }
        if self.SEARCH_BOX in st.session_state:
            reset[self.SEARCH_BOX] = st.session_state[self.SEARCH_BOX]
        else:
            reset[self.SEARCH_BOX] = self.get_search_box()  # obs

        return reset

    def show_display(self) -> None:
        hit = self.get_search_box()
        if hit:
            hits = [h.strip() for h in hit.split(" ")]
            self.show_hit(hits)
        else:
            self.display_settings_info_no_hits()

    def show_hit(self, hits: List[str]) -> None:
        selections = self.search_display.get_selections()
        st.session_state['kwic_selections'] = selections
        data = self.get_data(
            hits,
            self.search_display.get_slider(),
            selections=selections,
            words_before=st.session_state[self.N_WORDS_BEFORE],
            words_after=st.session_state[self.N_WORDS_AFTER],
            lemmatized=not st.session_state[self.LEMMA_WORD_TOGGLE],
        )

        if data.empty:
            self.display_settings_info_no_hits()
        else:
            with self.n_hits_container:
                self.add_download_button(data, ct.kwic_filename)
            with self.result_desc_container:
                self.display_settings_info()
            with self.result_container:
                st_columns = self.table_display.get_kwick_columns()
                self.add_sort_buttons(self.labels, st_columns[:-1], self.column_names)

                with st_columns[-1]:
                    st.markdown(ct.kwic_show_speeches)

                if self.SORT_KEY in st.session_state:
                    data.sort_values(
                        st.session_state[self.SORT_KEY],
                        ascending=st.session_state[self.ASCENDING_KEY],
                        inplace=True,
                    )

                st.session_state[self.DATA_KEY] = data
                self.table_display.write_table()

    @st.cache_data
    def get_data(
        _self,
        hits: List[str],
        slider: Any,
        selections: dict,
        words_before: int,
        words_after: int,
        lemmatized: bool = True,
    ) -> pd.DataFrame:
        data = _self.api.get_kwic_results_for_search_hits(
            hits,
            from_year=slider[0],
            to_year=slider[1],
            selections=selections,
            words_before=words_before,
            words_after=words_after,
            lemmatized=lemmatized,
        )

        return data
