import spacy
import time

from annotators import get_nlp_with_all_annotators
from dfiner.ontonote.ontonotes_data import load_ontonotes, GoldMentionView
from dfiner.utils import get_default_config
from dfiner.datastructures.utils import constituent_covers_index


def load_type_to_alias(filepath):
    type_to_alias = {}
    with open(filepath) as f_in:
        errors = 0
        for line in f_in:
            tokens = line.rstrip().split("\t")
            try:
                t, alias = tokens
                type_to_alias.setdefault(t, [])
                type_to_alias[t].append(alias)
            except:
                errors += 1
    return type_to_alias


def get_titles(doc, titles_set, max_ngram_size=3):
    TITLE_LABEL_NAME = 'TITLE'

    mention_view = doc.user_data[GoldMentionView.GOLD_MENTION_VIEW_NAME]
    mention_constituents = mention_view.constituents
    person_consituents = filter(lambda c: c.name == 'PERSON', mention_constituents)
    if len(person_consituents) == 0:
        return []
    hits = []
    person_starts, person_ends = map(set, zip(*[(c.start, c.end)
                                                for c in person_consituents]))
    for n in xrange(max_ngram_size, -1, -1):
        for i in xrange(len(doc)):
            # only care if the previous or next is a person
            if (i-1) in person_ends or (i+n) in person_starts:
                candidate_text = doc[i:i+n].text
                if candidate_text in titles_set:
                    # check if any other mention constituent overlaps
                    if any([constituent_covers_index(c, i) or constituent_covers_index(c, i+n-1) for c in mention_view.constituents]):
                        continue
                    hits.append(candidate_text)
    return hits


def add_titles(doc, titles_set, max_ngram_size=3):
    TITLE_LABEL_NAME = 'TITLE'

    mention_view = doc.user_data[GoldMentionView.GOLD_MENTION_VIEW_NAME]
    mention_constituents = mention_view.constituents
    person_consituents = filter(lambda c: c.name == 'PERSON', mention_constituents)
    if len(person_consituents) == 0:
        return []
    person_starts, person_ends = map(set, zip(*[(c.start, c.end)
                                                for c in person_consituents]))
    for n in xrange(max_ngram_size, -1, -1):
        for i in xrange(len(doc)):
            # only care if the previous or next is a person
            if (i-1) in person_ends or (i+n) in person_starts:
                candidate_text = doc[i:i+n].text
                if candidate_text in titles_set:
                    # check if any other mention constituent overlaps
                    if any([constituent_covers_index(c, i) or constituent_covers_index(c, i+n-1) for c in mention_view.constituents]):
                        continue
                    mention_view.add_constituent_from_args(i, i+n, name=TITLE_LABEL_NAME)


def add_typexs(type_name, doc, type_alias_set, max_ngram_size=3, check_lower=False):
    mention_view = doc.user_data[GoldMentionView.GOLD_MENTION_VIEW_NAME]
    for n in xrange(max_ngram_size, -1, -1):
        for i in xrange(len(doc)):
            candidate_text = doc[i:i + n].text
            if candidate_text in type_alias_set or (check_lower and candidate_text.lower() in type_alias_set):
                if any([constituent_covers_index(c, i) or constituent_covers_index(c, i + n - 1) for c in
                        mention_view.constituents]):
                    continue
                mention_view.add_constituent_from_args(i, i+n, name=type_name)


def get_hits(doc, gold_set, max_ngram_size=3, check_lower=False):
    mention_view = doc.user_data[GoldMentionView.GOLD_MENTION_VIEW_NAME]
    hits = []
    # sents = []
    for n in xrange(max_ngram_size, -1, -1):
        for i in xrange(len(doc)):
            candidate_text = doc[i:i + n].text
            if candidate_text in gold_set or (check_lower and candidate_text.lower() in gold_set):
                if any([constituent_covers_index(c, i) or constituent_covers_index(c, i + n - 1) for c in
                        mention_view.constituents]):
                    continue
                hits.append((candidate_text, doc.text))
                # sents.append(doc.text)
    return hits


