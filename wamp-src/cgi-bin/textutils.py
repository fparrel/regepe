# -*- coding: latin_1 -*-

import unicodedata
import sys

def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def remove_accents(input_str,encoding):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str,encoding))
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii

def main():
    print remove_accents('été à la braïssa','latin1')

if __name__=='__main__':
    main()
