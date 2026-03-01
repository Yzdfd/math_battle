import random

# Define player and monster Hp

player_hp = 100
monster_hp = 100

# Define game start
print("Welcome to Math Battle!")

while player_hp > 0 and monster_hp > 0:
    # Generate random math problem
    print("Player Hp : ", player_hp)
    print("Monster Hp : ", monster_hp)
    
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 30)
    
    print(f"Soal {num1} + {num2}?")
    answer = int(input("Jawaban Kamu : "))
    if answer == num1 + num2:
        damage = random.randint(5, 30)
        monster_hp -= damage
        print(f"Kamu Benar!, Kamu memberikan damage sebesar {damage} ke Monster.")
    else:
        damage = random.randint(5, 30)
        player_hp -= damage
        print(f"Kamu Salah!, Monster memberikan damage sebesar {damage} ke Player.")
    
    if player_hp <= 0:
        print(f"Kamu Kalah! Sisa HP monster sebesar {monster_hp}")
    else : 
        print(f"Kamu Menang!")