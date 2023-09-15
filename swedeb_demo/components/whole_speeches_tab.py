from typing import Any

import pandas as pd
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore

from .table_results import TableDisplay
from .tool_tab import ToolTab

from .speech_display_mixin import ExpandedSpeechDisplay


class FullSpeechDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(self, another_api: ADummyApi, shared_meta: MetaDataDisplay) -> None:
        super().__init__(another_api, shared_meta, "full_form")

        CURRENT_PAGE = "current_page_full"
        SEARCH_PERFORMED = "search_performed_full"
        self.EXPANDED_SPEECH = "expanded_speech_full"
        self.ROWS_PER_PAGE = "rows_per_page_full"
        self.DATA_KEY = "data_full"
        self.SORT_KEY = "sort_key_full"
        self.ASCENDING_KEY = "ascending_full"

        if (
            self.EXPANDED_SPEECH in st.session_state
            and st.session_state[self.EXPANDED_SPEECH]
        ):
            reset_dict = {self.EXPANDED_SPEECH: False}
            self.display_speech(reset_dict, self.api, self.FORM_KEY)
        else:
            session_state_initial_values = {
                CURRENT_PAGE: 0,
                SEARCH_PERFORMED: False,
                self.EXPANDED_SPEECH: False,
                self.ROWS_PER_PAGE: 5,
            }
            self.st_dict_when_button_clicked = {
                CURRENT_PAGE: 0,
                SEARCH_PERFORMED: True,
                self.EXPANDED_SPEECH: False,
            }

            st.caption(
                "Sök på hela anföranden. Välj tidsintervall, partier, kön och talare till vänster."
            )
            self.top_container = st.container()
            self.bottom_container = st.container()

            self.table_display = TableDisplay(
                current_container_key="FULL_SOURCE",
                current_page_name=CURRENT_PAGE,
                party_abbrev_to_color=self.api.party_abbrev_to_color,
                expanded_speech_key=self.EXPANDED_SPEECH,
                rows_per_table_key=self.ROWS_PER_PAGE,
                table_type="source",
                data_key=self.DATA_KEY,
                sort_key=self.SORT_KEY,
                ascending_key=self.ASCENDING_KEY,
            )

            with self.top_container:
                st.button(
                    "Visa anföranden",
                    key=f"search_button_{self.FORM_KEY}",
                    on_click=self.handle_button_click,
                )
                self.draw_line()

            self.init_session_state(session_state_initial_values)

            if st.session_state[SEARCH_PERFORMED]:
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
            _, col_right = st.columns([4,2])
           
            with col_right:
                st.selectbox(
                    "Antal resultat per sida",
                    options=[5, 10, 20, 50],
                    key=self.ROWS_PER_PAGE,
                )
            
            (
            speaker_col,
            gender_col,
            year_col,
            party_col,
            link_col,
            expander_col,
            ) = self.table_display.get_columns()

            with speaker_col:
   
                button_sort = st.button('Talare↕', key='sort_button')
            with gender_col:
                button_sort_gender = st.button('Kön↕', key='button könssortering')
            with year_col:
                button_sort_year = st.button('År↕', key='button årsortering')
            with party_col:
                button_sort_party = st.button('Parti↕', key='button partisortering')
            with link_col:
                st.write("Källa")
            with expander_col:
                st.write("Tal")
            sort_key = None
            if button_sort:
                ascending=self.get_sort_direction('talare_sortering_full')
                sort_key = 'Talare'
                self.table_display.reset_page()
            elif button_sort_gender:
                ascending=self.get_sort_direction('gender_sortering_full')
                sort_key = 'Kön'
                self.table_display.reset_page()

            elif button_sort_year:
                ascending=self.get_sort_direction('year_sortering_full')
                sort_key = 'År'
                self.table_display.reset_page()

            elif button_sort_party:
                ascending = self.get_sort_direction('party_sortering_full')
                sort_key = 'Parti'
                self.table_display.reset_page()

            
            if sort_key is not None:
            
                st.session_state[self.SORT_KEY] = sort_key
                st.session_state[self.ASCENDING_KEY] = ascending
                anforanden.sort_values(st.session_state[self.SORT_KEY], ascending=st.session_state[self.ASCENDING_KEY], inplace=True)
            
        

            st.session_state[self.DATA_KEY] = anforanden
            self.table_display.write_table()
