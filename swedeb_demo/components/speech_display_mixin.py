import streamlit as st
from swedeb_demo.api.dummy_api import ADummyApi  # type: ignore
from typing import List


class ExpandedSpeechDisplay:
    def display_expanded_speech(
        self,
        reset_dict: dict,
        api: ADummyApi,
        tab_key: str,
        search_terms: List[str] = None,
    ) -> None:
        
        selected_protocol = st.session_state["selected_protocol"]
        
        chamber = 'Andra kammaren' if 'ak' in selected_protocol else 'Första kammaren'
        
        simplified_protocol = selected_protocol.split("-")[1] + ":" + selected_protocol.split("-")[5].split('_')[0]
        dummy_pdf = "https://www.riksdagen.se/sv/sok/?avd=dokument&doktyp=prot"
        link = f"[{simplified_protocol}]({dummy_pdf})"
        col_1, col_3 = st.columns([3, 1])
        
            #**Anförande**: {selected_protocol}
        with col_1:
            
            info_text = f"""
            **Talare**: {st.session_state['selected_speaker']}    
            **År**: {st.session_state['selected_year']}  

            **Hela protokollet** {link}, {chamber}
            
            **Talarnotering**: {api.get_speaker_note(selected_protocol)}(
            
            
            """
            st.info(info_text)

        with col_3:
            st.button(
                "Stäng och återgå",
                key=f"close_button_{tab_key}",
                on_click=self.reset_speech_state,
                args=(reset_dict,),
            )
        st.write('**Hela anförandet:**')
        text = api.get_speech_text(st.session_state["selected_protocol"])
        text = text.replace("\n", "<br><br>")
        if search_terms is not None:
            for search_term in search_terms:
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
