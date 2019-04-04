import spacy
import bz2


def corpus_to_token_lemma_pos(corpus, output_token, output_lemma, output_pos, verbose=False):
    nlp = spacy.load('en')

    with bz2.open(corpus, 'rt') as infile, \
            bz2.open(output_token, 'wt') as token_file, \
            bz2.open(output_lemma, 'wt') as lemma_file, \
            bz2.open(output_pos, 'wt') as pos_file:

        # Idatzi goiburukoak
        token_file.write('{}\t{}\n'.format('index', 'tokens'))
        lemma_file.write('{}\t{}\n'.format('index', 'lemma'))
        pos_file.write('{}\t{}\n'.format('index', 'pos'))

        index = 0

        for line in infile:

            # Izenburuak deuseztatu
            if line.startswith('#'):
                if verbose:
                    print(line)
                continue

            # Garbitu lerroa arazoak sor ditzaketen karaktereetatik
            line = line.replace("\"", "")
            line = line.replace("\n", " ")
            line = line.replace("\t", " ")

            doc = nlp(line)

            for sent in doc.sents:
                tokens, lemmas, pos = [], [], []

                # Prozesatu esaldia
                for elem in sent:
                    if '\n' in elem.lower_:
                        continue
                    tokens.append(elem.lower_)
                    lemmas.append(elem.lemma_)
                    pos.append(elem.tag_)

                # Idatzi esaldia
                token_file.write('{}\t{}\n'.format(index, " ".join(tokens).strip()))
                lemma_file.write('{}\t{}\n'.format(index, " ".join(lemmas).strip()))
                pos_file.write('{}\t{}\n'.format(index, " ".join(pos).strip()))

                index += 1


def prozesatu_esaldiak(esaldiak):
    nlp = spacy.load('en')
    tokens, lemmas, pos = [], [], []

    doc = nlp(esaldiak)
    for esaldi in doc.sents:
        t, l, p = [], [], []
        for elem in esaldi:
            t.append(elem.lower_)
            l.append(elem.lemma_)
            p.append(elem.tag_)

        tokens.append(" ".join(t).replace("\t", " ").strip())
        lemmas.append(" ".join(l).replace("\t", " ").strip())
        pos.append(" ".join(p).replace("\t", " ").strip())

    return tokens, lemmas, pos

