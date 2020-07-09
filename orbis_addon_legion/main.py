# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from pprint import pprint
from copy import deepcopy
import collections

from conditions import conditions

import logging
logger = logging.getLogger(__name__)


class Main(object):
    """docstring for Main"""

    def __init__(self):
        super(Main, self).__init__()
        self.rucksack_location = '/home/fabian/orbis-eval/logs/'
        self.corpora_location = '/home/fabian/orbis-eval/data/corpora/'
        self.corpora_names = self.get_corpora_names()
        self.computer_names = self.get_computer_names()
        self.gold_files = self.get_gold_files()
        self.gold_entities = {}
        self.get_gold_entities()
        self.computer_files = {}
        self.get_computer_files()
        self.computed_entities = {}
        self.get_computed_entities()
        self.endorsement = {}
        self.endorsement_condition = "overlap"
        self.get_endorsement()
        self.evaluation = collections.defaultdict(lambda: collections.defaultdict(dict))
        self.evaluation = {}
        self.get_evaluation()

    def run(self):
        # print(self.corpora_names)
        # print(self.computer_names)
        # print(self.gold_files)
        # print(self.computer_files)
        # self.test()
        pass

    def get_corpora_names(self):
        return list(set([
            folder.name
            for folder
            in Path(self.corpora_location).glob("*")
            if folder.is_dir()
        ]))

    def get_computer_names(self):
        return list(set([
            folder.name
            for folder
            in Path(self.corpora_location).glob("*/computed/*")
            if folder.is_dir()
        ]))

    def load_evaluations(self):
        pass

    def get_gold_files(self):
        return list([
            folder
            for folder
            in Path(self.corpora_location).glob("*/gold/*")
            if folder.is_file()
        ])

    def get_gold_entities(self):
        for file in self.gold_files:
            corpus_name = str(file).split("/")[-3]
            self.gold_entities[corpus_name] = self.gold_entities.get(corpus_name, {})

            with open(file, "r") as open_file:
                for line in open_file.readlines():
                    doc_id = line.split()[0]
                    start = line.split()[1]
                    end = line.split()[2]
                    url = line.split()[3]
                    entity_type = line.split()[5]
                    surface_form = line.split()[6]

                    # "entity_type": entity_type,
                    self.gold_entities[corpus_name][doc_id] = self.gold_entities[corpus_name].get(doc_id, {})
                    self.gold_entities[corpus_name][doc_id][f"{start}-{end}"] = {
                        "doc_id": doc_id,
                        "start": int(start),
                        "end": int(end),
                        "url": url,
                        "surface_form": surface_form,
                        "endorsements": {}
                    }
        with open("gold_entities.json", "w") as open_file:
            json.dump(self.gold_entities, open_file, indent=4, sort_keys=True)
        # print(self.gold_entities)

    def get_computer_files(self):

        for corpus_name in self.corpora_names:
            self.computer_files[corpus_name] = self.computer_files.get(corpus_name, {})

            for computer in self.computer_names:
                self.computer_files[corpus_name][computer] = self.computer_files[corpus_name].get(computer, {})

                files = list([
                    file
                    for file
                    in Path(self.rucksack_location).glob(f"rucksack_{corpus_name}-{computer}*")
                    if file.is_file()
                ])
                # datetime.strptime(date, "%d-%b-%y")
                self.computer_files[corpus_name][computer] = files

    def get_computed_entities(self):
        # self.gold_entities[corpus_name][doc_id]
        # self.computed_entities

        for corpus_name, computers in self.computer_files.items():
            # print(corpus_name, computers)

            for computer_name, files in computers.items():
                if len(files) <= 0:
                    continue
                # print(computer_name, files)

                for file in files:
                    with open(file) as open_file:
                        computer_data = json.load(open_file)
                    # print(file, computer_data['data']['computed'].keys())

                    for doc_id, entities in computer_data['data']['computed'].items():
                        # print(doc_id, len(entities))
                        for entity in entities:
                            # print(doc_id, entity)
                            self.computed_entities[corpus_name] = self.computed_entities.get(corpus_name, {})
                            self.computed_entities[corpus_name][doc_id] = self.computed_entities[corpus_name].get(doc_id, [])

                            # "entity_type": entity['entity_type'],
                            self.computed_entities[corpus_name][doc_id].append({
                                "doc_id": doc_id,
                                "computer_name": computer_name,
                                "start": int(entity['document_start']),
                                "end": int(entity['document_end']),
                                "url": entity['key'],
                                "surface_form": entity['surfaceForm']
                            })

    def get_endorsement(self):
        for gold_corpus_name, gold_doc_ids in self.gold_entities.items():
            # print(corpus_name, doc_ids.keys())
            # print(gold_corpus_name)
            for gold_doc_id, gold_entities in gold_doc_ids.items():
                # print(gold_corpus_name, gold_doc_id, gold_entities)
                # print(f"\n{gold_doc_id}")

                for gold_entity_id, gold_entity in gold_entities.items():
                    # print(gold_entities)
                    self.endorsement[gold_corpus_name] = self.endorsement.get(gold_corpus_name, {})
                    self.endorsement[gold_corpus_name][gold_doc_id] = self.endorsement[gold_corpus_name].get(gold_doc_id, {})
                    self.endorsement[gold_corpus_name][gold_doc_id][f"{gold_entity['start']}-{gold_entity['end']}"] = gold_entity
                    # print(self.endorsement)

                    if gold_corpus_name not in self.computed_entities:
                        continue

                    if gold_doc_id not in self.computed_entities[gold_corpus_name]:
                        continue

                    # entity = deepcopy(gold_entity)
                    # print(f"Gold: ({gold_entity['start']} - {gold_entity['end']})")
                    for computed_entity in self.computed_entities[gold_corpus_name][gold_doc_id]:
                        state = self.get_comparison(gold_entity, computed_entity)
                        computed_entity['state'] = state
                        # self.endorsement[gold_corpus_name][gold_doc_id][f"{computed_entity['start']}-{computed_entity['end']}"] = gold_entity

                        if state:
                            # print(computed_entity)
                            # entity["endorsements"].append(computed_entity)
                            self.endorsement[gold_corpus_name][gold_doc_id][f"{gold_entity['start']}-{gold_entity['end']}"]['endorsements'][f"{computed_entity['computer_name']}:{computed_entity['start']}-{computed_entity['end']}"] = computed_entity

        with open("endorsements.json", "w") as open_file:
            json.dump(self.endorsement, open_file, indent=4, sort_keys=True)

    def get_comparison(self, gold_entity, computed_entity):

        # "same_type": gold_entity['entity_type'] == computed_entity['entity_type'],
        states = {
            "same_url": gold_entity['url'] == computed_entity['url'],
            "same_surfaceForm": gold_entity['surface_form'] == computed_entity['surface_form'],
            "overlap": gold_entity['end'] >= computed_entity['start'] and gold_entity['start'] <= computed_entity['end'],
            "same_start": gold_entity['start'] == computed_entity['start'],
            "same_end": gold_entity['end'] == computed_entity['end']
        }

        # multiline_logging(app, states)
        if all([states[condition] for condition in conditions[self.endorsement_condition]]):
            # print('perfect')
            result = states

        elif states["same_start"] and states["same_end"]:
            result = states

        elif states['overlap']:
            result = states

        else:
            result = False

        return result

    def get_annotator_used(self, corpus_name):
        annotators_used = set()
        for doc, entries in self.endorsement[corpus_name].items():
            for entry_key, entry in entries.items():
                for key, value in entry['endorsements'].items():
                    # print(value['computer_name'])
                    annotators_used.add(value['computer_name'])
        return annotators_used

    def get_evaluation(self):

        for corpus, docs in self.endorsement.items():
            number_annotators_used = len(self.get_annotator_used(corpus))

            if number_annotators_used <= 0:
                continue

            print(f"\n{corpus}\n{'-' * len(corpus)}")
            self.evaluation[corpus] = {}

            total_possible_corpus_points = 0
            corpus_points = 0

            for doc, entries in docs.items():
                self.evaluation[corpus][doc] = {}
                total_possible_doc_points = 0
                doc_points = 0

                for entry_key, entry in entries.items():
                    self.evaluation[corpus][doc][entry_key] = {
                        "agreeing_annotators": [],
                        "agreement_count": 0,
                        "score": 0
                    }

                    for endorsement_key, endorsement in entry["endorsements"].items():

                        if endorsement['state'] and endorsement['state']['same_url']:
                            self.evaluation[corpus][doc][entry_key]["agreeing_annotators"].append(endorsement['computer_name'])
                            self.evaluation[corpus][doc][entry_key]["agreement_count"] += 1

                    score = self.evaluation[corpus][doc][entry_key]["agreement_count"] / number_annotators_used
                    self.evaluation[corpus][doc][entry_key]["score"] = score
                    total_possible_doc_points += 1
                    doc_points += score

                # self.evaluation[corpus][doc]['total_possible_doc_points'] = total_possible_doc_points
                # self.evaluation[corpus][doc]['doc_points'] = doc_points

                total_possible_corpus_points += total_possible_doc_points
                corpus_points += doc_points

            print(f"Result: {corpus_points}/{total_possible_corpus_points}")

        with open("evaluation.json", "w") as open_file:
            json.dump(self.evaluation, open_file, indent=4, sort_keys=True)


if __name__ == "__main__":
    main = Main()
    main.run()
