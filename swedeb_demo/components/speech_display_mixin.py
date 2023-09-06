import streamlit as st
from api.dummy_api import ADummyApi  # type: ignore


class ExpandedSpeechDisplay:
    def display_speech(
        self, reset_dict: dict, api: ADummyApi, tab_key: str, search_term: str = None
    ) -> None:
        col_1, col_3 = st.columns([3, 1])
        with col_1:
            selected_protocol = st.session_state["selected_protocol"]
            info_text = f"""
            Talare: {st.session_state['selected_speaker']}    
            År: {st.session_state['selected_year']}  
            Anförande: {selected_protocol}
            """
            st.info(info_text)

        with col_3:
            st.button(
                "Stäng och återgå",
                key=f"close_button_{tab_key}",
                on_click=self.reset_speech_state,
                args=(reset_dict,),
            )

        text = api.get_speech_text(st.session_state["selected_protocol"])
        if search_term is not None:
            text = text.replace(
                search_term,
                f'<span style="background-color: #FFFF00">{search_term}</span>',
            )
        st.markdown(
            f'<p style="border-width:2px; border-style:solid; border-color:#000000; padding: 1em;">{text}</p>',
            unsafe_allow_html=True,
        )

    def reset_speech_state(self, reset_dict: dict) -> None:
        st.session_state["selected_protocol"] = None
        for k, v in reset_dict.items():
            st.session_state[k] = v
