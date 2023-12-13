######################
# KWIC display texts #
######################
kwic_desc = """Med verktyget **Key Words in Context** kan du söka på ord och fraser, 
t ex `information` eller `information om`, och se kontexten till vänster och 
höger om sökningen. För att få fler träffar kan `.*` användas, 
t ex `information.*`. Under Filtrera sökresultat kan du avgränsa 
anförandena till vissa partier, talare eller år. Observera att denna test-korpus är 
lemmatiserad, dvs sökresultateten baseras på ordets grammatiska rot."""
kwic_toggle = "Exakt match (ej lemmatiserat)"
kwic_word_before = "Antal ord före sökordet (0–5 ord)"
kwic_words_after = "Antal ord efter sökordet (0–5 ord)"
kwic_toggle_help = (
    "Lemmatisering ger fler träffar eftersom "
    "även böjningsformer av sökordet inkluderas"
)
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
kwic_update_button = "Uppdatera sökning"
kwic_text_input = "Skriv sökterm:"

# KWIC show speeches
kwic_show_speeches = "Visa anföranden"

###############################
# WORD TRENDs display texts   #
###############################

word_trend_desc = (
    "Sök på ett eller flera ord för att se hur de har använts över tid. "
    "För att söka på flera ord särskilj med kommatecken, t ex `debatt,information`. "
    "Sök med `*` för att få fler varianter, t.ex. `debatt*`. Under Filtrera "
    "sökresultat kan du avgränsa anförandena till vissa partier, talare eller år. "
    "Observera att denna test-korpus är lemmatiserad, dvs sökresultateten "
    "baseras på ordets grammatiska rot."
)

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
wt_table_labels = ["Talare↕", "Kön↕", "År↕", "Parti↕", "Källa↕", "Träff↕"]
wt_column_names = ["Talare", "Kön", "År", "Parti", "Protokoll", "hit"]

# word trends plot settings
wt_plot_markers = ["circle", "hourglass", "x", "cross", "square", 5]
wt_plot_lines = ["solid", "dash", "dot", "dashdot", "solid"]
wt_x_axis = "År"
wt_y_asix = "Frekvens"

# word trends download filename
wt_filename = "Ordtrender_frekvens.csv"
wt_filename_speeches = "Ordtrender_anforanden.csv"


###############################
# SPEECHES display texts      #
###############################

sp_desc = (
    "Sök på hela anföranden. Under Filtrera sökresultat kan du avgränsa anförandena "
    "till vissa partier, talare eller år. Observera att du i dagsläget endast "
    "kan ladda ner en lista med metadata om anföranden och inte talen "
    "i sig (men det kommer man kunna göra i den färdiga versionen)."
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
m_corpus_selectbox_help = "Välj vilket korpus du vill arbeta med."
m_corpus_selectbox_options = ["Riksdagsanföranden 1920-2021"]

# meta sidebar settings
m_meta_header = "Filtrera sökresultat"
m_meta_help = """Filtrera sökresultatet efter metadata, t.ex. kön, parti, och 
tidsperiod. Filtreringen påverkar alla verktyg."""
m_meta_caption = "Filtreringen påverkar resultaten för alla verktyg"
m_meta_expander = "Filtreringsalternativ"

# hits per page
m_hits_per_page = "Antal resultat per sida"
m_hits_options = [10, 20, 50]

# tabs
m_kwic_tab = "KWIC"
m_wt_tab = "WT"
m_sp_tab = "SPEECH"
m_ngram_caption = """Under utveckling. I den färdiga versionen kommer det gå att 
utforska olika fraser, dess frekvenser och kontexter."""
m_topics_caption = """Under utveckling. I den färdiga versionen kommer det gå att 
utforska olika temamodeller (eng ”topic models”) och t ex följa teman över tid och 
dess relation till varandra."""

# about tab

humlab_link = "https://www.umu.se/humlab/"
humlab = f"[Humlab]({humlab_link})"
swerik_link = "https://swerik-project.github.io"
swerik = f"[Swerik]({swerik_link})"
fredrik_link = "https://mau.se/personer/fredrik.noren/"
fredrik = f"[Fredrik Mohammadi Norén]({fredrik_link})"

m_about_caption = (
    "SweDeb (Swedish Parliamentary Debates) är ett "
    "infrastrukturprojekt "
    f"som finansieras av Umeå universitet (2023–2024) och utvecklas av {humlab} – "
    "universitetets center för digital humaniora. Syftet med SweDeb är att ta "
    "fram ett användarvänligt gränssnitt som forskare och studenter kan "
    "använda för att utforska alla riksdagsanföranden från 1867 och framåt. "
    "Det färdiga gränssnittet ska lanseras i slutet av 2024.\n\n"
    "Det underliggande datasetet till SweDeb (dvs riksdagsanförandena) hämtas "
    f"från det RJ-finansierade infrastrukturprojektet {swerik}, vars syfte bl a "
    "är att (1) skapa "
    "en databas med alla riksdagsledamöter sedan 1867, (2) annotera kammarens "
    "protokoll "
    "och märka upp alla enskilda anföranden för att sedan (3) koppla samman "
    "varje anförande med aktuell ledamot.\n\n"
    f"För frågor om SweDeb eller Swerik kontakta projektledare {fredrik} "
)


###############################
# Gender checkboxes texts     #
###############################

g_hint = "Välj kön i menyn till vänster för att visa resultat för enskilda grupper  \n"
