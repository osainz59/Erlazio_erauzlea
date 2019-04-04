import argparse
import numpy as np

from erlazio_erauzlea.corpus.terminoak import TerminoakLDA, TerminoakWordNet


def terminoak_erauzi(sarrera, irteera, emaitzak, mota='wordnet', verbose=False):
    if mota is 'wordnet':
        erauzlea = TerminoakWordNet()
        terminoak, balioak = erauzlea.erauzi_terminoak()
    elif mota is 'lda':
        erauzlea = TerminoakLDA()
        terminoak, balioak = erauzlea.erauzi_terminoak(sarrera)

        if emaitzak:
            balioak.to_csv(emaitzak, sep='\t', index=False)
    else:
        raise ValueError("mota argumentua 'wordnet' edo 'lda' izan behar du.")

    np.save(irteera, terminoak)


def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="termino_erauzlea", description="Domeinuko terminoak erauzi.")
    parser.add_argument('-i', type=str, dest='sarrera',
                        help="Corpus fitxategiaren path-a.")
    parser.add_argument('-o', type=str, dest='irteera',
                        help="Terminoen zerrenda gordeko duen fitxategiaren izena.")
    parser.add_argument('-emaitzak', type=str, dest='emaitzak',
                        help="Prozesuan lortutako balioen emaitzak gordetzeko fitxategia.")
    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()

    # Argumentuak ondo jaso direla ziurtatu
    if args.sarrera is None:
        raise IOError('Sarrera fitxategia beharrezko argumentu bat da.')

    if args.irteera is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    # Deitu funtziori
    terminoak_erauzi(**vars(args))


if __name__ == "__main__":
    main()
