def treino(treinamento):
    def meu_treino(treino_valor):
        treino = treinamento(treino_valor)
        if treino.split("-")[1] == "00":
            return treino.upper()
        return "esse treino já é outro treinamento"
    return meu_treino

@treino
def treinamento(treino):
    return "esse treino é o treinamento" + f"-{treino}"

print(treinamento("00"))
print(treinamento("01"))