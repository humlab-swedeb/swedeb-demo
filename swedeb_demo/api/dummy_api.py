from __future__ import annotations
import os

import pandas as pd
import penelope.utility as pu  # type: ignore
from dotenv import load_dotenv
from penelope.common.keyness import KeynessMetric  # type: ignore
from penelope.corpus import VectorizedCorpus  # type: ignore
from penelope.utility import PropertyValueMaskingOpts  # type: ignore
from ccc import Corpus, Corpora


from .parlaclarin.trends_data import SweDebComputeOpts, SweDebTrendsData
from .westac.riksprot.parlaclarin import codecs as md
from .westac.riksprot.parlaclarin import speech_text as sr

from typing import Union, Mapping, Tuple



class ADummyApi:
    """Dummy API for testing and developing the SweDeb GUI"""

    def __init__(self, env_file: str = ".env_sample_docker") -> None:
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
        self.kwic_corpus = self.load_kwic_corpus()
        self.words_per_year = self._set_words_per_year()

    def _set_words_per_year(self) -> pd.DataFrame:
        data_year_series = self.corpus.document_index.groupby("year")[
            "n_raw_tokens"
        ].sum()
        return data_year_series.to_frame().set_index(data_year_series.index.astype(str))

    def get_words_per_year(self):
        return self.words_per_year

    def load_kwic_corpus(self) -> Corpus:
        corpora: Corpora = Corpora(registry_dir="/usr/local/share/cwb/registry/")
        corpus: Corpus = corpora.corpus(corpus_name="RIKSPROT_V090_TEST")
        return corpus

    def load_corpus(self) -> None:
        self.corpus = VectorizedCorpus.load(folder=self.folder, tag=self.tag)

    def get_party_specs(self) -> Union[str, Mapping[str, int]]:
        for specification in self.data.property_values_specs:
            if specification["text_name"] == "party_abbrev":
                return specification["values"]

    def get_word_hits(self, search_term: str, n_hits: int = 5) -> list[str]:
        search_term = search_term.lower()
        return self.corpus.find_matching_words({f"{search_term}"}, n_hits)

    def get_speech(self, document_name: str):  # type: ignore
        return self.repository.speech(speech_name=document_name, mode="dict")

    def get_speech_text(self, document_name: str):  # type: ignore
        return self.repository.to_text(self.get_speech(document_name))

    def get_speaker_note(self, document_name: str) -> str:
        speech = self.get_speech(document_name)
        if "speaker_note_id" not in speech:
            return document_name
        if speech["speaker_note_id"] == "missing":
            return "Talet saknar notering"
        else:
            return speech["speaker_note"]

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

    def filter_corpus(
        self, filter_dict: dict, corpus: VectorizedCorpus
    ) -> VectorizedCorpus:
        if filter_dict is not None:
            for key in filter_dict:
                corpus = corpus.filter(lambda row: row[key] in filter_dict[key])
        return corpus

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

    def get_link(self, person_id, name):
        if name == "":
            "Okänd"
        return f"[{name}](https://www.wikidata.org/wiki/{person_id})"

    def prepare_anforande_display(
        self, anforanden_doc_index: pd.DataFrame
    ) -> pd.DataFrame:
        anforanden_doc_index = anforanden_doc_index[
            ["who", "year", "document_name", "gender_id", "party_id"]
        ]
        adi = anforanden_doc_index.rename(columns={"who": "person_id"})
        self.person_codecs.decode(adi, drop=False)
        adi["link"] = adi.apply(
            lambda x: self.get_link(x["person_id"], x["name"]), axis=1
        )
        adi.drop(columns=["person_id", "gender_id", "party_id"], inplace=True)

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

    def construct_multiword_query(search_terms):
        # [lemma="information"] [lemma="om"]
        query = ""
        for term in search_terms:
            query += f' [lemma="{term}"]'
        return query[1:]

    def get_query_from_selections(self, selections, prefix):
        query = ""
        for key, value in selections.items():
            query += f'&({prefix}.{key}="{value[0]}"'
            for v in value[1:]:
                query += f'|{prefix}.{key}="{v}"'
            query += ")"

        return query[1:]

    def get_query(self, search_terms, selection, prefix):
        term_query = self.get_search_query_list(search_terms)
        if selection:
            query = f"{prefix}:{term_query}::{self.get_query_from_selections(selection, prefix=prefix)}"
            return query
        return term_query

    def get_search_query_list(self, search_terms):
        # [lemma="information"] [lemma="om"]
        query = ""
        for term in search_terms:
            query += f' [lemma="{term}"]'
        return query[1:]

    def rename_selection_keys(self, selections):
        renames = {"gender_id": "speech_gender_id", "party_id": "speech_party_id"}
        for key, value in renames.items():
            if key in selections:
                selections[value] = selections.pop(key)
        return selections

    def get_kwic_results_for_search_hits(
        self,
        search_hits: List[str],
        from_year: int,
        to_year: int,
        selections: dict,
        words_before: int,
        words_after: int,
    ) -> pd.DataFrame:
        selections = self.rename_selection_keys(selections)
        query_str = self.get_query(search_hits, selections, prefix="a")
        subcorpus = self.kwic_corpus.query(
            query_str, context_left=words_before, context_right=words_after
        )

        data: pd.DataFrame = subcorpus.concordance(
            # form='dataframe'
            form="kwic",  # 'simple', 'dataframes',...
            p_show=["word"],  # ['word', 'pos', 'lemma']
            s_show=[
                "speech_who",
                "speech_title",
                "year_title",
                "speech_party_id",
                "speech_gender_id",
            ],
            order="first",
            cut_off=100000,
            matches=None,
            slots=None,
            cwb_ids=False,
        )

        if len(data) == 0:
            return pd.DataFrame()

        renamed_selections = {
            "speech_gender_id": "gender_id",
            "speech_party_id": "party_id",
            "speech_who": "person_id",
        }

        data.reset_index(inplace=True)
        data.rename(columns=renamed_selections, inplace=True)
        data = data.astype({"gender_id": int, "party_id": int, "year_title": int})
        data = data[data["year_title"].between(from_year, to_year)]
        data = data.astype({"year_title": str})
        data = self.person_codecs.decode(data, drop=False)
        data["link"] = data.apply(
            lambda x: self.get_link(x["person_id"], x["name"]), axis=1
        )
        renamed_columns = {
            "left_word": "Kontext Vänster",
            "node_word": "Sökord",
            "right_word": "Kontext Höger",
            "year_title": "År",
            "name": "Talare",
            "party_abbrev": "Parti",
            "speech_title": "Protokoll",
            "gender": "Kön",
        }
        data.rename(columns=renamed_columns, inplace=True)

        return data[
            [
                "Kontext Vänster",
                "Sökord",
                "Kontext Höger",
                "Parti",
                "Talare",
                "År",
                "Kön",
                "Protokoll",
                "person_id",
                "link",
            ]
        ]

    def get_property_specs(self) -> list:
        return self.data.property_values_specs

    def get_word_trend_results(
        self,
        search_terms: List[str],
        filter_opts: dict,
        start_year: int,
        end_year: int,
    ) -> pd.DataFrame:
        search_terms = [x.lower() for x in search_terms if x in self.corpus.vocabulary]

        if not search_terms:
            return pd.DataFrame(), pd.DataFrame()

        trends_data: SweDebTrendsData = SweDebTrendsData(
            corpus=self.corpus, person_codecs=self.person_codecs, n_top=1000000  # type: ignore
        )
        pivot_keys = list(filter_opts.keys()) if filter_opts else []

        opts: SweDebComputeOpts = SweDebComputeOpts(
            fill_gaps=False,
            keyness=KeynessMetric.TF,
            normalize=False,
            pivot_keys_id_names=pivot_keys,
            filter_opts=PropertyValueMaskingOpts(**filter_opts),
            smooth=False,
            temporal_key="year",
            top_count=100000,
            unstack_tabular=False,
            words=search_terms,
        )

        trends_data.transform(opts)

        anforanden = self.get_anforanden_for_word_trends(search_terms, filter_opts)

        trends: pd.DataFrame = trends_data.extract(
            indices=trends_data.find_word_indices(opts)
        )

        trends = trends[trends["year"].between(start_year, end_year)]
        anforanden = anforanden[anforanden["År"].between(start_year, end_year)]
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

    def get_anforanden_for_word_trends(self, search_terms, filter_opts):
        filtered_corpus = self.filter_corpus(filter_opts, self.corpus)
        vectors = self.get_word_vectors(search_terms, filtered_corpus)
        hits = []
        for word, vec in vectors.items():
            hit_di = filtered_corpus.document_index[vec.astype(bool)]
            anforanden = self.prepare_anforande_display(hit_di)
            anforanden["hit"] = word
            hits.append(anforanden)

        all_hits = pd.concat(hits)

        return all_hits

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
