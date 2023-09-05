from __future__ import annotations

from typing import Iterable

import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore


class PartyDropDown:
    def __init__(self, another_api: ADummyApi) -> None:
        self.api = another_api
        self.party_to_id = self.api.party_specs
        self.id_to_party = {v: k for k, v in self.party_to_id.items()}
        self.draw_selector()

    def draw_selector(self) -> None:
        css = self.get_css_for_all(self.party_to_id.values(), self.party_to_id.keys())
        st.markdown(css, unsafe_allow_html=True)
        self.selector = st.multiselect(
            "Välj partier",
            self.id_to_party.keys(),
            format_func=self.format_party,
            default=[],
            key="party_dropdown",
        )

    def generate_css_for_party_id(self, party_id: int, part_abbrev: str) -> str:
        color = self.api.party_id_to_color.get(party_id, "#000000")
        return f"""
        span[data-baseweb="tag"][aria-label="{part_abbrev}, close by backspace"]{{
            background-color: {color};
        }}

        """

    def get_css_for_all(
        self, party_ids: Iterable[int], party_abbrevs: Iterable[str]
    ) -> str:
        css = ""
        for party_id, party_abbrev in zip(party_ids, party_abbrevs):
            css += self.generate_css_for_party_id(party_id, party_abbrev)
        return f"\n<style>{css}</style>\n"

    def format_party(self, x: int) -> str:
        return self.id_to_party[x]

    def get_selection(self) -> dict | None:
        if len(self.selector) == 0:
            return None
        return {"party_id": self.selector}

    def get_selected_parties_string(self) -> str:
        if len(self.selector) == 0:
            return "**Valda partier**: Alla. "
        party_str = ", ".join([self.id_to_party[x] for x in self.selector])
        return f"**Valda partier**: {party_str}. "
