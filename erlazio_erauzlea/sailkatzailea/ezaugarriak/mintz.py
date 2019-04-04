

def PF(arg1_pos, arg2_pos):
    """
    Ze argumentu datorren lehendabizi adierazten du.

    :param arg1_pos: Lehenengo argumentuaren posizioa.
    :param arg2_pos: Bigarren argumentuaren posizioa.
    :return: Ze argumentu datorren lehendabizi adierazten du.
    """
    return "PF: " + ("0" if arg1_pos < arg2_pos else "1")


def __BT(b, c, tokens, pos):
    return " ".join(["{}/{}".format(token, tag) for token, tag in zip(tokens[b:c], pos[b:c])])


def __LW(a, tokens, pos, k):
    begin = a - k if a - k >= 0 else 0
    return " ".join(["{}/{}".format(token, tag) for token, tag in zip(tokens[begin:a], pos[begin:a])])


def __RW(d, tokens, pos, k):
    end = d + k if d + k < len(tokens) else len(tokens)
    return " ".join(["{}/{}".format(token, tag) for token, tag in zip(tokens[d:end], pos[d:end])])


def lortu_ezaugarri_guztiak(arg1_pos, arg2_pos,
                            a, b, c, d,
                            tokens, pos, k=3):
    ezaugarriak = [
        PF(arg1_pos, arg2_pos)
    ]

    for i in range(k):
        ezaugarriak.append(
            " ".join([__LW(a, tokens, pos, i), '<ARG>', __BT(b, c, tokens, pos), '<ARG>', __RW(d, tokens, pos, k)]).strip()
        )

    return ezaugarriak