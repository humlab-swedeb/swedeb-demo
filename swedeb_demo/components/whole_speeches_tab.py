from typing import Any

import pandas as pd
import streamlit as st

from swedeb_demo.api.dummy_api import ADummyApi  # type: ignore
from swedeb_demo.components import component_texts as ct
from swedeb_demo.components.meta_data_display import \
    MetaDataDisplay  # type: ignore
from swedeb_demo.components.speech_display_mixin import ExpandedSpeechDisplay
from swedeb_demo.components.table_results import TableDisplay
from swedeb_demo.components.tool_tab import ToolTab


class FullSpeechDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(
        self, another_api: ADummyApi, shared_meta: MetaDataDisplay, tab_key: str
    ) -> None:
        super().__init__(another_api, shared_meta, tab_key)

        self.labels = ct.sp_labels
        self.column_names = ct.sp_col_names
        self.CURRENT_PAGE = f"current_page_{self.TAB_KEY}"
        self.SEARCH_PERFORMED = f"search_performed_{self.TAB_KEY}"
        self.EXPANDED_SPEECH = f"expanded_speech_{self.TAB_KEY}"
        self.DATA_KEY = f"data_{self.TAB_KEY}"
        self.SORT_KEY = f"sort_key_{self.TAB_KEY}"
        self.ASCENDING_KEY = f"ascending_{self.TAB_KEY}"

        if self.has_and_is(self.EXPANDED_SPEECH):
            reset_dict = {self.EXPANDED_SPEECH: False}
            self.display_expanded_speech(reset_dict, self.api, self.TAB_KEY)
        else:
            session_state_initial_values = {
                self.CURRENT_PAGE: 0,
                self.SEARCH_PERFORMED: False,
                self.EXPANDED_SPEECH: False,
            }
            self.st_dict_when_button_clicked = {
                self.CURRENT_PAGE: 0,
                self.SEARCH_PERFORMED: True,
                self.EXPANDED_SPEECH: False,
            }

            st.caption(ct.sp_desc)
            self.top_container = st.container()
            self.bottom_container = st.container()

            self.table_display = TableDisplay(
                current_container_key=self.TAB_KEY,
                current_page_name=self.CURRENT_PAGE,
                party_abbrev_to_color=self.api.party_abbrev_to_color,
                expanded_speech_key=self.EXPANDED_SPEECH,
                table_type=ct.sp_table_type,
                data_key=self.DATA_KEY,
            )

            with self.top_container:
                self.add_search_button(ct.sp_search_button)
                self.draw_line()

            self.init_session_state(session_state_initial_values)

            if st.session_state[self.SEARCH_PERFORMED]:
                self.show_display()

    def handle_button_click(self) -> None:
        for k, v in self.st_dict_when_button_clicked.items():
            st.session_state[k] = v

    @st.cache_data
    def get_anforanden(
        _self, _another_api: Any, from_year: int, to_year: int, selections: dict
    ) -> pd.DataFrame:
        data = _another_api.get_anforanden(from_year, to_year, selections)
        return data

    def show_display(self) -> None:
        start_year, end_year = self.search_display.get_slider()

        anforanden = self.get_anforanden(
            self.api,
            start_year,
            end_year,
            selections=self.search_display.get_selections(),
        )
        if len(anforanden) == 0:
            self.display_settings_info_no_hits(with_search_hits=False)
        else:
            self.display_results(anforanden)

    def display_results(self, anforanden: pd.DataFrame) -> None:
        with self.bottom_container:
            self.display_settings_info(with_search_hits=False)
            _, col_right = st.columns([4, 2])

            with col_right:
                self.add_download_button(anforanden, ct.sp_filename)
            self.draw_line()

            columns = self.table_display.get_columns()

            self.add_sort_buttons(self.labels, columns, self.column_names)

            if self.SORT_KEY in st.session_state:
                anforanden.sort_values(
                    st.session_state[self.SORT_KEY],
                    ascending=st.session_state[self.ASCENDING_KEY],
                    inplace=True,
                )

            st.session_state[self.DATA_KEY] = anforanden
            self.table_display.write_table()
