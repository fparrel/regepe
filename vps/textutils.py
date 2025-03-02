# -*- coding: latin1 -*-

import unicodedata

def remove_accents(input_str,encoding):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str,encoding))
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii

def main():
    print(remove_accents('�t� � la bra�ssa','latin1'))

if __name__=='__main__':
    main()
