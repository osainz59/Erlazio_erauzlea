import argparse
import pandas as pd

from erlazio_erauzlea.corpus.distant_supervision import Solr


def indexatu_corpusa(url, corpusa):

    # Sortu solr instantzia
    solr = Solr(url)

    # Irakurri corpusa
    solr.indexatu_corpusa(corpusa)


def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="indexatu_corpusa",
                                     description="Corpusa Solr bilaketa motorean indexatzeko scripta.")
    parser.add_argument('-url', type=str, dest='url',
                        help="Solr zerbitzariaren helbidea.")
    parser.add_argument('-i', type=str, dest='corpusa',
                        help="Corpusa jasotzen duen tsv-a.")

    args = parser.parse_args()

    # Argumentuak ondo jaso direla ziurtatu
    if args.url is None:
        raise IOError('URL-a beharrezko argumentu bat da.')

    if args.corpusa is None:
        raise IOError('Corpusa beharrezko argumentu bat da.')

    indexatu_corpusa(**vars(args))

if __name__ == "__main__":
    main()
