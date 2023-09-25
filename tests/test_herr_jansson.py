
import pytest
from swedeb_demo.api.dummy_api import ADummyApi
import pandas as pd
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)

@pytest.fixture
def api_fixture():
    api = ADummyApi('.env_example')
    return api


def test_herr_j(api_fixture) -> None:
    # Talarintroduktion: Herr JANSSON (vpk):
    # sök på endast kvinnor, parti: M 
    # år 1968
    # ord i kontext Saker . debatten har inte 
    # ger error i streamlit, men hjälper att ta bort < och > från texten

    protocol = "prot-1968--ak--18_031"
    text = api_fixture.get_speech_text(protocol)
    print(text)


def test_get(api_fixture):
    """
    I Kwic när man söker på ordet "information" 
    och talaren Anna-Lisa Lewén-Eliasson Q4961902
    så får man ett resultat där "information" ska finnas i 
    protokoll prot-1960--ak--14_056

    (Det protokollet blir också resultatet i jupyter-notebooken)

    Det protokollet hör dock till Hans Nordgren Q6157349
    och innehåller inte "information"

    Om man istället söker i word_trends på "information" och
    Anna-Lisa Lewén-Eliasson, så får man ett protokoll som
    resultat:  prot-1960--ak--14_058

    Det protokollet innhåller "information"
    
    Det verkar därför som att vissa (inte alla) protokoll i 
    kwic-data har blivit taggade med fel protokoll-id
    """

    search_term = 'information'
    kwic_anna_lisa_information = api_fixture.get_kwic_results_for_search_hits([search_term], 1960, 1960, {'who':['Q4961902']}, 5, 5, lemmatized=False)  # noqa: E501
    kwic_anna_lisa_information = kwic_anna_lisa_information[['Kontext Vänster', 
                                                             'Sökord',
                                                             'Talare', 
                                                             'Kön', 
                                                             'Protokoll', 
                                                             'person_id']]

    #prot-1960--ak--14_056 också i jupyter  (samma resultat)
    print('_____resultat kwic Anna-Lisa Lewén-Eliasson "information"______')
    print(kwic_anna_lisa_information)
    protocol_id = kwic_anna_lisa_information.iloc[0]['Protokoll'] 
    speech = api_fixture.get_speech_text(protocol_id)
    if search_term not in speech:
        print('______motsvarande tal enligt protokoll-id i kwic-resultatet_________')
        speech_info = api_fixture.get_speech(protocol_id)

        print('\nTEXT: ',speech)
        print('WHO:  ', speech_info['who']) # Q6157349
        print('NAME:  ', speech_info['name']) # Hans Nordgren
        print('PROTOKOLL: ', speech_info['document_name']) #prot-1960--ak--14_056

    
    _, speeches_anna_lisa = api_fixture.get_word_trend_results([search_term],  {'who':['Q4961902']}, 1960, 1960)  # noqa: E501

    print('____protokoll för anförande med "information" Anna-Lisa Lewén-Eliasson_____')
    print(speeches_anna_lisa['Protokoll'])
    correct = api_fixture.get_speech_text(speeches_anna_lisa['Protokoll'].iloc[0])
    assert search_term in correct
                                                                        
                                                                        
   


