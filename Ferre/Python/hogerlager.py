loops: int = 0
print("Quizmaster wat is het getal")
num = int(input('Geef getal: '))
while (True):
  loops+=1
  num1 = int(input('Doe gok: '))
  if num > num1:
    print("raad hoger")
  elif num < num1:
    print("raad lager")
  elif num == num1:
    print(f"Goed geraden in {loops} pogingen")
    break
  
  
