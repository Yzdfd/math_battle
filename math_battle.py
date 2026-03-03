import random
import time

# Define char and monster hp
def chara_difficulty():
    print("Welcome to Math Battle!")
    print("Character")
    print("1. Tanker (Hp 200, Damage 7-12)")
    print("2. Fighter (Hp 175, Damage 10-17)")
    print("3. Assasin (Hp 75, Damage 20-34)")
    char = int(input("Choose Your Character : "))
    if char == 1:
        char = "Tanker"
        player_hp = 200
        damage_range = (7, 12)
    elif char == 2:
        char = "Fighter"        
        player_hp = 175
        damage_range = (10, 17)
    elif char == 3:
        char = "Assasin"
        player_hp = 75
        damage_range = (20, 34)
    print(f"You Choose Character {char} with Hp {player_hp} and Damage {damage_range}")
    
    print("\nTimer")
    print("1. 20 Seconds")
    print("2. 15 Seconds")
    print("3. 10 Seconds")
    time_limit = int(input("Choose Your Time Limit : "))
    if time_limit == 1:
        time_limit = 20     
    elif time_limit == 2:   
        time_limit = 15
    elif time_limit == 3:
        time_limit = 10
    print(f"You Choose Time Limit {time_limit} Seconds")
    

    print("\nDifficulty")
    print("1. Easy (Hp 100, Damage 7 - 12)")
    print("2. Medium (Hp 200, Damage 10 - 15)")
    print("3. Hard (Hp 250, Damage 13 - 18)")
    print("4. Extreme (Hp 450, Damage 25 - 70)")
    difficulty = int(input("Choose Your Difficulty : "))
    if difficulty == 1:
        monster_hp = 100
        monster_damage_range = (7, 12)
    elif difficulty == 2:
        monster_hp = 200
        monster_damage_range = (10, 15)
    elif difficulty == 3:
        monster_hp = 250
        monster_damage_range = (13, 18)
    elif difficulty == 4:
        monster_hp = 450
        monster_damage_range = (25, 70)
    print(f"Monster HP : {monster_hp}, Monster Damage Range : {monster_damage_range}")
    
    
    return player_hp, monster_hp, damage_range, monster_damage_range, time_limit

    
def mechanic_game(player_hp, monster_hp, damage_range, monster_damage_range, time_limit):
    while player_hp > 0 and monster_hp > 0:
        
        print("\nPlayer Hp : ", player_hp)
        print("Monster Hp : ", monster_hp)
        
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        operators = ['+','-']
        # operators = ['+','-','*','/','^']
        operator = random.choice(operators)
        
        print(f"Soal {num1} {operator} {num2} ? ")
        start_time = time.time() 
        answer = float(input("Your Answer : "))
        end_time = time.time()
        elapsed_time = end_time - start_time 
        
        if operator == '+':
            correct_answer = num1 + num2
        elif operator == '-':
            correct_answer = num1 - num2
        elif operator == '*':
            correct_answer = num1 * num2
        elif operator == '/':
            correct_answer = num1 / num2
        elif operator == '^':
            correct_answer = num1 ** num2
            
        if answer == correct_answer and elapsed_time <= time_limit:
            if elapsed_time <= 2:
                damage = random.randint(damage_range[0], damage_range[1]) * 2
                print(f"Correct! You deal CRITICAL HIT {damage} damage to the Monster.")
                print(f"Time taken: {elapsed_time:.2f} seconds")
            else:
                damage = random.randint(damage_range[0], damage_range[1])
                print(f"Correct! You deal {damage} damage to the Monster.")
                print(f"Time taken: {elapsed_time:.2f} seconds")
            monster_hp -= damage

        else:
            damage = random.randint(monster_damage_range[0], monster_damage_range[1])
            player_hp -= damage
            print(f"Wrong! The Monster deals {damage} damage to you.")
            print(f"Time taken: {elapsed_time:.2f} seconds")
        
    if player_hp <= 0:
        print(f"You Lose! Monster's remaining HP is {monster_hp}")
    else:
        print(f"You Win! Your remaining HP is {player_hp}")
      
def main():
    player_hp, monster_hp, damage_range, monster_damage_range, time_limit = chara_difficulty()
    mechanic_game(player_hp, monster_hp, damage_range, monster_damage_range, time_limit)


main()
