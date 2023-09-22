from .tool_tab import ToolTab
from .speech_display_mixin import ExpandedSpeechDisplay
from typing import Any

import pandas as pd
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore

from .table_results import TableDisplay



class FullSpeechDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(
        self, another_api: ADummyApi, shared_meta: MetaDataDisplay, tab_key: str
    ) -> None:
        super().__init__(another_api, shared_meta, tab_key)

        self.CURRENT_PAGE = f"current_page_{self.TAB_KEY}"
        self.SEARCH_PERFORMED = f"search_performed_{self.TAB_KEY}"
        self.EXPANDED_SPEECH = f"expanded_speech_{self.TAB_KEY}"
        self.ROWS_PER_PAGE = f"rows_per_page_{self.TAB_KEY}"
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
                self.ROWS_PER_PAGE: 5,
            }
            self.st_dict_when_button_clicked = {
                self.CURRENT_PAGE: 0,
                self.SEARCH_PERFORMED: True,
                self.EXPANDED_SPEECH: False,
            }

            st.caption(
                "Sök på hela anföranden. Välj tidsintervall, partier, kön och talare till vänster."
            )
            self.top_container = st.container()
            self.bottom_container = st.container()

            self.table_display = TableDisplay(
                current_container_key=self.TAB_KEY,
                current_page_name=self.CURRENT_PAGE,
                party_abbrev_to_color=self.api.party_abbrev_to_color,
                expanded_speech_key=self.EXPANDED_SPEECH,
                rows_per_table_key=self.ROWS_PER_PAGE,
                table_type="source",
                data_key=self.DATA_KEY,
            )

            with self.top_container:
                self.add_search_button("Visa anföranden")
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
                self.add_hits_per_page(self.ROWS_PER_PAGE)
                self.add_download_button(anforanden, "anforanden.csv")
            self.draw_line()

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
                    "Talare↕",
                    key="sort_button",
                    on_click=self.set_sorting,
                    args=("Talare",),
                )
            with gender_col:
                st.button(
                    "Kön↕",
                    key="button könssortering",
                    on_click=self.set_sorting,
                    args=("Kön",),
                )
            with year_col:
                st.button(
                    "År↕",
                    key="button årsortering",
                    on_click=self.set_sorting,
                    args=("År",),
                )
            with party_col:
                st.button(
                    "Parti↕",
                    key="button partisortering",
                    on_click=self.set_sorting,
                    args=("Parti",),
                )
            with link_col:
                st.button(
                    "Källa↕",
                    key="button protokollsortering",
                    on_click=self.set_sorting,
                    args=("Protokoll",),
                )

            if self.SORT_KEY in st.session_state:
                anforanden.sort_values(
                    st.session_state[self.SORT_KEY],
                    ascending=st.session_state[self.ASCENDING_KEY],
                    inplace=True,
                )

            st.session_state[self.DATA_KEY] = anforanden
            self.table_display.write_table()
