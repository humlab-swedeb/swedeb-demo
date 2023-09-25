######################
# KWIC display texts #
######################
kwic_desc = """Med verktyget **Key Words in Context** kan du söka på ord och fraser, 
t.ex.\`information` eller `information om`. För att få fler träffar kan `.*` användas, 
t.ex. `.*information.*`. Under Filtrera sökresultatet kan du avgränsa sökningen 
till vissa partier, talare eller år. """
kwic_lemma_toggle = "Exakt match (ej lemmatiserat)"
kwic_word_before = "Antal ord före sökordet"
kwic_words_after = "Antal ord efter sökordet"

# KWIC table
kwic_table_type = "kwic"

# KWIC download filename
kwic_filename = "kwic.csv"

# KWIC table display
kwic_labels = ["Vänster", "Träff", "Höger", "Parti", "År", "Talare", "Kön"]
kwic_col_names = [
    "Kontext Vänster",
    "Sökord",
    "Kontext Höger",
    "Parti",
    "År",
    "Talare",
    "Kön",
]

# KWIC search button
kwic_search_button = "Sök"
kwic_text_input = "Skriv sökterm:"

# KWIC show speeches
kwic_show_speeches = "Visa anföranden"

###############################
# WORD TRENDs display texts   #
###############################

word_trend_desc = """Sök på ett begrepp för att se hur det använts över tid. För att 
 söka på flera termer, skriv dem med kommatecken, t.ex. `debatt,information`. Sök med 
 `*` för att få fler varianter, t.ex. `debatt*`. Välj vilka talare ska ingå i 
 filtreringen till vänster."""

# word trends table/plot/speeches
wt_table_type = "table"
wt_source_type = "source"
wt_speech_col = "Tal"

# word trends search settings
wt_hit_selector = "Välj sökord att inkludera"
wt_option_tabell = "Tabell"
wt_option_diagram = "Diagram"
wt_option_anforanden = "Anföranden"
wt_result_options = [wt_option_diagram, wt_option_tabell, wt_option_anforanden]
wt_options_desc = "Visa resultat som:"
wt_text_input = "Skriv sökterm:"
wt_search_button = "Sök"

# word trends normalization
wt_norm_radio_title = "Normalisera resultatet?"
wt_norm_help = """Frekvens: antal förekomster av söktermen per år. Normaliserad 
frekvens: antal förekomster av söktermen delat med totalt antal ord i tal 
under samma år."""

# word trends table display
wt_table_labels = ["Talare↕", "Kön↕", "År↕", "Parti↕", "Källa↕"]
wt_column_names = ["Talare", "Kön", "År", "Parti", "Protokoll"]

# word trends plot settings
wt_plot_markers = ["circle", "hourglass", "x", "cross", "square", 5]
wt_plot_lines = ["solid", "dash", "dot", "dashdot", "solid"]
wt_x_axis = "År"
wt_y_asix = "Frekvens"

# word trends download filename
wt_filename = "word_trends.csv"


###############################
# SPEECHES display texts      #
###############################

sp_desc = (
    "Sök på hela anföranden. Välj tidsintervall, partier, kön och talare till vänster."
)

# speeches table
sp_table_type = "source"

# speeches table display
sp_labels = ["Talare↕", "År↕", "Kön↕", "Parti↕", "Källa↕"]
sp_col_names = ["Talare", "År", "Kön", "Parti", "Protokoll"]

# speeches search settings
sp_search_button = "Visa anföranden"

# speeches download filename
sp_filename = "anforanden.csv"

###############################
# Main page display texts     #
###############################

# header
m_title = "Svenska riksdagsdebatter"

# corpus selectbox
m_corpus_selectbox = "Välj korpus"
m_corpus_selectbox_help = "Välj vilket korpus du vill arbeta med"
m_corpus_selectbox_options = ["Riksdagsdebatter, 1960-1969"]

# meta sidebar settings
m_meta_header = "Filtrera sökresultat"
m_meta_help = """Filtrera sökresultatet efter metadata, t.ex. kön, parti, och 
tidsperiod. Filtreringen påverkar alla verktyg."""
m_meta_caption = "Filtreringen påverkar resultaten för alla verktyg"
m_meta_expander = "Visa filtreringsalternativ"

# hits per page
m_hits_per_page = "Antal resultat per sida"
m_hits_options = [5, 10, 20, 50]

# tabs
m_kwic_tab = "KWIC"
m_wt_tab = "WT"
m_sp_tab = "SPEECH"
m_ngram_caption = "Här kommer information om verktyget **N-gram**"
m_topics_caption = "Här kommer information om verktyget **Temamodeller**"

# about tab
m_about_caption = "Här kommer information om SweDebprojektet och verktygen"
m_faq = "FAQ"
m_faq_Q1 = "Vad är detta?"
m_faq_A1 = """En prototyp utvecklad för att undersöka möjligheterna med att 
tillgängliggöra riksdagsdebatter"""
m_faq_Q2 = "Hur använder man den här prototypen?"
m_faq_A2 = """I vänsterspalten kan du välja vilken data du vill undersöka. 
I de olika flikarna kan du välja vilket verktyg du vill använda 
för att undersöka materialet."""


###############################
# Gender checkboxes texts     #
###############################

g_hint = "Välj kön i menyn till vänster för att visa resultat för enskilda grupper  \n"