# manually checked appropriate aliases on ontonotes
title_set = {
    u'Acting President', u'Actor', u'Admiral', u'Agent', u'Ambassador', u'Artist',
    u'Attorney', u'Author', u'Ayatollah', u'Baron', u'Bishop', u'Brigadier General',
    u'CEO', u'Captain', u'Cardinal', u'Chairman', u'Chancellor', u'Chief Executive',
    u'Chief Judge', u'Chief Justice', u'Chief Minister', u'Coach', u'Colonel', u'Commander',
    u'Commissioner', u'Commodore', u'Composer', u'Comptroller', u'Congressman',
    u'Consultant', u'Corporal', u'Correspondent', u'Council member', u'Councilman',
    u'Councilwoman', u'Counsel', u'Crewman', u'Crier', u'Critic', u'Deputy', u'Deputy Mayor',
    u'Designer', u'Director', u'Doctor', u'Economist', u'Engineer', u'Ethicist',
    u'Executive Director', u'First Lady', u'Foreign Minister', u'Fugitive', u'General',
    u'General Manager', u'General manager', u'Governor', u'Grand Duke', u'Head',
    u'Home Secretary', u'House', u'Industry analyst', u'Inspector', u'Jockey', u'Journalist',
    u'Judge', u'Lieutenant', u'Lieutenant Colonel', u'Lieutenant General', u'Major',
    u'Majority leader', u'Manager', u'Managing Editor', u'Marshal', u'Master', u'Mayor',
    u'Minister', u'Minister of Defense', u'Minister of Education', u'Minister of State',
    u'Mister', u'Mr.', u'Mrs.', u'National Security Advisor', u'Neuroscientist', u'Pioneer',
    u'Pope', u'President', u'Press Secretary', u'Prince', u'Princess', u'Professor',
    u'Prophet', u'Public Relations', u'Reader', u'Seaman', u'Secretary', u'Secretary General',
    u'Secretary of State', u'Solicitor', u'Speaker', u'Staff', u'Supervisor', u'Teacher',
    u'Undersecretary', u'Vicar', u'Vice President',
    u'Writer', u'astronomer', u'coach',u'developer', u'prime minister',
    # unique test hits
    u'Administrator', u'Commissar', u'Director General', u'Foreign Secretary',
    u'General Secretary', u'Imam', u'Inventor', u'Referee'
}

symptom_alias_set = \
    {
        u'Anxiety', u'heart attack', u'hemorrhaging', u'Epilepsy',u'alcoholism',
        u'anorexia', u'anxiety', u'apprehension', u'arthritis', u'asthma',
        u'blackouts', u'bleeding', u'blister', u'boil', u'brain damage',
        u'cataract', u'coma', u'cough', u'dandruff', u'dehydration', u'dementia',
        u'depression', u'diabetes', u'diarrhea', u'dryness', u'emotional security',
        u'engorgement', u'epilepsy', u'euphoria', u'fainting', u'farsightedness',
        u'fatigue', u'fever', u'fidgeting', u'flashbacks', u'fracture', u'fractures',
        u'genital warts', u'guilt', u'headaches', u'heart attack', u'hemorrhaging',
        u'high fever', u'hostility', u'hypertension', u'hypoglycemia', u'immune deficiency',
        u'indigestion', u'infection', u'infertility', u'inflammation',
        u'intestinal obstruction', u'joint pain', u'kidney failure', u'knuckle',
        u'leukemia', u'loneliness', u'low blood sugar', u'major depression', u'malaise',
        u'melancholy', u'mental illness', u'mood disorders', u'mood swings',
        u'morning sickness', u'muscle contractions', u'nausea', u'nightmare', u'nightmares',
        u'obesity', u'ossification', u'osteoporosis', u'pain', u'pallor', u'panic',
        u'paralysis', u'paranoia', u'passed out', u'pneumonia', u'psychosis',
        u'rapid breathing', u'rash', u'renal failure', u'rickets', u'rigor',
        u'sadness', u'screaming', u'seizure', u'seizures', u'shaking',
        u'sleep deprivation', u'spinal tumor', u'squinting', u'starvation',
        u'substance abuse', u'swelling', u'swooning', u'tumor', u'twitching',
        u'vomiting', u'warts', u'wheezing',
        # unique test hits
        u'Cataracts', u'Fever', u'Nausea', u'Weakness', u'aggression', u'anger', u'black eye', u'bone loss', u'feel sick', u'heavy bleeding', u'necrosis', u'overweight', u'shivering', u'snoring'
    }

