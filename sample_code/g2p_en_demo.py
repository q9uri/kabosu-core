if __name__ == '__main__':
    from kabosu_core.g2p_en import G2p
    texts = ["I have $250 in my pocket.", # number -> spell-out
             "popular pets, e.g. cats and dogs", # e.g. -> for example
             "I refuse to collect the refuse around here.", # homograph
             "I'm an activationist."] # newly coined word
    g2p = G2p()
    for text in texts:
        out = g2p(text)
        print(out)
