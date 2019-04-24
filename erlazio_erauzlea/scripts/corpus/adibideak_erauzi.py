import argparse
import pandas as pd

from erlazio_erauzlea.corpus.distant_supervision import Solr


def adibideak_erauzi(url, conceptnet, nil_adibide_kopurua, output, verbose):
    # Sortu solr instantzia
    solr = Solr(url)

    # Erauzi tripleten adibideak
    conceptnet = pd.read_csv(conceptnet, sep='\t')
    corpusa = solr.erauzi_corpusa(conceptnet)

    # Erauzi NIL adibideak
    nil_adibideak = solr.sortu_nil_adibideak(conceptnet, n=nil_adibide_kopurua, verbose=verbose)

    corpusa.append(nil_adibideak, ignore_index=True)

    # Gorde dataseta
    corpusa.to_csv(output, sep='\t', index=False)


def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="conceptnet_iragazlea",
                                     description="Hiztegi batean oinarrituta tripletak erauzi")
    parser.add_argument('-url', type=str, dest='url',
                        help="Solr zerbitzariaren helbidea.")
    parser.add_argument('-cn', type=str, dest='conceptnet',
                        help="Conceptnet-eko tripleta multzoa.")
    parser.add_argument('-nil', type=int, dest='nil_adibide_kopurua',
                        help="NIL adibide kopurua.", default=0)
    parser.add_argument('-o', type=str, dest='output',
                        help="Output fitxategia.")
    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()

    # Argumentuak ondo jaso direla ziurtatu
    if args.url is None:
        raise IOError('Solr zerbitzariaren URL-a beharrezko argumentu bat da.')

    if args.conceptnet is None:
        raise IOError('CN sarrera fitxategia beharrezko argumentu bat da.')

    if args.output is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    # Deitu funtziori
    adibideak_erauzi(**vars(args))


if __name__ == "__main__":
    main()
