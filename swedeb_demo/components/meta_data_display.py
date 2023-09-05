from __future__ import annotations

from typing import Any, Optional

import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore

from .gender_checkboxes import GenderCheckBoxes
from .party_dropdown import PartyDropDown
from .speaker_dropdown import SpeakerDropDown


# tid, parti, kön, (kammare, valkrets), namn
class MetaDataDisplay:
    def __init__(self, st_dict: Any, api: ADummyApi) -> None:
        self.st_dict = st_dict
        self.another_api = api
        self.min_year = self.another_api.get_years_start()
        self.max_year = self.another_api.get_years_end()
        self.add_filter_components()

    def add_filter_components(self) -> None:
        self.slider = st.slider(
            "Välj intervall:",
            value=[self.min_year, self.max_year],
            min_value=self.min_year,
            max_value=self.max_year,
            key="years_slider",
        )
        self.column_container = st.container()

        with self.column_container:
            self.gender_boxes = GenderCheckBoxes()
            self.party_dropdown = PartyDropDown(self.another_api)
            self.speaker_dropdown = SpeakerDropDown(
                self.another_api,
                self.party_dropdown.get_selection(),
                self.gender_boxes.get_selection(),
            )

    def get_slider(self) -> Any:
        return self.slider

    def get_gender_selection(self) -> Optional[dict]:
        return self.gender_boxes.get_selection()

    def get_party_selection(self) -> dict | None:
        return self.party_dropdown.get_selection()

    def get_speaker_selection(self) -> dict | None:
        return self.speaker_dropdown.get_selection()

    def get_selections(self) -> dict:
        selections = {}
        gs = self.gender_boxes.get_selection()
        ps = self.party_dropdown.get_selection()
        ss = self.speaker_dropdown.get_selection()
        if gs is not None:
            selections.update(gs)
        if ps is not None:
            selections.update(ps)
        if ss is not None:
            selections.update(ss)
        return selections

    def get_selected_years_str(self) -> str:
        selected_years = self.get_slider()
        return f"**Intervall:** {selected_years[0]} – {selected_years[1]}"

    def get_current_settings(self) -> str:
        if self.speaker_dropdown.get_selected_speakers_string() == "Alla talare":
            return " ".join(
                [
                    self.gender_boxes.get_selected_genders_string(),
                    self.party_dropdown.get_selected_parties_string(),
                    self.get_selected_years_str(),
                ]
            )
        else:
            return " ".join(
                [
                    self.speaker_dropdown.get_selected_speakers_string(),
                    self.get_selected_years_str(),
                ]
            )
