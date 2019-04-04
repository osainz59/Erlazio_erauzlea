import argparse

from erlazio_erauzlea.corpus.testu_prozesaketa import corpus_to_token_lemma_pos


def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="conceptnet_iragazlea", description="Hiztegi batean oinarrituta tripletak erauzi")
    parser.add_argument('-i', type=str, dest='corpus',
                        help="Corpusa.")
    parser.add_argument('-t', type=str, dest='output_token',
                        help="Tokenak gordetzeko fitxategia.")
    parser.add_argument('-l', type=str, dest='output_lemma',
                        help="Lemak gordetzeko fitxategia.")
    parser.add_argument('-p', type=str, dest='output_pos',
                        help="POS etiketak gordetzeko fitxategia.")
    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()

    # Argumentuak ondo jaso direla ziurtatu
    if args.corpus is None:
        raise IOError('Sarrera fitxategia beharrezko argumentu bat da.')

    if args.output_token is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    if args.output_lemma is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    if args.output_pos is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    # Deitu funtziori
    corpus_to_token_lemma_pos(**vars(args))


if __name__ == "__main__":
    main()