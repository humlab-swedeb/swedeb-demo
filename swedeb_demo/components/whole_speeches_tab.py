from typing import Any

import pandas as pd
import streamlit as st
from api.dummy_api import ADummyApi # type: ignore
from components.meta_data_display import MetaDataDisplay # type: ignore

from .table_results import TableDisplay
from .tool_tab import ToolTab


class FullSpeechDisplay(ToolTab):
    def __init__(self, another_api: ADummyApi, shared_meta: MetaDataDisplay) -> None:
        super().__init__(another_api, shared_meta, "full_form")
        st.caption("Sök på hela anföranden. Välj tidsintervall, partier, kön och talare till vänster.")
        self.top_container = st.container()
        self.middle_container = st.container()
        self.bottom_container = st.container()

        CURRENT_PAGE = "current_page_full"
        SEARCH_PERFORMED = "search_performed_full"

        self.hits_per_page = 6
        self.table_display = TableDisplay(
            self.hits_per_page,
            current_container_key="FULL_SOURCE",
            current_page_name=CURRENT_PAGE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
        )

        session_state_initial_values = {CURRENT_PAGE: 0, SEARCH_PERFORMED: False}
        st_dict_when_button_clicked = {CURRENT_PAGE: 0, SEARCH_PERFORMED: True}

        with self.middle_container:
            self.show_button = st.button(
                "Visa anföranden", key=f"search_button_{self.FORM_KEY}"
            )
            self.draw_line()

        self.init_session_state(session_state_initial_values)

        if self.show_button:
            for k, v in st_dict_when_button_clicked.items():
                st.session_state[k] = v

        if st.session_state[SEARCH_PERFORMED]:
            self.show_display()

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
            self.table_display.show_table(anforanden, type="source")
            self.add_download_button(anforanden, "anforanden.csv")
