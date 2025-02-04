import os

DAYS_WINDOW = 1

CASSATION_PUBLICATION_DICT = {'b': 'Bulletin',
                              'r' : 'Rapport',
                              'l' : 'Lettres de chambre',
                              'c' : 'Communiqué'}
CASSATION_PUBLICATION_FILTERS = ['r', 'c', 'b']

CE_PUBLICATION_DICT = {"A" : "Recueil Lebon",
                       "B" : "Mentionné dans les tables",
                       "R" : "Non publié mais présentant un intérêt majeur",
                       "C" : "Non publiée et dont l'intérêt particulier"}
CE_PUBLICATION_FILTERS = ['A', 'B']

BUCKET_NAME = "deciscope"
CASSATION_DECISIONS_S3_FILE = "cassation_processed_decisions_id.txt"
CE_DECISIONS_S3_FILE = "ce_processed_decisions_id.txt"