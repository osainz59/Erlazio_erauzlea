import argparse
import pandas as pd
import json

from erlazio_erauzlea.corpus.utils import to_json


def json_fitxategiak_lortu(datasetak, tokens, irteera, verbose):
    rel2id = {
        'Nil': 0,
        'AtLocation': 1,
        'IsA': 2,
        'PartOf': 3,
        'UsedFor': 4
    }

    with open(irteera + '/rel2id.json', 'wt') as fitx:
        json.dump(rel2id, fitx, indent='\t')

    tokens = pd.read_csv(tokens, sep='\t', index_col=0, encoding='latin-1', compression='bz2')

    for dataset in datasetak:
        print('Dataseta: {}'.format(dataset))
        dataset_name = ".".join(dataset.split('/')[-1].split('.')[:-1]) + '.json'

        dataset = pd.read_csv(dataset, sep='\t')
        json_dataset = to_json(dataset, tokens)

        with open(irteera + '/' + dataset_name, 'wt') as fitx:
            json.dump(eval(json_dataset), fitx, indent='\t')



def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="dataseta_to_json",
                                     description="Hiztegi batean oinarrituta tripletak erauzi")

    parser.add_argument('-datasetak', nargs='+', dest='datasetak',
                        help="Erauzi nahi diren erlazioak.")
    parser.add_argument('-esaldiak', type=str, dest='tokens',
                        help="Esaldiak gordetzen dituen fitxategiaren helbidea.")
    parser.add_argument('-o', type=str, dest='irteera',
                        help="Datasetak gordetzeko karpearen helbidea.")

    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()

    if args.datasetak is None:
        raise IOError('Sar itzazu nahi dituzun datasetak -datasetak [dataset1] [dataset2] ... ')
    if args.irteera is None:
        raise IOError('Irteera fitxategia beharrezko argumentu bat da.')
    if args.tokens is None:
        raise IOError('Esaldiak fitxategia beharrezko argumentu bat da.')

    # Deitu funtziori
    json_fitxategiak_lortu(**vars(args))


if __name__ == "__main__":
    main()
