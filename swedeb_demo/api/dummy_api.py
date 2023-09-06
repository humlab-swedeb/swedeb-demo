from __future__ import annotations
import os

import pandas as pd
import penelope.utility as pu  # type: ignore
from dotenv import load_dotenv
from penelope.common.keyness import KeynessMetric  # type: ignore
from penelope.corpus import VectorizedCorpus  # type: ignore
from penelope.utility import PropertyValueMaskingOpts  # type: ignore

from .parlaclarin.trends_data import SweDebComputeOpts, SweDebTrendsData
from .westac.riksprot.parlaclarin import codecs as md
from .westac.riksprot.parlaclarin import speech_text as sr

from typing import Union, Mapping, Tuple

import streamlit as st


class ADummyApi:
    """Dummy API for testing and developing the SweDeb GUI"""

    def __init__(self, env_file: str = ".env_sample_data") -> None:
        load_dotenv(env_file)
        self.tag: str = os.getenv("TAG")
        self.folder = os.getenv("FOLDER")
        METADATA_FILENAME = os.getenv("METADATA_FILENAME")
        TAGGED_CORPUS_FOLDER = os.getenv("TAGGED_CORPUS_FOLDER")

        self.load_corpus()
        self.data: md.Codecs = md.Codecs().load(source=METADATA_FILENAME)

        self.person_codecs: md.PersonCodecs = md.PersonCodecs().load(
            source=METADATA_FILENAME
        )

        self.repository: sr.SpeechTextRepository = sr.SpeechTextRepository(
            source=TAGGED_CORPUS_FOLDER,
            person_codecs=self.person_codecs,
            document_index=self.corpus.document_index,
        )

        self.gender_to_swedish = {"man": "Man", "woman": "Kvinna", "unknown": "Okänt"}

        self.party_specs = self.get_party_specs()
        self.decoded_persons = self.data.decode(
            self.person_codecs.persons_of_interest, drop=False
        )
        self.possible_pivots = [
            v["text_name"] for v in self.person_codecs.property_values_specs
        ]
        self.party_id_to_color = dict(
            zip(self.data.party.index, self.data.party.party_color)
        )
        self.party_abbrev_to_color = dict(
            zip(self.data.party.party_abbrev, self.data.party.party_color)
        )

    def load_corpus(self) -> None:
        self.corpus = VectorizedCorpus.load(folder=self.folder, tag=self.tag)

    def get_party_specs(self) -> Union[str, Mapping[str, int]]:
        for specification in self.data.property_values_specs:
            if specification["text_name"] == "party_abbrev":
                return specification["values"]

    def get_word_hits(self, search_term: str, n_hits: int = 5) -> list[str]:
        return self.corpus.find_matching_words({f"{search_term}"}, n_hits)

    def get_speech(self, document_name: str):  # type: ignore
        return self.repository.speech(speech_name=document_name, mode="dict")

    def get_speech_text(self, document_name: str):  # type: ignore
        return self.repository.to_text(self.get_speech(document_name))

    def get_word_vectors(
        self, words: list[str], corpus: VectorizedCorpus = None
    ) -> dict:
        """Returns individual corpus columns vectors for each search term

        Args:
            words: list of strings (search terms)
            corpus (VectorizedCorpus, optional): current corpus in None. Defaults to None.

        Returns:
            dict: key: search term, value: corpus column vector
        """
        vectors = {}
        if corpus is None:
            corpus = self.corpus

        for word in words:
            vectors[word] = corpus.get_word_vector(word)
        return vectors

    def add_speech(
        self,
        row: pd.Series,
        words_before: int = -1,
        words_after: int = -1,
        no_match_len_short: int = 20,
        no_match_len_long: int = 200,
    ) -> tuple[str, str, str, str, str, str, str, str]:
        """Returns speech-related data for a row of selected data"""
        current_speech = self.get_speech(row["document_name"])
        speech_text = self.repository.to_text(current_speech)
        current_hit = None
        if "hit" in row:
            current_hit = row["hit"]

        speech_text_short, speech_text_longer = self.get_sample_text(
            speech_text,
            current_hit,
            no_match_len_long,
            no_match_len_short,
            words_before,
            words_after,
        )
        return (
            speech_text_short,
            speech_text_longer,
            current_speech["party_abbrev"],
            str(current_speech["year"]),
            current_speech["document_name"],
            current_speech["name"],
            self.gender_to_swedish[current_speech["gender"]],
            current_speech["who"],
        )

    def get_sample_text(
        self,
        speech_text: str,
        current_hit: str,
        len_long_sample: int,
        len_short_sample: int,
        words_before: int,
        words_after: int,
    ) -> Tuple[str, str]:
        """Returns samples of the speech text, with the current search term highlighted


        Args:
            speech_text str: Text content of current speech
            current_hit str: Current search term
            no_match_len_long int: Length of longer sample text
            no_match_len_short int: Length of shorter sample text
            words_before int: words before current search term (for dummy kwic)
            words_after int: words after current search term (for dummy kwic)

        Returns:
            str, str: Shorter and longer sample text surrounding the current search term or text from beginning of speech if no match
        """
        if current_hit is None:
            return speech_text[0:len_short_sample], speech_text[0:len_long_sample]
        word_index = speech_text.find(current_hit)
        start_short = self.get_start_index(word_index, len_short_sample, words_before)
        end_short = self.get_end_index(
            word_index, len(current_hit), len_short_sample, words_after
        )
        start_long = self.get_start_index(word_index, len_long_sample)
        end_long = self.get_end_index(word_index, len(current_hit), len_long_sample)
        shorter = speech_text[start_short:end_short]
        shorter = shorter.replace(current_hit, current_hit.upper())

        longer = speech_text[start_long:end_long]
        longer = longer.replace(current_hit, f"**{current_hit}**")
        return shorter, longer

    def get_end_index(
        self, word_index: int, word_len: int, diff: int, words_after: int = -1
    ) -> int:
        """Helper for getting some speech text"""
        if words_after == 0:
            return word_index + word_len

        return word_index + word_len + diff if word_index > -1 else diff

    def get_start_index(
        self, word_index: int, diff: int, words_before: int = -1
    ) -> int:
        """Helper for getting some speech text"""
        if words_before == 0:
            return word_index

        return 0 if word_index - diff < 0 else word_index - diff

    def get_anforanden(
        self, from_year: int, to_year: int, selections: dict, di_selected: pd.DataFrame = None
    ) -> pd.DataFrame:
        """For getting a list of - and info about - the full 'Anföranden' (speeches)

        Args:
            from_year int: start year
            to_year int: end year
            selections dict: selected filters, i.e. genders, parties, and, speakers

        Returns:
            DatFrame: DataFrame with speeches for selected years and filter.
        """
        if di_selected is None:
            filtered_corpus = self.filter_corpus(selections, self.corpus)
            di_selected = filtered_corpus.document_index
        di_selected = di_selected[di_selected["year"].between(from_year, to_year)]

        return self.prepare_anforande_display(di_selected)

    def prepare_anforande_display(
        self, anforanden_doc_index: pd.DataFrame
    ) -> pd.DataFrame:
        anforanden_doc_index = anforanden_doc_index[
            ["who", "year", "document_name", "gender_id", "party_id"]
        ]
        adi = anforanden_doc_index.rename(columns={"who": "person_id"})
        self.person_codecs.decode(adi, drop=False)

        # to sort unknowns to the end of the results
        sorted_adi = adi.sort_values(by="name", key=lambda x: x == "")
        return sorted_adi.rename(
            columns={
                "name": "Talare",
                "document_name": "Protokoll",
                "gender": "Kön",
                "party_abbrev": "Parti",
                "year": "År",
            }
        )

    def get_kwic_results_for_search_hits(
        self,
        search_hits: list,
        from_year: int,
        to_year: int,
        selections: dict,
        words_before: int,
        words_after: int,
    ) -> pd.DataFrame:
        """Dummy KWIC data, will be replaced

        Returns:
            DataFrame: dummy KWIC like data
        """
        filtered_corpus = self.filter_corpus(selections, self.corpus)
        # om filtered corpus är tomt, hantera det här
        col_vector_dict = self.get_word_vectors(search_hits, corpus=filtered_corpus)
        if col_vector_dict:
            dfs = []
            for word, vector in col_vector_dict.items():
                current_df = filtered_corpus.document_index[vector.astype(bool)].copy()
                current_df["hit"] = word
                dfs.append(current_df)
            df = pd.concat(dfs)

            self.add_speech_content(words_before, words_after, df)

            return df[df["year"].between(from_year, to_year)]
        return pd.DataFrame()

    def filter_corpus(
        self, filter_dict: dict, corpus: VectorizedCorpus
    ) -> VectorizedCorpus:
        if filter_dict is not None:
            for key in filter_dict:
                corpus = corpus.filter(lambda row: row[key] in filter_dict[key])
        return corpus

    def add_speech_content(
        self, words_before: int, words_after: int, df: pd.DataFrame
    ) -> None:
        df[
            ["Tal", "longer", "Parti", "År", "Protokoll", "Talare", "Kön", "who"]
        ] = df.apply(
            lambda x: self.add_speech(
                x, words_before=words_before, words_after=words_after
            ),
            axis=1,
            result_type="expand",
        )

    def get_property_specs(self) -> list:
        return self.data.property_values_specs

    def get_word_trend_results(
        self,
        search_term: str,
        filter_opts: dict,
        start_year: int,
        end_year: int,
        normalize: bool = False,
    ) -> pd.DataFrame:
        
        if search_term not in self.corpus.vocabulary:
            return pd.DataFrame(), pd.DataFrame() 


        trends_data: SweDebTrendsData = SweDebTrendsData(
            corpus=self.corpus, person_codecs=self.person_codecs, n_top=1000000  # type: ignore
        )
        pivot_keys = list(filter_opts.keys()) if filter_opts else []

        opts: SweDebComputeOpts = SweDebComputeOpts(
            fill_gaps=False,
            keyness=KeynessMetric.TF_normalized if normalize else KeynessMetric.TF,
            normalize=normalize,
            pivot_keys_id_names=pivot_keys,
            filter_opts=PropertyValueMaskingOpts(**filter_opts),
            smooth=False,
            temporal_key="year",
            top_count=10000,
            unstack_tabular=False,
            words=[search_term],
        )

        trends_data.transform(opts)

        filtered_corpus = self.filter_corpus(filter_opts, trends_data.corpus)
        hit_vec = filtered_corpus.get_word_vector(search_term)
        doc_index = filtered_corpus.document_index[hit_vec.astype(bool)]
        anforanden = self.get_anforanden(start_year, end_year, filter_opts, doc_index)

        

        trends: pd.DataFrame = trends_data.extract(
            indices=trends_data.find_word_indices(opts)
        )

        trends = trends[trends["year"].between(start_year, end_year)]
        trends["year"] = trends["year"].astype(str)

        trends.rename(columns={"who": "person_id"}, inplace=True)
        trends_data.person_codecs.decode(trends)

        if not pivot_keys:
            unstacked_trends = trends.set_index(opts.temporal_key)

        else:
            current_pivot_keys = [opts.temporal_key] + [
                x for x in trends.columns if x in self.possible_pivots
            ]
            unstacked_trends = pu.unstack_data(trends, current_pivot_keys)
        self.translate_dataframe(unstacked_trends)
        unstacked_trends = unstacked_trends.loc[:, (unstacked_trends != 0).any(axis=0)]
        return unstacked_trends, anforanden

    def translate_gender_col_header(self, col: str) -> str:
        """Translates gender column names to Swedish

        Args:
            col str: column name, possibly a gender

        Returns:
            str: Swedish translation of column name if a gender, else the original column name
        """
        new_col = col
        if "man" in col and "woman" not in col:
            new_col = col.replace("man", "Män ")
        if "woman" in col:
            new_col = col.replace("woman", "Kvinnor ")
        if "unknown" in col:
            new_col = col.replace("unknown", "Okänt kön")
        return new_col

    def translate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Translates the (gender) columns of a data frame to Swedish

        Args:
            df DataFrame: data frame to translate
        """
        cols = df.columns.tolist()
        translations = {}
        for col in cols:
            translations[col] = self.translate_gender_col_header(col)
        df.rename(columns=translations, inplace=True)

    def get_years_start(self) -> int:
        """Returns the first year in the corpus"""
        return int(self.corpus.document_index["year"].min())

    def get_years_end(self) -> int:
        """Returns the last year in the corpus"""
        return int(self.corpus.document_index["year"].max())


# speech:
# (['speaker_note_id', 'who', 'u_id', 'paragraphs', 'num_tokens', 'num_words', 'page_number', 'page_number2', 'protocol_name', 'date', 'document_id', 'year', 'document_name', 'filename', 'n_tokens', 'n_utterances', 'speech_index', 'gender_id', 'party_id', 'office_type_id', 'sub_office_type_id', 'Adjective', 'Adverb', 'Conjunction', 'Delimiter'
