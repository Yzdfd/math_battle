import random
import time
import json
import os

# Define char and monster hp



def chara_difficulty():
    print("Welcome to Math Battle!")
    print("Character")
    print("1. Tanker (Hp 200, Damage 7-12)")
    print("2. Fighter (Hp 175, Damage 10-17)")
    print("3. Assasin (Hp 75, Damage 20-34)")
    while True:
        char = int(input("Choose Your Character : "))
        if char == 1:
            char = "Tanker"
            player_hp = 200
            damage_range = (7, 12)
            break
        elif char == 2:
            char = "Fighter"        
            player_hp = 175
            damage_range = (10, 17)
            break
        elif char == 3:
            char = "Assasin"
            player_hp = 75
            damage_range = (20, 34)
            break
        else :
            print("Invalid Character. Please choose again.")
    print(f"You Choose Character {char} with Hp {player_hp} and Damage {damage_range}")
        
    print("\nTimer")
    print("1. 20 Seconds")
    print("2. 15 Seconds")
    print("3. 10 Seconds")
    while True:
        time_limit = int(input("Choose Your Time Limit : "))
        if time_limit == 1:
            time_limit = 20  
            break   
        elif time_limit == 2:   
            time_limit = 15
            break
        elif time_limit == 3:
            time_limit = 10
            break
        else:
            print("Invalid Time Limit. Please choose again.")
    print(f"You Choose Time Limit {time_limit} Seconds")
    

    print("\nDifficulty")
    print("1. Easy (Hp 100, Damage 7 - 12)")
    print("2. Medium (Hp 200, Damage 10 - 15)")
    print("3. Hard (Hp 250, Damage 13 - 18)")
    print("4. Extreme (Hp 450, Damage 25 - 70)")
    while True:
        difficulty = int(input("Choose Your Difficulty : "))
        if difficulty == 1:
            monster_hp = 100
            monster_damage_range = (7, 12)
            break
        elif difficulty == 2:
            monster_hp = 200
            monster_damage_range = (10, 15)
            break
        elif difficulty == 3:
            monster_hp = 250
            monster_damage_range = (13, 18)
            break
        elif difficulty == 4:
            monster_hp = 450
            monster_damage_range = (25, 70)
            break
        else:   
            print("Invalid Difficulty. Please choose again.")
    print(f"Monster HP : {monster_hp}, Monster Damage Range : {monster_damage_range}")
        
    
    return player_hp, monster_hp, damage_range, monster_damage_range, time_limit

    
def mechanic_game(player_hp, monster_hp, damage_range, monster_damage_range, time_limit, combo_damage = 0):
    combo = 0
    while player_hp > 0 and monster_hp > 0:
        
        print("\nPlayer Hp : ", player_hp)
        print("Monster Hp : ", monster_hp)
        
        num1 = random.randint(10, 20)
        num2 = random.randint(1, 10)
        # operators = ['+','-']
        operators = ['+','-','*','%','^']
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
        elif operator == '%':
            correct_answer = num1 % num2
        elif operator == '^':
            correct_answer = num1 ** num2
            
        if answer == correct_answer and elapsed_time <= time_limit:
            combo += 1
            if elapsed_time <= 2:
                damage = random.randint(damage_range[0], damage_range[1]) * 2
                print(f"Combo {combo}")
                print(f"Correct! You deal CRITICAL HIT {damage} damage to the Monster.")
                print(f"Time taken: {elapsed_time:.2f} seconds")
            else:
                damage = random.randint(damage_range[0], damage_range[1])
                print(f"Combo {combo}")
                print(f"Correct! You deal {damage} damage to the Monster.")
                print(f"Time taken: {elapsed_time:.2f} seconds")
            if combo >= 2:
                combo_damage = damage * 2
                print(f"Combo {combo} - Bonus Damage {combo_damage}")
                
            monster_hp -= damage + combo_damage

        else: 
            combo = 0
            damage = random.randint(monster_damage_range[0], monster_damage_range[1])
            player_hp -= damage
            print(f"Combo Reset")
            print(f"Wrong! The Monster deals {damage} damage to you.")
            print(f"Time taken: {elapsed_time:.2f} seconds")
            
        save_game(player_hp, monster_hp, damage_range, monster_damage_range, time_limit)    
        
        
    if player_hp <= 0:
        print(f"You Lose! Monster's remaining HP is {monster_hp}")
    else:
        print(f"You Win! Your remaining HP is {player_hp}")

def save_game(player_hp, monster_hp, damage_range, monster_damage_range, time_limit):
    data = {
        "player_hp": player_hp,
        "monster_hp": monster_hp,
        "damage_range": damage_range,
        "monster_damage_range": monster_damage_range,
        "time_limit": time_limit
    }
    
    with open("savegame.json", "w") as file :
        json.dump(data, file)
        
    print("Game Saved!")

def load_game():
    if not os.path.exists("savegame.json"):
        print("No save file found!")
        return None

    with open("savegame.json", "r") as file:
        data = json.load(file)

    return (
        data["player_hp"],
        data["monster_hp"],
        tuple(data["damage_range"]),
        tuple(data["monster_damage_range"]),
        data["time_limit"]
    )

def menu():
    print("=== MATH BATTLE ===")
    print("1. New Game")
    print("2. Continue")

    choice = input("Choose: ")

    if choice == "1":
        return chara_difficulty()
    elif choice == "2":
        data = load_game()
        if data:
            print("Save loaded!")
            return data
        else:
            print("Starting new game...")
            return chara_difficulty()

def main():
    data = menu()

    player_hp, monster_hp, damage_range, monster_damage_range, time_limit = data

    mechanic_game(player_hp, monster_hp, damage_range, monster_damage_range, time_limit)

main()
