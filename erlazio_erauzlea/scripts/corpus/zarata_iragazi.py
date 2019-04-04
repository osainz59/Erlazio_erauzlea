import argparse
import pandas as pd

from erlazio_erauzlea.corpus import iragazketak
from erlazio_erauzlea.corpus.utils import kalkulatu_erlazioen_adibide_proportzioa


def zarata_iragazi(input, output, pmi_atalasea, verbose):
    # Irakurri dataseta
    dataseta = pd.read_csv(input, sep='\t')

    print("Datasetaren proportzioak...")
    print(kalkulatu_erlazioen_adibide_proportzioa(dataseta))

    # Argumentuetan oinarritutako iragazketak
    print("Argumentuetan oinarritutako iragazketak...", end="", flush=True)
    dataseta = iragazketak.argumentu_berdineko_tripletak_ezabatu(dataseta)
    dataseta = iragazketak.multiwordeko_argumentu_berdineko_tripletak_ezabatu(dataseta)
    print('Okey!')

    # Nil gabeko subseta
    not_nil = dataseta[dataseta.rel != 'Nil']
    nil = dataseta[dataseta.rel == 'Nil']

    # PMI aplikatu
    print("PMI iragazketa...", end="", flush=True)
    pmi = iragazketak.pmi_iragazketa(not_nil, atalasea=pmi_atalasea, verbose=verbose)[['arg1', 'arg2', 'rel', 'docid']]
    dataseta = pmi.append(nil, ignore_index=True)
    print('Okey!')

    # Kopuruan oinarritutako iragazketa
    print("Kopuruan oinarritutako iragazketak...", end="", flush=True)
    dataseta = iragazketak.agerpen_gutxiko_tripletak_ezabatu(dataseta)
    print('Okey!')

    # Ezabatu multi-instance adibideak
    #print("Multi-instance-ak garbitu...", end="", flush=True)
    #dataseta = iragazketak.multi_instance_adibideak_iragazi(dataseta)
    #print('Okey!')

    dataseta.reset_index(inplace=True)
    del dataseta['index']

    print("Dataset berriaren proportzioak...")
    print(kalkulatu_erlazioen_adibide_proportzioa(dataseta))

    # Gorde dataset berriak
    dataseta.to_csv(output, sep='\t', index=False)


def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="conceptnet_iragazlea",
                                     description="Hiztegi batean oinarrituta tripletak erauzi")
    parser.add_argument('-i', type=str, dest='input',
                        help="Output fitxategia.")
    parser.add_argument('-o', type=str, dest='output',
                        help="Output fitxategia.")
    parser.add_argument('-pmi', type=float, dest='pmi_atalasea',
                        help="PMI atalase desberdinak.")
    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()

    # Argumentuak ondo jaso direla ziurtatu
    if args.input is None:
        raise IOError('Sarrera fitxategia beharrezko argumentu bat da.')

    if args.output is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    # Deitu funtziori
    zarata_iragazi(**vars(args))


if __name__ == "__main__":
    main()
