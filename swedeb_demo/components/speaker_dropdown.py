from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore


class SpeakerDropDown:
    def __init__(
        self, another_api: ADummyApi, party_selections: dict, gender_selections: dict
    ) -> None:
        self.api = another_api
        self.speakers = self.api.decoded_persons
        self.party_selections = party_selections
        self.gender_selections = gender_selections
        self.selector = self.draw_multiselect()

    def draw_multiselect(self) -> Any:
        current_speakers = self.get_speakers_for_selected_parties()
        if self.gender_selections is not None:
            current_speakers = self.get_speakers_selected_genders(current_speakers)
        return st.multiselect(
            "Sök enskilda talare",
            current_speakers.index,
            format_func=self.format_speaker,
            default=[],
            key="speaker_dropdown",
        )

    def get_speakers_selected_genders(
        self, current_speakers: pd.DataFrame
    ) -> pd.DataFrame:
        return current_speakers[
            current_speakers["gender_id"].isin(self.gender_selections["gender_id"])
        ]

    def get_speakers_for_selected_parties(self) -> pd.DataFrame:
        if self.party_selections is not None:
            return self.speakers[
                self.speakers["party_id"].isin(self.party_selections["party_id"])
            ]
        return self.speakers

    def format_speaker(self, x: str) -> str:
        if (birth_year := self.speakers.loc[x, "year_of_birth"]) != 0:
            birth_year = f"{birth_year} - "
        else:
            birth_year = ""
        if (death_year := self.speakers.loc[x, "year_of_death"]) == 0:
            death_year = ""
        return f'{self.speakers.loc[x, "name"]} ({self.speakers.loc[x, "party_abbrev"]}) {birth_year} {death_year}'

    def get_selection(self) -> dict | None:
        if len(self.selector) == 0:
            return None
        return {"who": self.selector}

    def get_selected_speakers_string(self) -> str:
        if len(self.selector) == 0:
            return "Alla talare"
        return f"**Valda talare**: {', '.join([self.format_speaker(x) for x in self.selector])}.\n"
