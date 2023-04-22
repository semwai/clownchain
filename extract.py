import random


class Jokes:

    def __init__(self, path="very cringe jokes.txt") -> None:
        try:
            with open(path, encoding="utf-8") as f:
                Jokes.data = f.read().split("* * *")
        except FileNotFoundError:
            Jokes.data = []

    def __call__(self):
        return random.choice(Jokes.data) if len(Jokes.data) > 0 else None


if __name__ == "__main__":
    joke = Jokes()
    for i in range(1):
        print(i + 1, joke())
