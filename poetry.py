import random

# Define some words to use in the poems
nouns = ["tempo", "mundo", "sonho", "luz", "noite", "dia", "coração", "alma", "estrela", "céu"]
verbs = ["corre", "voa", "brilha", "cai", "sobe", "bate", "sussurra", "canta", "dança", "brilha"]
adjectives = ["brilhante", "escuro", "silencioso", "alto", "frio", "quente", "suave", "duro", "profundo", "alto"]
prepositions = ["em", "sobre", "sob", "acima", "entre", "através", "com", "sem", "antes", "depois"]

def generate_poem():
    # Generate a random poem
    poem = []
    for _ in range(4):
        line = f"O {random.choice(adjectives)} {random.choice(nouns)} {random.choice(verbs)} {random.choice(prepositions)} o {random.choice(adjectives)} {random.choice(nouns)}."
        poem.append(line)
    return "\n".join(poem)

# Generate and print a random poem
print(generate_poem())