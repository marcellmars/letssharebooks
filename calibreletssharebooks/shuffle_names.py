import random, string

first_names = ['abb3', 'abbe', 'adam', 'c0ffin', 'charl3s', 'charles', 'coffin', 'ephraim', 'ezra', 'franz', 'g0tthold', 'g3org', 'g3rard', 'gaspard', 'georg', 'gerard', 'gottfri3d', 'gottfried', 'gotthold', 'gr33n', 'green', 'h3nri', 'henri', 'hug0', 'hugo', 'j0achim', 'j0hann', 'j0hn', 'jacqu3s', 'jacques', 'jak0b', 'jakob', 'joachim', 'johann', 'john', 'jos3ph', 'joseph', 'k0nrad', 'konrad', 'langd0n', 'langdon', 'm3lvil', 'melvi1', 'melvil', 'mich3l', 'miche1', 'michel', 'pau1', 'paul', 'philipp', 'st3phan', 'stephan', 'thadd3us', 'thaddeus', 'vinc3ntius', 'vincentius', 'wilh3lm', 'wilhelm', 'william']

last_names = ['abb0t', 'abbot', 'bartsch', 'bl0tius', 'blotius', 'brun3t', 'brunet', 'cogsw3ll', 'cogswell', 'crosw3ll', 'croswell', 'd3w3y', 'd3wey', 'dew3y', 'dewey', 'f0lsom', 'folsom', 'g3ssn3r', 'gessner', 'harris', 'harsdorff3r', 'harsdorffer', 'j3w3tt', 'j3wett', 'jew3tt', 'jewett', 'jungius', 'l3blond', 'l3ibniz', 'l3ssing', 'la f0untain', 'la fountain', 'leblond', 'leibniz', 'lessing', 'mos3r', 'moser', 'otl3t', 'otlet', 'placcius', 'raut3nstrauch', 'rautenstrauch', 'ridl3r', 'ridler', 'rozi3r', 'rozier', 'sibl3y', 'sibley', 'van swi3t3n', 'van swi3ten', 'van swiet3n', 'van swieten']


def get_libranon(middle=False):
    if middle:
        return "{} {} {}".format(string.capwords(random.choice(first_names)), string.capwords(random.choice(first_names)), string.capwords(random.choice(last_names)))
    else:
        return "{} {}".format(string.capwords(random.choice(first_names)), string.capwords(random.choice(last_names)))
