#!/usr/bin/env python3
"""Patch an isolated PGPR runtime copy for Amazon-book KGAT preprocess smoke.

This script is intentionally scoped to the data-loader/preprocess layer. It
does not make a formal Amazon PGPR baseline complete; training, policy
inference, path export, and strict accuracy validation remain separate gates.
"""

from __future__ import annotations

import argparse
from pathlib import Path


AMAZON = "amazon_book_kgat_v1"
BOOK_RELATIONS = [
    "book_author",
    "book_genre",
    "book_original_language",
    "book_subject",
    "book_next_in_series",
    "book_previous_in_series",
    "book_part_of_series",
    "book_character",
    "book_interior_illustration",
]


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not find expected block in {path}: {old[:80]!r}")
    return text.replace(old, new, 1)


def write_if_changed(path: Path, text: str, changed: list[str]) -> None:
    original = path.read_text()
    if text != original:
        path.write_text(text)
        changed.append(str(path))


def patch_utils(pgpr_root: Path) -> list[str]:
    path = pgpr_root / "utils.py"
    text = path.read_text()
    changed: list[str] = []

    text = replace_once(
        text,
        "LASTFM = 'lastfm'\n",
        "LASTFM = 'lastfm'\nAMAZON_BOOK_KGAT = 'amazon_book_kgat_v1'\n",
        path,
    )
    text = replace_once(
        text,
        "DATASET_DIR = {\n    ML1M: '../../datasets/ml1m',\n    LASTFM: '../../datasets/lastfm'\n}\n",
        (
            "DATASET_DIR = {\n"
            "    ML1M: '../../datasets/ml1m',\n"
            "    LASTFM: '../../datasets/lastfm',\n"
            "    AMAZON_BOOK_KGAT: '../../datasets/amazon_book_kgat_v1'\n"
            "}\n"
        ),
        path,
    )
    text = replace_once(
        text,
        "TMP_DIR = {\n    ML1M: 'tmp/ml1m',\n    LASTFM: 'tmp/lastfm'\n}\n",
        (
            "TMP_DIR = {\n"
            "    ML1M: 'tmp/ml1m',\n"
            "    LASTFM: 'tmp/lastfm',\n"
            "    AMAZON_BOOK_KGAT: 'tmp/amazon_book_kgat_v1'\n"
            "}\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "LABELS = {\n"
            "    ML1M: (TMP_DIR[ML1M] + '/train_label.pkl', TMP_DIR[ML1M] + '/test_label.pkl'),\n"
            "    LASTFM: (TMP_DIR[LASTFM] + '/train_label.pkl', TMP_DIR[LASTFM] + '/test_label.pkl'),\n"
            "\n"
            "}\n"
        ),
        (
            "LABELS = {\n"
            "    ML1M: (TMP_DIR[ML1M] + '/train_label.pkl', TMP_DIR[ML1M] + '/test_label.pkl'),\n"
            "    LASTFM: (TMP_DIR[LASTFM] + '/train_label.pkl', TMP_DIR[LASTFM] + '/test_label.pkl'),\n"
            "    AMAZON_BOOK_KGAT: (TMP_DIR[AMAZON_BOOK_KGAT] + '/train_label.pkl', TMP_DIR[AMAZON_BOOK_KGAT] + '/test_label.pkl'),\n"
            "\n"
            "}\n"
        ),
        path,
    )
    text = replace_once(
        text,
        "#SHARED ENTITIES\nUSER = 'user'\nCATEGORY = 'category'\n",
        (
            "#AMAZON BOOK ENTITIES\n"
            "BOOK = 'book'\n"
            "ENTITY = 'entity'\n"
            "#SHARED ENTITIES\n"
            "USER = 'user'\n"
            "CATEGORY = 'category'\n"
        ),
        path,
    )
    text = replace_once(
        text,
        "SELF_LOOP = 'self_loop'\n",
        (
            "PURCHASED = 'purchased'\n"
            "BOOK_AUTHOR = 'book_author'\n"
            "BOOK_GENRE = 'book_genre'\n"
            "BOOK_ORIGINAL_LANGUAGE = 'book_original_language'\n"
            "BOOK_SUBJECT = 'book_subject'\n"
            "BOOK_NEXT_IN_SERIES = 'book_next_in_series'\n"
            "BOOK_PREVIOUS_IN_SERIES = 'book_previous_in_series'\n"
            "BOOK_PART_OF_SERIES = 'book_part_of_series'\n"
            "BOOK_CHARACTER = 'book_character'\n"
            "BOOK_INTERIOR_ILLUSTRATION = 'book_interior_illustration'\n"
            "SELF_LOOP = 'self_loop'\n"
        ),
        path,
    )
    text = replace_once(
        text,
        "ML1M_TAIL_ENTITY_NAME = {0: CINEMATOGRAPHER, 1: PRODUCTION_COMPANY, 2: COMPOSER, 3: CATEGORY, 8: CATEGORY, 10: ACTOR, 14: EDITOR, 15: PRODUCER, 16: WRITTER, 18: DIRECTOR}\n",
        (
            "AMAZON_BOOK_RELATIONS = [\n"
            "    BOOK_AUTHOR,\n"
            "    BOOK_GENRE,\n"
            "    BOOK_ORIGINAL_LANGUAGE,\n"
            "    BOOK_SUBJECT,\n"
            "    BOOK_NEXT_IN_SERIES,\n"
            "    BOOK_PREVIOUS_IN_SERIES,\n"
            "    BOOK_PART_OF_SERIES,\n"
            "    BOOK_CHARACTER,\n"
            "    BOOK_INTERIOR_ILLUSTRATION,\n"
            "]\n"
            "AMAZON_BOOK_KG_RELATION = {\n"
            "    USER: {PURCHASED: BOOK},\n"
            "    BOOK: dict([(PURCHASED, USER)] + [(relation, ENTITY) for relation in AMAZON_BOOK_RELATIONS]),\n"
            "    ENTITY: {relation: BOOK for relation in AMAZON_BOOK_RELATIONS},\n"
            "}\n"
            "AMAZON_BOOK_PATH_PATTERN = {\n"
            "    10: ((None, USER), (PURCHASED, BOOK), (BOOK_AUTHOR, ENTITY), (BOOK_AUTHOR, BOOK)),\n"
            "    13: ((None, USER), (PURCHASED, BOOK), (BOOK_GENRE, ENTITY), (BOOK_GENRE, BOOK)),\n"
            "    11: ((None, USER), (PURCHASED, BOOK), (BOOK_ORIGINAL_LANGUAGE, ENTITY), (BOOK_ORIGINAL_LANGUAGE, BOOK)),\n"
            "    5: ((None, USER), (PURCHASED, BOOK), (BOOK_SUBJECT, ENTITY), (BOOK_SUBJECT, BOOK)),\n"
            "    20: ((None, USER), (PURCHASED, BOOK), (BOOK_NEXT_IN_SERIES, ENTITY), (BOOK_NEXT_IN_SERIES, BOOK)),\n"
            "    15: ((None, USER), (PURCHASED, BOOK), (BOOK_PREVIOUS_IN_SERIES, ENTITY), (BOOK_PREVIOUS_IN_SERIES, BOOK)),\n"
            "    18: ((None, USER), (PURCHASED, BOOK), (BOOK_PART_OF_SERIES, ENTITY), (BOOK_PART_OF_SERIES, BOOK)),\n"
            "    19: ((None, USER), (PURCHASED, BOOK), (BOOK_CHARACTER, ENTITY), (BOOK_CHARACTER, BOOK)),\n"
            "    36: ((None, USER), (PURCHASED, BOOK), (BOOK_INTERIOR_ILLUSTRATION, ENTITY), (BOOK_INTERIOR_ILLUSTRATION, BOOK)),\n"
            "}\n"
            "ML1M_TAIL_ENTITY_NAME = {0: CINEMATOGRAPHER, 1: PRODUCTION_COMPANY, 2: COMPOSER, 3: CATEGORY, 8: CATEGORY, 10: ACTOR, 14: EDITOR, 15: PRODUCER, 16: WRITTER, 18: DIRECTOR}\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "def get_entities(dataset_name):\n"
            "    return list(ML1M_KG_RELATION.keys()) if dataset_name == \"ml1m\" else list(LASTFM_KG_RELATION.keys())\n\n"
        ),
        (
            "def get_kg_relation(dataset_name):\n"
            "    if dataset_name == ML1M:\n"
            "        return ML1M_KG_RELATION\n"
            "    if dataset_name == LASTFM:\n"
            "        return LASTFM_KG_RELATION\n"
            "    if dataset_name == AMAZON_BOOK_KGAT:\n"
            "        return AMAZON_BOOK_KG_RELATION\n"
            "    raise ValueError('unsupported PGPR dataset: {}'.format(dataset_name))\n\n"
            "def get_entities(dataset_name):\n"
            "    return list(get_kg_relation(dataset_name).keys())\n\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "def get_entities_without_user(dataset_name):\n"
            "    ans = list(ML1M_KG_RELATION.keys()) if dataset_name == ML1M else list(LASTFM_KG_RELATION.keys())\n"
            "    ans.remove('user')\n"
            "    return ans\n\n"
        ),
        (
            "def get_entities_without_user(dataset_name):\n"
            "    ans = list(get_kg_relation(dataset_name).keys())\n"
            "    ans.remove(USER)\n"
            "    return ans\n\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "def get_song_relationships():\n"
            "    ans = list(LASTFM_KG_RELATION[SONG].keys())\n"
            "    ans.remove(LISTENED)\n"
            "    return ans\n\n"
        ),
        (
            "def get_song_relationships():\n"
            "    ans = list(LASTFM_KG_RELATION[SONG].keys())\n"
            "    ans.remove(LISTENED)\n"
            "    return ans\n\n"
            "def get_book_relationships():\n"
            "    return list(AMAZON_BOOK_RELATIONS)\n\n"
            "def get_product_entity(dataset_name):\n"
            "    if dataset_name == ML1M:\n"
            "        return MOVIE\n"
            "    if dataset_name == LASTFM:\n"
            "        return SONG\n"
            "    if dataset_name == AMAZON_BOOK_KGAT:\n"
            "        return BOOK\n"
            "    raise ValueError('unsupported PGPR dataset: {}'.format(dataset_name))\n\n"
            "def get_interaction_relation(dataset_name):\n"
            "    if dataset_name == ML1M:\n"
            "        return WATCHED\n"
            "    if dataset_name == LASTFM:\n"
            "        return LISTENED\n"
            "    if dataset_name == AMAZON_BOOK_KGAT:\n"
            "        return PURCHASED\n"
            "    raise ValueError('unsupported PGPR dataset: {}'.format(dataset_name))\n\n"
            "def get_product_relationships(dataset_name):\n"
            "    if dataset_name == ML1M:\n"
            "        return get_movie_relationships()\n"
            "    if dataset_name == LASTFM:\n"
            "        return get_song_relationships()\n"
            "    if dataset_name == AMAZON_BOOK_KGAT:\n"
            "        return get_book_relationships()\n"
            "    raise ValueError('unsupported PGPR dataset: {}'.format(dataset_name))\n\n"
            "def get_relations_for_entity(dataset_name, entity_head):\n"
            "    return list(get_kg_relation(dataset_name)[entity_head].keys())\n\n"
            "def get_path_patterns(dataset_name):\n"
            "    if dataset_name == ML1M:\n"
            "        return ML1M_PATH_PATTERN\n"
            "    if dataset_name == LASTFM:\n"
            "        return LASTFM_PATH_PATTERN\n"
            "    if dataset_name == AMAZON_BOOK_KGAT:\n"
            "        return AMAZON_BOOK_PATH_PATTERN\n"
            "    raise ValueError('unsupported PGPR dataset: {}'.format(dataset_name))\n\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "def get_entity_tail(dataset_name, entity_head, relation):\n"
            "    return ML1M_KG_RELATION[entity_head][relation] if dataset_name == \"ml1m\" else LASTFM_KG_RELATION[entity_head][relation]\n\n"
        ),
        (
            "def get_entity_tail(dataset_name, entity_head, relation):\n"
            "    return get_kg_relation(dataset_name)[entity_head][relation]\n\n"
        ),
        path,
    )
    write_if_changed(path, text, changed)
    return changed


def patch_data_utils(pgpr_root: Path) -> list[str]:
    path = pgpr_root / "data_utils.py"
    text = path.read_text()
    changed: list[str] = []

    text = replace_once(
        text,
        (
            "from utils import get_movie_relationships, DATASET_DIR, \\\n"
            "    get_product_id_kgid_mapping, get_song_relationships, get_uid_to_kgid_mapping\n"
        ),
        (
            "from utils import get_movie_relationships, DATASET_DIR, \\\n"
            "    get_product_id_kgid_mapping, get_song_relationships, get_uid_to_kgid_mapping, \\\n"
            "    get_book_relationships, get_product_entity, get_product_relationships\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            entity_files = edict(\n"
            "                user='entities/user.txt.gz',\n"
            "                song='entities/song.txt.gz',\n"
            "                artist='entities/artist.txt.gz',\n"
            "                engineer='entities/engineer.txt.gz',\n"
            "                producer='entities/producer.txt.gz',\n"
            "                category='entities/category.txt.gz',\n"
            "                related_song='entities/related_song.txt.gz',\n"
            "            )\n"
        ),
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            entity_files = edict(\n"
            "                user='entities/user.txt.gz',\n"
            "                song='entities/song.txt.gz',\n"
            "                artist='entities/artist.txt.gz',\n"
            "                engineer='entities/engineer.txt.gz',\n"
            "                producer='entities/producer.txt.gz',\n"
            "                category='entities/category.txt.gz',\n"
            "                related_song='entities/related_song.txt.gz',\n"
            "            )\n"
            "        elif self.dataset_name == \"amazon_book_kgat_v1\":\n"
            "            entity_files = edict(\n"
            "                user='entities/user.txt.gz',\n"
            "                book='entities/book.txt.gz',\n"
            "                entity='entities/entity.txt.gz',\n"
            "            )\n"
            "        else:\n"
            "            raise ValueError('unsupported PGPR dataset: {}'.format(self.dataset_name))\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        product_distrib = np.zeros(self.movie.vocab_size) if self.dataset_name == \"ml1m\" else np.zeros(self.song.vocab_size)\n"
        ),
        (
            "        product_entity = get_product_entity(self.dataset_name)\n"
            "        product_distrib = np.zeros(getattr(self, product_entity).vocab_size)\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "                product_uniform_distrib=np.ones(self.movie.vocab_size if self.dataset_name == \"ml1m\" else self.song.vocab_size),\n"
        ),
        (
            "                product_uniform_distrib=np.ones(getattr(self, product_entity).vocab_size),\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            dataset_dir = DATASET_DIR[self.dataset_name]\n"
            "            product_relations = edict(\n"
            "                mixed_by=(\"/relations/mixed_by_s_e.txt.gz\", self.engineer),\n"
            "                featured_by=(\"/relations/featured_by_s_a.txt.gz\",self.artist),\n"
            "                sang_by=('/relations/sang_by_s_a.txt.gz', self.artist),\n"
            "                related_to=('/relations/related_to_s_rs.txt.gz', self.related_song),\n"
            "                alternative_version_of=(\"relations/alternative_version_of_s_rs.txt.gz\", self.related_song),\n"
            "                original_version_of=(\"relations/orginal_version_of_s_rs.txt.gz\", self.related_song),\n"
            "                belong_to=('relations/belong_to_s_ca.txt.gz', self.category),\n"
            "                produced_by_producer=('relations/produced_by_producer_s_pr.txt.gz', self.producer),\n"
            "            )\n"
        ),
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            dataset_dir = DATASET_DIR[self.dataset_name]\n"
            "            product_relations = edict(\n"
            "                mixed_by=(\"/relations/mixed_by_s_e.txt.gz\", self.engineer),\n"
            "                featured_by=(\"/relations/featured_by_s_a.txt.gz\",self.artist),\n"
            "                sang_by=('/relations/sang_by_s_a.txt.gz', self.artist),\n"
            "                related_to=('/relations/related_to_s_rs.txt.gz', self.related_song),\n"
            "                alternative_version_of=(\"relations/alternative_version_of_s_rs.txt.gz\", self.related_song),\n"
            "                original_version_of=(\"relations/orginal_version_of_s_rs.txt.gz\", self.related_song),\n"
            "                belong_to=('relations/belong_to_s_ca.txt.gz', self.category),\n"
            "                produced_by_producer=('relations/produced_by_producer_s_pr.txt.gz', self.producer),\n"
            "            )\n"
            "        elif self.dataset_name == \"amazon_book_kgat_v1\":\n"
            "            dataset_dir = DATASET_DIR[self.dataset_name]\n"
            "            product_relations = edict(\n"
            "                book_author=('relations/book_author_b_e.txt.gz', self.entity),\n"
            "                book_genre=('relations/book_genre_b_e.txt.gz', self.entity),\n"
            "                book_original_language=('relations/book_original_language_b_e.txt.gz', self.entity),\n"
            "                book_subject=('relations/book_subject_b_e.txt.gz', self.entity),\n"
            "                book_next_in_series=('relations/book_next_in_series_b_e.txt.gz', self.entity),\n"
            "                book_previous_in_series=('relations/book_previous_in_series_b_e.txt.gz', self.entity),\n"
            "                book_part_of_series=('relations/book_part_of_series_b_e.txt.gz', self.entity),\n"
            "                book_character=('relations/book_character_b_e.txt.gz', self.entity),\n"
            "                book_interior_illustration=('relations/book_interior_illustration_b_e.txt.gz', self.entity),\n"
            "            )\n"
            "        else:\n"
            "            raise ValueError('unsupported PGPR dataset: {}'.format(self.dataset_name))\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        self.product_relations = get_movie_relationships() if dataset.dataset_name == \"ml1m\" else get_song_relationships()\n"
        ),
        "        self.product_relations = get_product_relationships(dataset.dataset_name)\n",
        path,
    )
    write_if_changed(path, text, changed)
    return changed


def patch_knowledge_graph(pgpr_root: Path) -> list[str]:
    path = pgpr_root / "knowledge_graph.py"
    text = path.read_text()
    changed: list[str] = []
    text = replace_once(
        text,
        (
            "                relations = get_movie_relations(entity) if dataset.dataset_name == \"ml1m\" else get_song_relations(entity)\n"
        ),
        "                relations = get_relations_for_entity(dataset.dataset_name, entity)\n",
        path,
    )
    text = replace_once(
        text,
        (
            "            if dataset.dataset_name == \"ml1m\":\n"
            "                self._add_edge(USER, uid, WATCHED, MOVIE, pid)\n"
            "            elif dataset.dataset_name == \"lastfm\":\n"
            "                self._add_edge(USER, uid, LISTENED, SONG, pid)\n"
        ),
        (
            "            main_product = get_product_entity(dataset.dataset_name)\n"
            "            interaction = get_interaction_relation(dataset.dataset_name)\n"
            "            self._add_edge(USER, uid, interaction, main_product, pid)\n"
        ),
        path,
    )
    text = replace_once(
        text,
        "        relationships = get_movie_relationships() if dataset.dataset_name == \"ml1m\" else get_song_relationships()\n",
        "        relationships = get_product_relationships(dataset.dataset_name)\n",
        path,
    )
    text = replace_once(
        text,
        (
            "                    if dataset.dataset_name == \"ml1m\":\n"
            "                        et_type = get_entity_tail(dataset.dataset_name, MOVIE, relation)\n"
            "                        self._add_edge(MOVIE, pid, relation, et_type, eid)\n"
            "                    elif dataset.dataset_name == \"lastfm\":\n"
            "                        et_type = get_entity_tail(dataset.dataset_name, SONG, relation)\n"
            "                        self._add_edge(SONG, pid, relation, et_type, eid)\n"
        ),
        (
            "                    main_product = get_product_entity(dataset.dataset_name)\n"
            "                    et_type = get_entity_tail(dataset.dataset_name, main_product, relation)\n"
            "                    self._add_edge(main_product, pid, relation, et_type, eid)\n"
        ),
        path,
    )
    write_if_changed(path, text, changed)
    return changed


def patch_transe_model(pgpr_root: Path) -> list[str]:
    path = pgpr_root / "transe_model.py"
    text = path.read_text()
    changed: list[str] = []

    text = replace_once(
        text,
        "        distrib = np.power(np.array(distrib, dtype=np.float), 0.75)\n",
        "        distrib = np.power(np.array(distrib, dtype=float), 0.75)\n",
        path,
    )
    text = replace_once(
        text,
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            self.entities = edict(\n"
            "                user=edict(vocab_size=dataset.user.vocab_size),\n"
            "                song=edict(vocab_size=dataset.song.vocab_size),\n"
            "                artist=edict(vocab_size=dataset.artist.vocab_size),\n"
            "                engineer=edict(vocab_size=dataset.engineer.vocab_size),\n"
            "                related_song=edict(vocab_size=dataset.related_song.vocab_size),\n"
            "                producer=edict(vocab_size=dataset.producer.vocab_size),\n"
            "                category=edict(vocab_size=dataset.category.vocab_size),\n"
            "            )\n"
        ),
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            self.entities = edict(\n"
            "                user=edict(vocab_size=dataset.user.vocab_size),\n"
            "                song=edict(vocab_size=dataset.song.vocab_size),\n"
            "                artist=edict(vocab_size=dataset.artist.vocab_size),\n"
            "                engineer=edict(vocab_size=dataset.engineer.vocab_size),\n"
            "                related_song=edict(vocab_size=dataset.related_song.vocab_size),\n"
            "                producer=edict(vocab_size=dataset.producer.vocab_size),\n"
            "                category=edict(vocab_size=dataset.category.vocab_size),\n"
            "            )\n"
            "        elif self.dataset_name == \"amazon_book_kgat_v1\":\n"
            "            self.entities = edict(\n"
            "                user=edict(vocab_size=dataset.user.vocab_size),\n"
            "                book=edict(vocab_size=dataset.book.vocab_size),\n"
            "                entity=edict(vocab_size=dataset.entity.vocab_size),\n"
            "            )\n"
            "        else:\n"
            "            raise ValueError('unsupported PGPR dataset: {}'.format(self.dataset_name))\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            self.relations = edict(\n"
            "                listened=edict(\n"
            "                    et='song',\n"
            "                    et_distrib=self._make_distrib(dataset.review.product_uniform_distrib)),\n"
            "                sang_by=edict(\n"
            "                    et='artist',\n"
            "                    et_distrib=self._make_distrib(dataset.sang_by.et_distrib)),\n"
            "                produced_by_producer=edict(\n"
            "                    et='producer',\n"
            "                    et_distrib=self._make_distrib(dataset.produced_by_producer.et_distrib)),\n"
            "                belong_to=edict(\n"
            "                    et='category',\n"
            "                    et_distrib=self._make_distrib(dataset.belong_to.et_distrib)),\n"
            "                featured_by=edict(\n"
            "                    et='artist',\n"
            "                    et_distrib=self._make_distrib(dataset.featured_by.et_distrib)),\n"
            "                mixed_by=edict(\n"
            "                    et='engineer',\n"
            "                    et_distrib=self._make_distrib(dataset.mixed_by.et_distrib)),\n"
            "                related_to=edict(\n"
            "                    et='related_song',\n"
            "                    et_distrib=self._make_distrib(dataset.related_to.et_distrib)),\n"
            "                alternative_version_of=edict(\n"
            "                    et='related_song',\n"
            "                    et_distrib=self._make_distrib(dataset.alternative_version_of.et_distrib)),\n"
            "                original_version_of=edict(\n"
            "                    et='related_song',\n"
            "                    et_distrib=self._make_distrib(dataset.original_version_of.et_distrib)),\n"
            "            )\n"
        ),
        (
            "        elif self.dataset_name == \"lastfm\":\n"
            "            self.relations = edict(\n"
            "                listened=edict(\n"
            "                    et='song',\n"
            "                    et_distrib=self._make_distrib(dataset.review.product_uniform_distrib)),\n"
            "                sang_by=edict(\n"
            "                    et='artist',\n"
            "                    et_distrib=self._make_distrib(dataset.sang_by.et_distrib)),\n"
            "                produced_by_producer=edict(\n"
            "                    et='producer',\n"
            "                    et_distrib=self._make_distrib(dataset.produced_by_producer.et_distrib)),\n"
            "                belong_to=edict(\n"
            "                    et='category',\n"
            "                    et_distrib=self._make_distrib(dataset.belong_to.et_distrib)),\n"
            "                featured_by=edict(\n"
            "                    et='artist',\n"
            "                    et_distrib=self._make_distrib(dataset.featured_by.et_distrib)),\n"
            "                mixed_by=edict(\n"
            "                    et='engineer',\n"
            "                    et_distrib=self._make_distrib(dataset.mixed_by.et_distrib)),\n"
            "                related_to=edict(\n"
            "                    et='related_song',\n"
            "                    et_distrib=self._make_distrib(dataset.related_to.et_distrib)),\n"
            "                alternative_version_of=edict(\n"
            "                    et='related_song',\n"
            "                    et_distrib=self._make_distrib(dataset.alternative_version_of.et_distrib)),\n"
            "                original_version_of=edict(\n"
            "                    et='related_song',\n"
            "                    et_distrib=self._make_distrib(dataset.original_version_of.et_distrib)),\n"
            "            )\n"
            "        elif self.dataset_name == \"amazon_book_kgat_v1\":\n"
            "            self.relations = edict(\n"
            "                purchased=edict(\n"
            "                    et='book',\n"
            "                    et_distrib=self._make_distrib(dataset.review.product_uniform_distrib)),\n"
            "            )\n"
            "            for relation_name in get_book_relationships():\n"
            "                self.relations[relation_name] = edict(\n"
            "                    et='entity',\n"
            "                    et_distrib=self._make_distrib(getattr(dataset, relation_name).et_distrib),\n"
            "                )\n"
            "        else:\n"
            "            raise ValueError('unsupported PGPR dataset: {}'.format(self.dataset_name))\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "\n\n        # l2 regularization\n"
            "        if self.l2_lambda > 0:\n"
        ),
        (
            "\n"
            "        elif self.dataset_name == \"amazon_book_kgat_v1\":\n"
            "            user_idxs = batch_idxs[:, 0]\n"
            "            book_idxs = batch_idxs[:, 1]\n"
            "            ub_loss, ub_embeds = self.neg_loss('user', 'purchased', 'book', user_idxs, book_idxs)\n"
            "            regularizations.extend(ub_embeds)\n"
            "            loss = ub_loss\n"
            "            for relation_offset, relation_name in enumerate(get_book_relationships(), start=2):\n"
            "                entity_idxs = batch_idxs[:, relation_offset]\n"
            "                rel_loss, rel_embeds = self.neg_loss('book', relation_name, 'entity', book_idxs, entity_idxs)\n"
            "                if rel_loss is not None:\n"
            "                    regularizations.extend(rel_embeds)\n"
            "                    loss += rel_loss\n"
            "\n"
            "\n"
            "        # l2 regularization\n"
            "        if self.l2_lambda > 0:\n"
        ),
        path,
    )
    write_if_changed(path, text, changed)
    return changed


def patch_train_transe_model(pgpr_root: Path) -> list[str]:
    path = pgpr_root / "train_transe_model.py"
    text = path.read_text()
    changed: list[str] = []
    text = replace_once(
        text,
        "    save_embed(args.dataset, embeds)\n",
        (
            "    elif args.dataset == \"amazon_book_kgat_v1\":\n"
            "        embeds = {\n"
            "            USER: state_dict['user.weight'].cpu().data.numpy()[:-1],\n"
            "            BOOK: state_dict['book.weight'].cpu().data.numpy()[:-1],\n"
            "            ENTITY: state_dict['entity.weight'].cpu().data.numpy()[:-1],\n"
            "            PURCHASED: (\n"
            "                state_dict['purchased'].cpu().data.numpy()[0],\n"
            "                state_dict['purchased_bias.weight'].cpu().data.numpy()\n"
            "            ),\n"
            "        }\n"
            "        for relation_name in get_book_relationships():\n"
            "            embeds[relation_name] = (\n"
            "                state_dict[relation_name].cpu().data.numpy()[0],\n"
            "                state_dict[relation_name + '_bias.weight'].cpu().data.numpy(),\n"
            "            )\n"
            "    save_embed(args.dataset, embeds)\n"
        ),
        path,
    )
    write_if_changed(path, text, changed)
    return changed


def patch_kg_env(pgpr_root: Path) -> list[str]:
    path = pgpr_root / "kg_env.py"
    text = path.read_text()
    changed: list[str] = []

    text = replace_once(
        text,
        (
            "        # Compute the per-user maximum without materializing the\n"
            "        # complete user-product score matrix.\n"
            "        if dataset_str == \"ml1m\":\n"
            "            user_queries = self.embeds[USER] + self.embeds[WATCHED][0]\n"
            "            product_embeds = self.embeds[MOVIE]\n"
            "        elif dataset_str == \"lastfm\":\n"
            "            user_queries = self.embeds[USER] + self.embeds[LISTENED][0]\n"
            "            product_embeds = self.embeds[SONG]\n"
            "        self.u_p_scales = np.empty(len(user_queries), dtype=np.float32)\n"
        ),
        (
            "        self.main_product = get_product_entity(dataset_str)\n"
            "        self.review_interaction = get_interaction_relation(dataset_str)\n"
            "        self.KG_RELATION = get_kg_relation(dataset_str)\n"
            "        # Compute the per-user maximum without materializing the\n"
            "        # complete user-product score matrix.\n"
            "        user_queries = self.embeds[USER] + self.embeds[self.review_interaction][0]\n"
            "        product_embeds = self.embeds[self.main_product]\n"
            "        self.u_p_scales = np.empty(len(user_queries), dtype=np.float32)\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        # Compute path patterns\n"
            "        self.patterns = []\n"
            "\n"
            "        # Changing according to the dataset\n"
            "        if self.dataset_name == \"ml1m\":\n"
            "            valid_patterns = list(ML1M_PATH_PATTERN.keys())\n"
            "            PATH_PATTERN = ML1M_PATH_PATTERN\n"
            "        elif self.dataset_name == \"lastfm\":\n"
            "            valid_patterns = list(LASTFM_PATH_PATTERN.keys())\n"
            "            PATH_PATTERN = LASTFM_PATH_PATTERN\n"
            "\n"
            "        valid_patterns = list(ML1M_PATH_PATTERN.keys()) if self.dataset_name == \"ml1m\" else list(LASTFM_PATH_PATTERN.keys())\n"
            "        PATH_PATTERN = ML1M_PATH_PATTERN if self.dataset_name == \"ml1m\" else LASTFM_PATH_PATTERN\n"
        ),
        (
            "        # Compute path patterns\n"
            "        self.patterns = []\n"
            "        PATH_PATTERN = get_path_patterns(self.dataset_name)\n"
            "        valid_patterns = list(PATH_PATTERN.keys())\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        # Changing according to the dataset\n"
            "        if self.dataset_name == \"ml1m\":\n"
            "            KG_RELATION = ML1M_KG_RELATION\n"
            "            main_product = MOVIE\n"
            "            review_interaction = WATCHED\n"
            "        elif self.dataset_name == \"lastfm\":\n"
            "            KG_RELATION = LASTFM_KG_RELATION\n"
            "            main_product = SONG\n"
            "            review_interaction = LISTENED\n"
            "\n"
        ),
        (
            "        KG_RELATION = self.KG_RELATION\n"
            "        main_product = self.main_product\n"
            "        review_interaction = self.review_interaction\n"
            "\n"
        ),
        path,
    )
    text = replace_once(
        text,
        (
            "        if self.dataset_name == \"ml1m\":\n"
            "            if curr_node_type == MOVIE:\n"
            "                # Give soft reward for other reached products.\n"
            "                uid = path[0][-1]\n"
            "                u_vec = self.embeds[USER][uid] + self.embeds[WATCHED][0]\n"
            "                p_vec = self.embeds[MOVIE][curr_node_id]\n"
            "                score = np.dot(u_vec, p_vec) / self.u_p_scales[uid]\n"
            "                target_score = max(score, 0.0)\n"
            "        else:\n"
            "            if curr_node_type == SONG:\n"
            "                # Give soft reward for other reached products.\n"
            "                uid = path[0][-1]\n"
            "                u_vec = self.embeds[USER][uid] + self.embeds[LISTENED][0]\n"
            "                p_vec = self.embeds[SONG][curr_node_id]\n"
            "                score = np.dot(u_vec, p_vec) / self.u_p_scales[uid]\n"
            "                target_score = max(score, 0.0)\n"
        ),
        (
            "        if curr_node_type == self.main_product:\n"
            "            # Give soft reward for other reached products.\n"
            "            uid = path[0][-1]\n"
            "            u_vec = self.embeds[USER][uid] + self.embeds[self.review_interaction][0]\n"
            "            p_vec = self.embeds[self.main_product][curr_node_id]\n"
            "            scale = self.u_p_scales[uid]\n"
            "            if scale != 0:\n"
            "                score = np.dot(u_vec, p_vec) / scale\n"
            "                target_score = max(score, 0.0)\n"
        ),
        path,
    )
    old_batch_relation = (
        "        # Changing according to the dataset\n"
        "        KG_RELATION = ML1M_KG_RELATION if self.dataset_name == \"ml1m\" else LASTFM_KG_RELATION\n"
        "\n"
        "        # Execute batch actions.\n"
    )
    new_batch_relation = (
        "        KG_RELATION = self.KG_RELATION\n"
        "\n"
        "        # Execute batch actions.\n"
    )
    if old_batch_relation in text:
        text = text.replace(old_batch_relation, new_batch_relation, 1)
    elif new_batch_relation not in text:
        raise RuntimeError(f"Could not patch batch_step KG_RELATION in {path}")
    write_if_changed(path, text, changed)
    return changed


def patch_test_agent(pgpr_root: Path) -> list[str]:
    path = pgpr_root / "test_agent.py"
    text = path.read_text()
    changed: list[str] = []
    text = replace_once(
        text,
        (
            "    # Changing according to the dataset\n"
            "    KG_RELATION = ML1M_KG_RELATION if env.dataset_name == \"ml1m\" else LASTFM_KG_RELATION\n"
        ),
        "    KG_RELATION = get_kg_relation(env.dataset_name)\n",
        path,
    )
    text = replace_once(
        text,
        (
            "    product = MOVIE if dataset_name == \"ml1m\" else SONG\n"
            "    user_embeds = embeds[USER]\n"
            "    watched_embeds = embeds[WATCHED][0] if dataset_name == \"ml1m\" else embeds[LISTENED][0]\n"
            "    movie_embeds = embeds[MOVIE] if dataset_name == \"ml1m\" else embeds[SONG]\n"
        ),
        (
            "    product = get_product_entity(dataset_name)\n"
            "    user_embeds = embeds[USER]\n"
            "    watched_embeds = embeds[get_interaction_relation(dataset_name)][0]\n"
            "    movie_embeds = embeds[product]\n"
        ),
        path,
    )
    write_if_changed(path, text, changed)
    return changed


def patch_runtime(runtime_root: Path) -> list[str]:
    pgpr_root = runtime_root / "models" / "PGPR"
    if not pgpr_root.exists():
        raise FileNotFoundError(pgpr_root)
    changed: list[str] = []
    changed.extend(patch_utils(pgpr_root))
    changed.extend(patch_data_utils(pgpr_root))
    changed.extend(patch_knowledge_graph(pgpr_root))
    changed.extend(patch_transe_model(pgpr_root))
    changed.extend(patch_train_transe_model(pgpr_root))
    changed.extend(patch_kg_env(pgpr_root))
    changed.extend(patch_test_agent(pgpr_root))
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    args = parser.parse_args()
    changed = patch_runtime(Path(args.runtime_root))
    if changed:
        print("patched_amazon_pgpr:")
        for item in changed:
            print(f"  {item}")
    else:
        print("already_patched_amazon_pgpr")


if __name__ == "__main__":
    main()
