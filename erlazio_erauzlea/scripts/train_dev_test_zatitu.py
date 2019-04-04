import argparse
import pandas as pd

from erlazio_erauzlea.corpus import utils


def dataseta_zatitu(input, output_path, verbose):
    dataseta = pd.read_csv(input, sep='\t')

    train, dev, test = utils.split_dataset(dataseta)

    train.to_csv(output_path+'/train.tsv', sep='\t', index=False)
    dev.to_csv(output_path+'/dev.tsv', sep='\t', index=False)
    test.to_csv(output_path+'/test.tsv', sep='\t', index=False)



def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="conceptnet_iragazlea",
                                     description="Hiztegi batean oinarrituta tripletak erauzi")
    parser.add_argument('-i', type=str, dest='input',
                        help="Output fitxategia.")
    parser.add_argument('-o', type=str, dest='output_path',
                        help="Output fitxategia.")
    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()

    # Argumentuak ondo jaso direla ziurtatu
    if args.input is None:
        raise IOError('Sarrera fitxategia beharrezko argumentu bat da.')

    if args.output_path is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')

    # Deitu funtziori
    dataseta_zatitu(**vars(args))


if __name__ == "__main__":
    main()