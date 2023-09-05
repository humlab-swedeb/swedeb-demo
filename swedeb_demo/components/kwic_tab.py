from typing import Any

import pandas as pd
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore

from .table_results import TableDisplay
from .tool_tab import ToolTab


class KWICDisplay(ToolTab):
    def __init__(self, another_api: ADummyApi, shared_meta: MetaDataDisplay) -> None:
        super().__init__(another_api, shared_meta, "kwick_form")
        st.caption(
            "Med verktyget **Key Words in Context** kan du söka på enskilda ord och begrepp. Det går också att söka med \* för att få flera träffar. Exempelvis 'debatt*' "
        )
        self.top_container = st.container()
        self.middle_container = st.container()
        self.search_button_container = st.container()
        self.result_desc_container = st.container()
        self.word_confirm_container = st.container()

        # search performed necessary to keep results when switching tabs
        self.SEARCH_PERFORMED = "search_performed_kwic"
        self.CURRENT_PAGE = "current_page_kwic"

        self.hits_per_page = 10

        self.st_dict_when_button_clicked = {
            self.SEARCH_PERFORMED: True,
            self.CURRENT_PAGE: 0,
        }
        session_state_initial_values = {
            self.SEARCH_PERFORMED: False,
            self.CURRENT_PAGE: 0,
        }

        self.init_session_state(session_state_initial_values)
        self.define_displays()

        with self.middle_container:
            st.text_input("Skriv sökterm:", key=f"search_box_{self.FORM_KEY}")
            self.add_window_size()

        with self.search_button_container:
            st.button(
                "Sök",
                key=f"search_button_{self.FORM_KEY}",
                on_click=self.handle_button_click,
            )
            self.draw_line()

        if st.session_state[self.SEARCH_PERFORMED]:
            self.show_display()

    def handle_button_click(self) -> None:
        if not self.handle_search_click(self.st_dict_when_button_clicked):
            st.session_state[self.SEARCH_PERFORMED] = False

    def add_window_size(self) -> None:
        cols_before, cols_after, _ = st.columns([2, 2, 2])
        with cols_before:
            st.number_input(
                "Antal ord före sökordet",
                key=f"n_words_before_{self.FORM_KEY}",
                min_value=0,
                max_value=1,
                value=1,
            )
        with cols_after:
            st.number_input(
                "Antal ord efter sökordet",
                key=f"n_words_after_{self.FORM_KEY}",
                min_value=0,
                max_value=1,
                value=1,
            )

    def define_displays(self) -> None:
        self.table_display = TableDisplay(
            self.hits_per_page,
            current_container_key=self.FORM_KEY,
            current_page_name=self.CURRENT_PAGE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key="not_used",  # TODO: fix
        )

    def show_display(self) -> None:
        hits = self.api.get_word_hits(self.get_search_box())

        if hits:
            with self.word_confirm_container:
                hit_selector = self.add_hit_selector(hits)
            if hit_selector:
                self.show_hits(hit_selector)
            else:
                self.display_settings_info_no_hits()
        else:
            self.display_settings_info_no_hits()

    def show_hits(self, hit_selector: Any) -> None:
        data = self.get_data(
            hit_selector,
            self.search_display.get_slider(),
            selections=self.search_display.get_selections(),
            words_before=st.session_state[f"n_words_before_{self.FORM_KEY}"],
            words_after=st.session_state[f"n_words_after_{self.FORM_KEY}"],
        )
        if data.empty:
            self.display_settings_info_no_hits()
        else:
            with self.result_desc_container:
                self.display_settings_info()
            self.table_display.show_table(data)
            self.add_download_button(data, file_name="kwic.csv")

    @st.cache_data
    def get_data(
        _self,
        hits: list[str],
        slider: Any,
        selections: dict,
        words_before: int,
        words_after: int,
    ) -> pd.DataFrame:
        data = _self.api.get_kwic_results_for_search_hits(
            hits,
            from_year=slider[0],
            to_year=slider[1],
            selections=selections,
            words_before=words_before,
            words_after=words_after,
        )

        if data.empty:
            return data
        data.rename(columns={"who": "ID"}, inplace=True)
        return data[["Tal", "Talare", "År", "Kön", "Parti", "Protokoll", "ID"]]
