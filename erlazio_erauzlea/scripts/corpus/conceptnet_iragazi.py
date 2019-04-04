import argparse

from erlazio_erauzlea.corpus.distant_supervision import ConceptNet


def conceptnet_iragazi(cn, hiztegia, erlazioak, irteera, verbose=False):
    print("ConceptNet kargatu...", end="", flush=True)
    conceptnet = ConceptNet(cn)
    print("Okey!")
    print("Domeinuko tripletak iragazi...", end="", flush=True)
    conceptnet.erauzi_domeinuko_tripletak(hiztegia, verbose=verbose)
    print("Okey!")
    print("Erauzi aukeratutako tripletak...", end="", flush=True)
    conceptnet.erauzi_erlazioak(erlazioak)
    print("Okey!")

    cn_df = conceptnet.lortu_conceptnet()
    cn_df.to_csv(irteera, sep='\t', index=False)


def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="conceptnet_iragazlea", description="Hiztegi batean oinarrituta tripletak erauzi")
    parser.add_argument('-cn', type=str, dest='cn',
                        help="Conceptnet fitxategiaren path-a.")
    parser.add_argument('-hizt', type=str, dest='hiztegia',
                        help="Hiztegiaren fitxategiaren path-a.")
    parser.add_argument('-erlazioak', nargs='+', dest='erlazioak',
                        help="Erauzi nahi diren erlazioak.")
    parser.add_argument('-o', type=str, dest='irteera',
                        help="Iragazitako ConceptNeta gordetzeko helbidea.")
    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()

    # Argumentuak ondo jaso direla ziurtatu
    if args.cn is None:
        raise IOError('Sarrera fitxategia beharrezko argumentu bat da.')

    if args.hiztegia is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    if args.irteera is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    # Deitu funtziori
    conceptnet_iragazi(**vars(args))


if __name__ == "__main__":
    main()