treatment_set = \
    {
        u'Caesarean section', u'abstinence', u'acupuncture', u'adenocard',
        u'amputation', u'analgesic', u'antidepressant',
        u'antidote', u'antiviral drug', u'aspirin', u'atropine', u'blood transfusion',
        u'bloodletting', u'cataract surgery', u'chemotherapy', u'detoxification',
        u'dialysis', u'diazepam', u'electrolysis', u'fluorouracil', u'formaldehyde',u'hydrotherapy',
        u'knee replacement', u'peritoneal dialysis', u'physical therapy', u'rehabilitation',
        # unique test hits
        u'IN VITRO fertilization', u'eye surgery', u'gene therapy',
        u'lumpectomy',u'mastectomy', u'streptokinase', u'surgery'
    }

drug_set = \
    {
        u'Hepatitis B vaccine', u'adenocard', u'ammonia', u'ammonium',
        u'amphetamine', u'antidepressant', u'antidote', u'antiviral drug',
        u'aspirin', u'atropine', u'carbamide', u'caustic soda', u'cyclosporine',
        u'diethylstilbestrol', u'doxepin', u'fluorine', u'fluorouracil',
        u'formaldehyde', u'gelatin', u'hydrogen peroxide', u'insulin', u'interferon',
        u'levamisole', u'methyl salicylate', u'salicylic acid', u'somatostatin',
        u'steroid', u'stimulant', u'vaccine', u'vinegar',
        # unique test hits
        u'Ascorbic acid', u'Dopamine', u'adrenaline', u'analgesic', u'anesthetic', u'dopamine'
    }

animal_set = \
    {
        u'antelope', u'butterfly', u'canine', u'chimpanzee', u'coyote', u'dog',
        u'donkey', u'fox', u'guinea pig', u'hashish', u'horse', u'jellyfish', u'lobster',
        u'monkey', u'neanderthal', u'octopus', u'owl', u'ox', u'oyster', u'parakeet',
        u'parrotfish', u'penguins', u'pony', u'pug', u'pup', u'rabbit', u'reptiles',
        u'sheep', u'spider', u'squid', u'thoroughbred', u'toad', u'turkey', u'whale', u'whooping crane',
        # unique test hits
        u'cheetah', u'lion', u'mosquito', u'raccoon'
     }

road_set = \
    {
        u'boulevard', u'expressway', u'federal highway', u'main street',
        u'northern highway', u'parkway', u'the highway', u'the parkway',
        # unique test hits
        u'the mound'
    }

if __name__ == '__main__':
    config = get_default_config()
    start_time = time.time()
    print("loading Language from spacy ... ")
    nlp = spacy.load('en')
    nlp.pipeline = [nlp.tagger]
    print(" done. took %.2fs" % (time.time() - start_time))

    start_time = time.time()
    print("loading train docs ... ")
    train_docs = load_ontonotes(nlp, config["ontonotes_train_path"], max_docs=None)
    print(" done. took %.2fs" % (time.time() - start_time))

    figer_type_to_alias_file = config["figer_type_to_alias"]
    start_time = time.time()
    print("loading type_to_alias ... ")
    type_to_alias = load_type_to_alias(figer_type_to_alias_file)
    print(" done. took %.2fs" % (time.time() - start_time))

    # _ = [add_titles(doc, title_set) for doc in train_docs]
    # _ = [add_typexs('MEDICINE', doc, symptom_alias_set.union(drug_set.union(treatment_set))) for doc in train_docs]
    # _ = [add_typexs('ANIMAL', doc, animal_set) for doc in train_docs]
    # _ = [add_typexs('ROAD', doc, road_set) for doc in train_docs]

