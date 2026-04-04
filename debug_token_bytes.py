with open(".token.txt", "rb") as f:
    b = f.read()
print(len(b))
print(b[:200])
