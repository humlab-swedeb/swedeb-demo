from __future__ import annotations

import streamlit as st
from swedeb_demo.components import component_texts as ct


class GenderCheckBoxes:
    def __init__(self) -> None:
        self.G_CHECK_MEN = "gender_check_men"
        self.G_CHECK_WOMEN = "gender_check_women"
        self.G_CHECK_UNK = "gender_check_unknown"
        self.G_KEY = "use_gender_filter"
        st.checkbox(
            "Filtrera på kön?",
            value=False,
            key=self.G_KEY,
            on_change=self.set_box_values,
        )
        disabled = not st.session_state[self.G_KEY]

        st.checkbox("Män", disabled=disabled, key=self.G_CHECK_MEN)
        st.checkbox("Kvinnor", disabled=disabled, key=self.G_CHECK_WOMEN)
        st.checkbox("Kön okänt", disabled=disabled, key=self.G_CHECK_UNK)

    def set_box_values(self) -> None:
        st.session_state[self.G_CHECK_UNK] = True
        st.session_state[self.G_CHECK_WOMEN] = True
        st.session_state[self.G_CHECK_MEN] = True

    def get_selection(self) -> dict | None:
        if st.session_state[self.G_KEY]:
            selected = []
            if st.session_state[self.G_CHECK_MEN]:
                selected.append(1)
            if st.session_state[self.G_CHECK_WOMEN]:
                selected.append(2)
            if st.session_state[self.G_CHECK_UNK]:
                selected.append(0)
            if selected:
                return {"gender_id": selected}
        return None

    def get_selected_genders_string(self) -> str:
        if st.session_state[self.G_KEY]:
            selected = []

            if st.session_state[self.G_CHECK_MEN]:
                selected.append("Män")

            if st.session_state[self.G_CHECK_WOMEN]:
                selected.append("Kvinnor")

            if st.session_state[self.G_CHECK_UNK]:
                selected.append("Okänt kön")

            gender_str = ", ".join(selected)
            if not selected:
                return ct.g_hint
            return f"**Valda kön**: {gender_str}.\n"
        return "**Valda kön**: Alla"
