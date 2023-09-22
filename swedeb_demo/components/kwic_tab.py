from typing import Any, List

import pandas as pd
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore
from components.meta_data_display import MetaDataDisplay  # type: ignore

from .table_results import TableDisplay
from .tool_tab import ToolTab

from .speech_display_mixin import ExpandedSpeechDisplay


class KWICDisplay(ExpandedSpeechDisplay, ToolTab):
    def __init__(
        self, another_api: ADummyApi, shared_meta: MetaDataDisplay, tab_key: str
    ) -> None:
        super().__init__(another_api, shared_meta, tab_key)

        self.CURRENT_PAGE = f"current_page_{self.TAB_KEY}"
        self.SEARCH_PERFORMED = f"search_performed__{self.TAB_KEY}"
        self.EXPANDED_SPEECH =f"expanded_speech__{self.TAB_KEY}"
        self.ROWS_PER_PAGE = f"rows_per_page__{self.TAB_KEY}"
        self.DATA_KEY = f"data_{self.TAB_KEY}"
        self.SORT_KEY = f"sort_key_{self.TAB_KEY}"
        self.ASCENDING_KEY = f"ascending_{self.TAB_KEY}"
        st.caption(
            "Med verktyget **Key Words in Context** kan du söka på ord och fraser, t.ex. `information` eller `information om`. För att få fler träffar kan `.*` användas, t.ex. `.*information.*`. Under Filtrera sökresultatet kan du avgränsa sökningen till vissa partier, talare eller år. "
        )

        if self.has_and_is(self.EXPANDED_SPEECH):
            self.display_expanded_speech(
                self.get_reset_dict(), self.api, self.TAB_KEY, search_terms=None
            )
        else:
            self.top_container = st.container()
            self.result_desc_container = st.container()
            self.n_hits_container = st.container()
            self.result_container = st.container()

            self.st_dict_when_button_clicked = {
                self.SEARCH_PERFORMED: True,
                self.CURRENT_PAGE: 0,
                self.EXPANDED_SPEECH: False,
            }

            self.define_displays()

            with self.top_container:
                st.text_input("Skriv sökterm:", key=f"search_box_{self.TAB_KEY}")
                self.add_window_size()
                self.add_search_button("Sök")
                self.draw_line()

            self.init_session_state(self.get_initial_values())
            if st.session_state[self.SEARCH_PERFORMED]:
                self.show_display()

    def get_initial_values(self) -> dict:
        return {
            self.SEARCH_PERFORMED: False,
            self.CURRENT_PAGE: 0,
            self.ROWS_PER_PAGE: 5,
        }

    def handle_button_click(self) -> None:
        if not self.handle_search_click(self.st_dict_when_button_clicked):
            st.session_state[self.SEARCH_PERFORMED] = False

    def add_window_size(self) -> None:
        cols_before, cols_after, _ = st.columns([2, 2, 2])
        with cols_before:
            self.add_window_select(
                "Antal ord före sökordet", f"n_words_before_{self.TAB_KEY}"
            )
        with cols_after:
            self.add_window_select(
                "Antal ord efter sökordet", f"n_words_after_{self.TAB_KEY}"
            )

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
            rows_per_table_key=self.ROWS_PER_PAGE,
            table_type="kwic",
            data_key=self.DATA_KEY,
        )

    def get_reset_dict(self) -> dict:
        reset = {
            self.SEARCH_PERFORMED: True,
            self.CURRENT_PAGE: st.session_state[self.CURRENT_PAGE],
            self.EXPANDED_SPEECH: False,
        }
        if f"search_box_{self.TAB_KEY}" in st.session_state:
            reset[f"search_box_{self.TAB_KEY}"] = st.session_state[
                f"search_box_{self.TAB_KEY}"
            ]
        else:
            reset[f"search_box_{self.TAB_KEY}"] = self.get_search_box()

        return reset

    def show_display(self) -> None:
        hit = self.get_search_box()
        if hit:
            hits = [h.strip() for h in hit.split(" ")]
            self.show_hit(hits)
            with self.n_hits_container:
                self.add_hits_per_page(self.ROWS_PER_PAGE)
        else:
            self.display_settings_info_no_hits()

    def show_hit(self, hits: List[str]) -> None:
        data = self.get_data(
            hits,
            self.search_display.get_slider(),
            selections=self.search_display.get_selections(),
            words_before=st.session_state[f"n_words_before_{self.TAB_KEY}"],
            words_after=st.session_state[f"n_words_after_{self.TAB_KEY}"],
        )

        if data.empty:
            self.display_settings_info_no_hits()
        else:
            with self.n_hits_container:
                self.add_download_button(data, "kwic.csv")
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
                    # gender_col,
                    proto_col,
                    # expander_col,
                ) = self.table_display.get_kwick_columns()

                with left_col:
                    st.button(
                        "Vänster",
                        key="sb_left_kwic",
                        on_click=self.set_sorting,
                        args=("Kontext Vänster",),
                    )
                with hit_col:
                    st.button(
                        "Träff",
                        key="sb_hit_kwic",
                        on_click=self.set_sorting,
                        args=("Sökord",),
                    )
                with right_col:
                    st.button(
                        "Höger",
                        key="sb_right_kwic",
                        on_click=self.set_sorting,
                        args=("Kontext Höger",),
                    )
                with party_col:
                    st.button(
                        "Parti",
                        key="sb_party_kwic",
                        on_click=self.set_sorting,
                        args=("Parti",),
                    )
                with year_col:
                    st.button(
                        "År",
                        key="sb_year_kwic",
                        on_click=self.set_sorting,
                        args=("År",)
                    )
                with link_col:

                    
                    st.button(
                        "Talare",
                        key="sb_speaker_kwic",
                        on_click=self.set_sorting,
                        args=("Talare",)
                    )
              
                # with gender_col:
                #    st.markdown("**Kön**")
                #    st.button('↕', key='button könssortering_kwic', on_click=self.set_sorting('Kön',))

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
