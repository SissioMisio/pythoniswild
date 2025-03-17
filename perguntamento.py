try:
    age = int(input("Idade: "))
    if age > 100:
        print("Idade inválida. Por favor, insira uma idade realista.")
    elif age >= 21:
        print("Podes mamar Eristoff. Vai para a festa. Bebe com moderação, Super Bock e Eristoff são caros.")
    else:
        print("Volta para o Santal. Não podes beber. Vai estudar. Faz-te útil.")  
except ValueError:
    print("Parece-me que a tua inteligência não é suficiente para responder a esta pergunta. Vai estudar, ou então, mete os óculos e escreve um número inteiro.")