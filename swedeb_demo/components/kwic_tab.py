from typing import Any, List

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
            "Med verktyget **Key Words in Context** kan du söka på ord och fraser, t.ex. `information` eller `information om`. För att få fler träffar kan `.*` användas, t.ex. `information.*`. Under Filtrera sökresultatet kan du avgränsa sökningen till vissa partier, talare eller år. "
        )
        self.top_container = st.container()
        self.result_desc_container = st.container()
        self.n_hits_container = st.container()
        self.result_container = st.container()

        # search performed necessary to keep results when switching tabs
        self.SEARCH_PERFORMED = "search_performed_kwic"
        self.CURRENT_PAGE = "current_page_kwic"
        self.ROWS_PER_PAGE = "rows_per_page_kwic"
        self.DATA_KEY = "data_kwic"
        self.SORT_KEY = "sort_key_kwic"
        self.ASCENDING_KEY = "ascending_kwic"
        self.EXPANDED_SPEECH = "expanded_speech_kwic"

        self.st_dict_when_button_clicked = {
            self.SEARCH_PERFORMED: True,
            self.CURRENT_PAGE: 0,
        }
        session_state_initial_values = {
            self.SEARCH_PERFORMED: False,
            self.CURRENT_PAGE: 0,
            self.ROWS_PER_PAGE: 5,
        }

        self.init_session_state(session_state_initial_values)
        self.define_displays()

        with self.top_container:
            st.text_input("Skriv sökterm:", key=f"search_box_{self.FORM_KEY}")
            self.add_window_size()

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
                max_value=5,
                value=2,
            )
        with cols_after:
            st.number_input(
                "Antal ord efter sökordet",
                key=f"n_words_after_{self.FORM_KEY}",
                min_value=0,
                max_value=5,
                value=2,
            )

    def define_displays(self) -> None:
        self.table_display = TableDisplay(
            current_container_key=self.FORM_KEY,
            current_page_name=self.CURRENT_PAGE,
            party_abbrev_to_color=self.api.party_abbrev_to_color,
            expanded_speech_key=self.EXPANDED_SPEECH,
            rows_per_table_key=self.ROWS_PER_PAGE,
            table_type="kwic",
            data_key=self.DATA_KEY,
            sort_key=self.SORT_KEY,
            ascending_key=self.ASCENDING_KEY,
        )

        

    def show_display(self) -> None:
        
        hit = self.get_search_box()
        if hit:
            hits = [h.strip() for h in hit.split(' ')]
            self.show_hit(hits)
            with self.n_hits_container:
                st.selectbox(
                    "Antal resultat per sida",
                    options=[5, 10, 20, 50],
                    key=self.ROWS_PER_PAGE,
                )
        else:
            self.display_settings_info_no_hits()

    def show_hit(self, hits: List[str]) -> None:
        data = self.get_data(
            hits,
            self.search_display.get_slider(),
            selections=self.search_display.get_selections(),
            words_before=st.session_state[f"n_words_before_{self.FORM_KEY}"],
            words_after
            =st.session_state[f"n_words_after_{self.FORM_KEY}"],
        )

        if data.empty:
            self.display_settings_info_no_hits()
        else:
            with self.result_desc_container:
                self.display_settings_info()
            with self.result_container:
                (
                    left_col,
                    hit_col,
                    right_col,
                    party_col,
                    year_col,
                    link_col,
                    gender_col,
                    proto_col,
                    expander_col,
                    ) = self.table_display.get_kwick_columns()
                
                with left_col:
                    st.write("Vänster")
                    button_sort_left = st.button('↕', key='sort_button_left')
                with hit_col:
                    st.write("Träff")
                    button_sort_hit = st.button('↕', key='sort_button_hit')
                with right_col:
                    st.write("Höger")
                    button_sort_right = st.button('↕', key='sort_button_right')

                with party_col:
                    st.markdown("**Parti**")
                    button_sort_party = st.button('↕', key='button partisortering_kwic')
                with year_col:
                    st.markdown("**År**")
                    button_sort_year = st.button('↕', key='button årsortering_kwic')
                with link_col:
                    st.markdown("**Talare**")
                    button_sort_link = st.button('↕', key='sort_button_kwic')
                with gender_col:
                    st.markdown("**Kön**")
                    button_sort_gender = st.button('↕', key='button könssortering_kwic')
                with proto_col:
                    st.markdown("**Källa**")
                    button_sort_source = st.button('↕', key='button källsortering_kwic')
       
         
                sort_key = None
                if button_sort_left:
                    ascending=self.get_sort_direction('left_sortering_kwic')
                    sort_key = 'Kontext Vänster'

                elif button_sort_hit:
                    ascending=self.get_sort_direction('hit_sortering_kwic')
                    sort_key = 'Sökord'
                
                elif button_sort_right:
                    ascending=self.get_sort_direction('right_sortering_kwic')
                    sort_key = 'Kontext Höger'
                
                
                elif button_sort_gender:
                    ascending=self.get_sort_direction('gender_sortering_kwic')
                    sort_key = 'Kön'

                elif button_sort_year:
                    ascending=self.get_sort_direction('year_sortering_kwic')
                    sort_key = 'År'

                elif button_sort_party:
                    ascending = self.get_sort_direction('party_sortering_kwic')
                    sort_key = 'Parti'
                elif button_sort_link:
                    ascending = self.get_sort_direction('link_sortering_kwic')
                    sort_key = 'Talare'
                elif button_sort_source:
                    ascending = self.get_sort_direction('source_sortering_kwic')
                    sort_key = "Protokoll"

                
                if sort_key is not None:
                
                    self.table_display.reset_page()
                    st.session_state[self.SORT_KEY] = sort_key
                    st.session_state[self.ASCENDING_KEY] = ascending
                    data.sort_values(st.session_state[self.SORT_KEY], ascending=st.session_state[self.ASCENDING_KEY], inplace=True)
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
    ) -> pd.DataFrame:
        data = _self.api.get_kwic_results_for_search_hits(
            hits,
            from_year=slider[0],
            to_year=slider[1],
            selections=selections,
            words_before=words_before,
            words_after=words_after,
        )

        return data
