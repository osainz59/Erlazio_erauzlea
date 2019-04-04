import pandas as pd
import numpy as np

from erlazio_erauzlea.sailkatzailea.ezaugarriak import EzaugarriErauzlea

if __name__ == "__main__":

    # Kargatu aurreprozesatutako Corpus-a
    print("Corpusa kargatu...", end="", flush=True)
    corpus_path = "C:/Users/osain/Desktop/QG/corpus/"
    tokens = pd.read_csv(corpus_path + "corpus_tokens_c.tsv.bz2", sep='\t', compression='bz2')
    lemmas = pd.read_csv(corpus_path + "corpus_lemmas_c.tsv.bz2", sep='\t', compression='bz2')
    train = pd.read_csv(corpus_path + 'and_train_set.tsv', sep='\t')
    dev = pd.read_csv(corpus_path + 'and_dev_set.tsv', sep='\t')
    train_ema = pd.read_csv(corpus_path + 'train_tripletak.tsv', sep='\t')
    izen_lexikografikoak = pd.read_csv(corpus_path + 'word_to_singular_name_entity.tsv', sep='\t')
    izen_lexikografikoak = izen_lexikografikoak.set_index('word').T.to_dict('list')
    print("Okey!")

    # Sortu erauzlearen instantzia
    print("Ezaugarri erauzlea sortu eta egokitu...", end="", flush=True)
    erauzlea = EzaugarriErauzlea(izen_lexikografikoak, ezaugarrien_agerpen_atalasea=0)

    # fit_transform
    X_train, y_train, ema = erauzlea.egokitu_eta_eraldatu(train, tokens, lemmas)
    X_dev, y_dev, _ = erauzlea.eraldatu(dev)
    print("Okey!")
    print(f"Emaitzak berdinak? {train_ema.equals(ema)}")

    # Lortutako ezaugarri matrizearen eta klase aldagaiaren bektorearen dimentsioak
    print(f"Ezaugarri matrizearen dimentsioak: {X_train.shape}, klase aldagaiaren bektorearen dimentsioak: {y_train.shape}")

    # Ikus dezagun adibide bat
    print("Adibide bat:")
    id2feature = {value: key for key, value in erauzlea.lortu_ezaugarri_hiztegia().items()}

    adibidea = X_train.getrow(0)
    indizeak = np.arange(X_train.shape[1])[adibidea.toarray()[0] > 0]

    print(f"Tripleta: ")
    print(np.array(train.loc[0]))
    print(f"Esaldia: {tokens.loc[int(train.loc[0].docid)][0]}")
    print(f"Ezaugarri zerrenda: {[ id2feature[i] for i in indizeak ]}")
