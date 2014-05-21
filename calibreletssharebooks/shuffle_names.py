# -*- coding: utf-8 -*-

import random, string


first_names = [u'Ezra', u'Regina', u'Henriette', u'Dušan', u'Adam', u'Pura', u'Walter', u'Hugo', u'Ethel', u'Jorge', u'Howard', u'Jacques', u'Joseph', u'William', u'Robert', u'Melvil', u'Sean', u'Electra', u'Charles', u'Henri', u'Conrad', u'Kenneth', u'Thaddeus', u'Georg', u'Charles', u'Joachim', u'Kovid', u'Markus', u'Léonie', u'Gaspard', u'Gottfried', u'Gotthold', u'Audre', u'Sebastian u', u'Johann', u'Makoto', u'Gabriel', u'Paul', u'Vincentius', u'Shiyali', u'Franz', u'Johann', u'Angela', u'Abbe', u'Carol', u'John', u'Gerard', u'Davidson', u'Martin', u'Luis', u'Charles', u'Green', u'C.', u'La', u'William', u'Philipp', u'Coffin', u'Michel', u'Wilhelm', u'Ephraim', u'Jakob', u'Ramamrita', u'Stephan', u'Wilhelm', u'Ruiz', u'Langdon', u'Van', u'G.']
last_names = [u'Abbot', u'Andrews', u'Avram', u'Barok', u'Bartsch', u'Belpré', u'Benjamin', u'Blotius', u'Bolden', u'Borges', u'Brown', u'Brunet', u'Cogswell', u'Croswell', u'Darnton', u'Dewey', u'Dockray', u'Doren', u'Folsom', u'Fontaine', u'Gessner', u'Goldsmith', u'Harris', u'Harsdorffer', u'Jewett', u'Jungius', u'Goyal', u'Krajewski', u'Lafontaine', u'Leblond', u'Leibniz', u'Lessing', u'Lorde', u'Luetgert', u'Moser', u'Nagao', u'Naudé', u'Otlet', u'Placcius', u'Ranganathan', u'Rautenstrauch', u'Ridler', u'Robles', u'Rozier', u'Seajay', u'Sibley', u'Swieten', u'Wells']


def get_libranon(middle=False):
    if middle:
        return u"{} {} {}".format(string.capwords(random.choice(first_names)), string.capwords(random.choice(first_names)), string.capwords(random.choice(last_names)))
    else:
        return u"{} {}".format(string.capwords(random.choice(first_names)), string.capwords(random.choice(last_names)))
