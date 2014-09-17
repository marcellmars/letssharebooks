# -*- coding: utf-8 -*-

from lxml import etree

class OpfWriter(object):
    def __init__(self):
        self.opf_namespace = 'http://www.idpf.org/2007/opf'
        self.dc_namespace = 'http://purl.org/dc/elements/1.1/'


    def create_root(self):
        self.opf_root = etree.Element('package',
                                      {'xmlns': self.opf_namespace,
                                       'unique-identifier' : 'uuid_id'})
        self.metadata = etree.SubElement(self.opf_root,
                                         'metadata',
                                         nsmap = {'dc': self.dc_namespace,
                                                  'opf': self.opf_namespace})

    def create_dc_element(self, key, val):
        v = etree.SubElement(self.metadata, '{%s}%s' % (self.dc_namespace, key))
        v.text = val

    def write_opf(self, p = False):
        opf_string = '{}'.format(etree.tostring(self.opf_root,
                                                pretty_print=True,
                                                encoding='utf-8',
                                                xml_declaration=True))
        if p:
            with open(p, 'w') as f:
                f.write(opf_string)
        else:
            print(opf_string)

