

def PF(arg1_pos, arg2_pos):
    """
    Ze argumentu datorren lehendabizi adierazten du.

    :param arg1_pos: Lehenengo argumentuaren posizioa.
    :param arg2_pos: Bigarren argumentuaren posizioa.
    :return: Ze argumentu datorren lehendabizi adierazten du.
    """
    return "PF: " + ("0" if arg1_pos < arg2_pos else "1")


def WM1(a, b, tokens):
    """
    Lehenengo argumentuaren hitzak. Bag of words in Mention 1.

    :param a: Lehenengo argumentuaren lehendabiziko posizioa.
    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Lehenengo argumentuaren hitzak.
    """
    return "WM1: " + " ".join(tokens[a:b])


def WM2(c, d, tokens):
    """
    Bigarren argumentuaren hitzak. Bag of words in Mention 2.

    :param c: Bigarren argumentuaren lehendabiziko posizioa.
    :param d: Bigarren argumentuaren azkeneko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bigarren argumentuaren hitzak.
    """
    return "WM2: " + " ".join(tokens[c:d])


def HM1(b, tokens):
    """
    Lehenengo argumentuaren erroa. Head of Mention 1.

    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Lehenengo argumentuaren erroa.
    """
    return "HM1: " + tokens[b-1]


def HM2(d, tokens):
    """
    Bigarren argumentuaren erroa. Head of Mention 2.

    :param d: Bigarren argumentuaren azkeneko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bigarren argumentuaren erroa.
    """
    return "HM2: " + tokens[d-1]


def HM12(b, d, tokens):
    """
    HM1 eta HM2-ren konbinaketa. Combination of HM1 and HM2.

    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param d: Bigarren argumentuaren azkeneko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: HM1 eta HM2-ren konbinaketa.
    """
    return "HM12: " + " ".join([tokens[b-1], tokens[d-1]])


def WBNULL(b, c):
    """
    Bi argumentuen artean hitzik ez daudenean. When no words in between.

    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param c: Bigarren argumentuaren lehendabiziko posizioa.
    :return: "WBNULL" Bi argumentuen artean hitzik ez daudenean ezer bestela.
    """
    return None if b < c else "WBNULL"


def WBFL(b, c, tokens):
    """
    Bi argumentuen artean dagoen hitz bakarra hitz bakarra dagoenean. The only word in between
    when only one word in between.

    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param c: Bigarren argumentuaren lehendabiziko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bi argumentuen artean dagoen hitz bakarra hitz bakarra dagoenean.
    """
    if c - b != 1:
        return None
    else:
        return "WBFL: " + tokens[b]


def WBF(b, c, tokens):
    """
    Bi argumentuen arteko lehendabiziko hitza bi argumentuen artean bi hitz edo gehiago daudenean.
    First word in between when at least two words in between.

    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param c: Bigarren argumentuaren lehendabiziko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bi argumentuen arteko lehendabiziko hitza bi argumentuen artean bi hitz edo gehiago daudenean.
    """
    if c - b < 2:
        return None
    else:
        return "WBF: " + tokens[b]


def WBL(b, c, tokens):
    """
    Bi argumentuen arteko azkeneko hitza bi argumentuen artean bi hitz edo gehiago daudenean.
    Last word in between when at least two words in between.

    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param c: Bigarren argumentuaren lehendabiziko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bi argumentuen arteko azkeneko hitza bi argumentuen artean bi hitz edo gehiago daudenean.
    """
    if c - b < 2:
        return None
    else:
        return "WBL: " + tokens[c-1]


def WBO(b, c, tokens):
    """
    Bi argumentuen arteko hitzak lehenengoa eta azkenekoa ezik bi argumentuen artean hiru hitz edo gehiago daudenean.
    Other words in between except first and last when at least three words in between.

    :param b: Lehenengo argumentuaren azkeneko posizioa.
    :param c: Bigarren argumentuaren lehendabiziko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bi argumentuen arteko hitzak lehenengoa eta azkenekoa ezik bi argumentuen artean hiru hitz edo gehiago daudenean.
    """
    if c - b < 3:
        return None
    else:
        return "WBO: " + " ".join(tokens[b+1:c-1])


def BM1F(a, tokens):
    """
    Lehenengo hitza lehenengo argumetuaren aurretik. First word before Mention 1.

    :param a: Lehenengo argumentuaren lehendabiziko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Lehenengo hitza lehenengo argumetuaren aurretik.
    """
    if a < 1:
        return None
    else:
        return "BM1F: " + tokens[a-1]


def BM1L(a, tokens):
    """
    Bigarren hitza lehenengo argumentuaren aurretik. Second word before Mention 1.

    :param a: Lehenengo argumentuaren lehendabiziko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bigarren hitza lehenengo argumentuaren aurretik.
    """
    if a < 2:
        return None
    else:
        return "BM1L: " + tokens[a-2]


def AM2F(d, tokens):
    """
    Lehenengo hitza bigarren argumetuaren ondoren. First word after Mention 2.

    :param d: Bigarren argumentuaren azkeneko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Lehenengo hitza bigarren argumetuaren ondoren.
    """
    if d > len(tokens) - 1:
        return None
    else:
        return "AM2F: " + tokens[d]


def AM2L(d, tokens):
    """
    Bigarren hitza bigarren argumentuaren ondoren. Second word after Mention 2.

    :param d: Bigarren argumentuaren azkeneko posizioa.
    :param tokens: Esaldiaren token seguida.
    :return: Bigarren hitza bigarren argumentuaren ondoren.
    """
    if d > len(tokens) - 2:
        return None
    else:
        return "AM2L: " + tokens[d + 1]


def ET12(arg1, arg2, izen_lexikografikoak):
    """
    Bi argumentuen izen lexikografikoen konbinaketa. Combination of mention entity types.

    :param arg1: Lehenengo argumentua.
    :param arg2: Bigarren argumentua.
    :param izen_lexikografikoak: (Argumentu - Izen Lexikografiko) ezagunen lista.
    :return: Bi argumentuen izen lexikografikoen konbinaketa.
    """
    return "ET12: " + " ".join([izen_lexikografikoak[arg1][0], izen_lexikografikoak[arg2][0]])


def lortu_ezaugarri_guztiak(arg1_pos, arg2_pos,
                            a, b, c, d,
                            a1, a2, tokens, izen_lexikografikoak):
    ezaugarriak = [
        PF(arg1_pos, arg2_pos),
        WM1(a, b, tokens),
        WM2(c, d, tokens),
        HM1(b, tokens),
        HM2(d, tokens),
        HM12(b, d, tokens),
        WBNULL(b, c),
        WBFL(b, c, tokens),
        WBF(b, c, tokens),
        WBL(b, c, tokens),
        WBO(b, c, tokens),
        BM1F(a, tokens),
        BM1L(a, tokens),
        AM2F(d, tokens),
        AM2L(d, tokens),
        ET12(a1, a2, izen_lexikografikoak)
    ]

    # Ezabatu None ezaugarriak
    ezaugarriak = [ezaugarri for ezaugarri in ezaugarriak if ezaugarri is not None]

    return ezaugarriak