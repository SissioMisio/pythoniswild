def check_drinks():
    try:
        drinks = int(input("Quantas já mamaste hoje, meu ganda maluco? "))
        if drinks > 10:
            print("Olha lá, já bebeste umas quantas, cuidado para não te estoirar a pescada!")
        elif drinks > 5:
            print("Ganda maluco, já não mamas mais Super Bock! Vai dormir!")
        else:
            print("Vá lá, ainda podes mamar mais umas quantas, mas não abuses! Olha a PIDE!")
    except ValueError:
        print("Já deves estar todo estourado, só podes meter números inteiros, não é assim tão difícil! Levas com dois estoiros dum bacalhau!")

if __name__ == "__main__":
    check_drinks()