from __future__ import annotations
import streamlit as st


class GenderCheckBoxes:
    def __init__(self) -> None:
        st.checkbox(
            "Filtrera på kön?",
            value=False,
            key="use_gender_filter",
            on_change=self.set_box_values,
        )
        disabled = not st.session_state["use_gender_filter"]

        st.checkbox("Män", disabled=disabled, key="gender_check_men")
        st.checkbox("Kvinnor", disabled=disabled, key="gender_check_women")
        st.checkbox("Kön okänt", disabled=disabled, key="gender_check_unknown")

    def set_box_values(self) -> None:
        st.session_state["gender_check_unknown"] = True
        st.session_state["gender_check_women"] = True
        st.session_state["gender_check_men"] = True

    def get_selection(self) -> dict | None:
        if st.session_state["use_gender_filter"]:
            selected = []
            if st.session_state["gender_check_men"]:
                selected.append(1)
            if st.session_state["gender_check_women"]:
                selected.append(2)
            if st.session_state["gender_check_unknown"]:
                selected.append(0)
            if selected:
                return {"gender_id": selected}
        return None

    def get_selected_genders_string(self) -> str:
        if st.session_state["use_gender_filter"]:
            selected = []

            if st.session_state["gender_check_men"]:
                selected.append("Män")

            if st.session_state["gender_check_women"]:
                selected.append("Kvinnor")

            if st.session_state["gender_check_unknown"]:
                selected.append("Okänt kön")

            gender_str = ", ".join(selected)
            if not selected:
                return f"Välj kön i menyn till vänster för att visa resultat för enskilda grupper  \n"
            return f"**Valda kön**: {gender_str}.\n"
        return "**Valda kön**: Alla"
