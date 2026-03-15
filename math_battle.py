import random
import time
import json
import os


# ══════════════════════════════════════════════════════════════════════════════
#  DATA CLASSES
# ══════════════════════════════════════════════════════════════════════════════

class Character:
    """Menyimpan data karakter pemain."""

    CHARACTERS = {
        1: ("Tanker",  200, (7,  12)),
        2: ("Fighter", 175, (10, 17)),
        3: ("Assasin", 75,  (20, 34)),
    }

    def __init__(self, choice: int):
        name, hp, dmg = self.CHARACTERS[choice]
        self.choice       = choice
        self.name         = name
        self.hp           = hp
        self.damage_range = dmg

    def __str__(self):
        return (f"{self.name}  |  HP: {self.hp}  |  "
                f"Damage: {self.damage_range[0]}-{self.damage_range[1]}")


class Monster:
    """Menyimpan data monster berdasarkan difficulty."""

    DIFFICULTIES = {
        1: ("Easy",    100, (7,  12)),
        2: ("Medium",  200, (10, 15)),
        3: ("Hard",    250, (13, 18)),
        4: ("Extreme", 450, (25, 70)),
    }

    def __init__(self, choice: int):
        name, hp, dmg     = self.DIFFICULTIES[choice]
        self.choice        = choice
        self.name          = name
        self.hp            = hp
        self.damage_range  = dmg

    def __str__(self):
        return (f"Monster HP : {self.hp}, "
                f"Monster Damage Range : {self.damage_range}")


# ══════════════════════════════════════════════════════════════════════════════
#  MATH QUESTION  (multiple-choice)
# ══════════════════════════════════════════════════════════════════════════════

class MathQuestion:
    """
    Membuat satu soal matematika dengan 4 pilihan jawaban (A-D).
    Jawaban yang salah dibuat 'tipis' bedanya dari jawaban benar.
    """

    OPERATORS = ['+', '-', '*', '%', '^']
    LABELS    = ['A', 'B', 'C', 'D']

    def __init__(self):
        self.num1     = random.randint(10, 20)
        self.num2     = random.randint(1, 10)
        self.operator = random.choice(self.OPERATORS)
        self.answer   = self._compute()
        self.choices, self.correct_label = self._make_choices()

    def _compute(self) -> float:
        ops = {
            '+': self.num1 + self.num2,
            '-': self.num1 - self.num2,
            '*': self.num1 * self.num2,
            '%': self.num1 % self.num2,
            '^': self.num1 ** self.num2,
        }
        return ops[self.operator]

    def _make_choices(self) -> tuple:
        """
        Buat 3 decoy yang mirip dengan jawaban benar.
        - Untuk ^ (hasil bisa besar): decoy ±5-15% dari jawaban
        - Untuk operator lain       : decoy ±1-5 dari jawaban
        """
        correct = self.answer
        decoys  = set()

        attempt = 0
        while len(decoys) < 3 and attempt < 200:
            attempt += 1
            if self.operator == '^':
                delta = random.randint(1, max(1, int(abs(correct) * 0.15)))
            else:
                delta = random.randint(1, 5)

            candidate = correct + random.choice([-1, 1]) * delta
            if candidate != correct:
                decoys.add(candidate)

        options = list(decoys) + [correct]
        random.shuffle(options)

        choices = {label: val for label, val in zip(self.LABELS, options)}
        correct_label = next(k for k, v in choices.items() if v == correct)
        return choices, correct_label

    def display(self):
        """Tampilkan soal dan pilihan."""
        print(f"\nSoal: {self.num1} {self.operator} {self.num2} ?")
        for label, val in self.choices.items():
            print(f"  {label}. {val}")

    def ask(self) -> tuple:
        """Terima input pilihan (A/B/C/D) + catat waktu. Kembalikan (label, elapsed)."""
        self.display()
        start = time.time()
        while True:
            raw = input("Your Answer (A/B/C/D) : ").strip().upper()
            if raw in self.LABELS:
                elapsed = time.time() - start
                return raw, elapsed
            print("Pilihan tidak valid! Masukkan A, B, C, atau D.")

    def is_correct(self, label: str) -> bool:
        return label == self.correct_label


# ══════════════════════════════════════════════════════════════════════════════
#  SAVE MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class SaveManager:
    """Simpan/load seluruh state permainan (termasuk karakter & options)."""

    FILE = "savegame.json"

    @staticmethod
    def save_profile(char_choice: int, time_limit: int, diff_choice: int):
        """Simpan pilihan karakter + options."""
        data = SaveManager._load_raw() or {}
        data.update({
            "char_choice": char_choice,
            "time_limit":  time_limit,
            "diff_choice": diff_choice,
        })
        SaveManager._write(data)

    @staticmethod
    def save_battle(player_hp: int, monster_hp: int,
                    damage_range: tuple, monster_damage_range: tuple,
                    time_limit: int):
        """Simpan state di tengah battle."""
        data = SaveManager._load_raw() or {}
        data.update({
            "player_hp":            player_hp,
            "monster_hp":           monster_hp,
            "damage_range":         list(damage_range),
            "monster_damage_range": list(monster_damage_range),
            "time_limit":           time_limit,
            "in_battle":            True,
        })
        SaveManager._write(data)
        print("Game Saved!")

    @staticmethod
    def load_profile():
        data = SaveManager._load_raw()
        if data and "char_choice" in data:
            return data
        return None

    @staticmethod
    def load_battle():
        data = SaveManager._load_raw()
        if data and data.get("in_battle"):
            return (
                data["player_hp"],
                data["monster_hp"],
                tuple(data["damage_range"]),
                tuple(data["monster_damage_range"]),
                data["time_limit"],
            )
        return None

    @staticmethod
    def clear_battle():
        """Hapus flag in_battle setelah pertarungan selesai."""
        data = SaveManager._load_raw() or {}
        for key in ["in_battle", "player_hp", "monster_hp",
                    "damage_range", "monster_damage_range"]:
            data.pop(key, None)
        SaveManager._write(data)

    @staticmethod
    def _load_raw():
        if not os.path.exists(SaveManager.FILE):
            return None
        with open(SaveManager.FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def _write(data: dict):
        with open(SaveManager.FILE, "w") as f:
            json.dump(data, f, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
#  BATTLE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class BattleEngine:
    """Loop pertarungan utama dengan soal pilihan ganda."""

    def __init__(self, player_hp: int, monster_hp: int,
                 damage_range: tuple, monster_damage_range: tuple,
                 time_limit: int):
        self.player_hp            = player_hp
        self.monster_hp           = monster_hp
        self.damage_range         = damage_range
        self.monster_damage_range = monster_damage_range
        self.time_limit           = time_limit
        self.combo                = 0
        self.combo_damage         = 0

    def run(self):
        while self.player_hp > 0 and self.monster_hp > 0:
            print("\nPlayer HP :", self.player_hp)
            print("Monster HP:", self.monster_hp)

            question       = MathQuestion()
            label, elapsed = question.ask()

            if question.is_correct(label) and elapsed <= self.time_limit:
                self._handle_correct(elapsed)
            else:
                self._handle_wrong(elapsed)

            SaveManager.save_battle(
                self.player_hp, self.monster_hp,
                self.damage_range, self.monster_damage_range,
                self.time_limit,
            )

        self._print_result()
        SaveManager.clear_battle()

    def _handle_correct(self, elapsed: float):
        self.combo += 1

        if elapsed <= 2:
            damage = random.randint(*self.damage_range) * 2
            print(f"Combo {self.combo}")
            print(f"Correct! You deal CRITICAL HIT {damage} damage to the Monster.")
        else:
            damage = random.randint(*self.damage_range)
            print(f"Combo {self.combo}")
            print(f"Correct! You deal {damage} damage to the Monster.")

        print(f"Time taken: {elapsed:.2f} seconds")

        if self.combo >= 2:
            self.combo_damage = damage * 2
            print(f"Combo {self.combo} - Bonus Damage {self.combo_damage}")

        self.monster_hp -= damage + self.combo_damage

    def _handle_wrong(self, elapsed: float):
        self.combo        = 0
        self.combo_damage = 0
        damage            = random.randint(*self.monster_damage_range)
        self.player_hp   -= damage
        print("Combo Reset")
        print(f"Wrong! The Monster deals {damage} damage to you.")
        print(f"Time taken: {elapsed:.2f} seconds")

    def _print_result(self):
        if self.player_hp <= 0:
            print(f"\nYou Lose! Monster's remaining HP is {self.monster_hp}")
        else:
            print(f"\nYou Win! Your remaining HP is {self.player_hp}")


# ══════════════════════════════════════════════════════════════════════════════
#  GAME  (main menu + sub-menu)
# ══════════════════════════════════════════════════════════════════════════════

class Game:
    """
    Titik masuk utama.

    State yang di-persist:
      - char_choice  : int (1-3)  -> karakter tetap sampai user ganti sendiri
      - time_limit   : int (seconds)
      - diff_choice  : int (1-4)
    """

    TIMER_MAP = {1: 20, 2: 15, 3: 10}

    def __init__(self):
        profile = SaveManager.load_profile()
        if profile:
            self.char_choice = profile["char_choice"]
            self.time_limit  = profile["time_limit"]
            self.diff_choice = profile["diff_choice"]
        else:
            self.char_choice = None
            self.time_limit  = 20
            self.diff_choice = 1

    # ── main loop ─────────────────────────────────────────────────────────────

    def run(self):
        while True:
            self._print_main_menu()
            choice = input("Choose: ").strip()

            if choice == "1":
                self._start_game()
            elif choice == "2":
                self._character_select()
            elif choice == "3":
                self._options_menu()
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    # ── main menu ─────────────────────────────────────────────────────────────

    def _print_main_menu(self):
        char_info = self._current_char_info()
        diff_name = Monster.DIFFICULTIES[self.diff_choice][0]
        print("\n" + "="*40)
        print("          MATH BATTLE")
        print("="*40)
        print(f"  Character : {char_info}")
        print(f"  Difficulty: {diff_name}")
        print(f"  Timer     : {self.time_limit} seconds")
        print("-"*40)
        print("  1. Start Game")
        print("  2. Character Select")
        print("  3. Options")
        print("  4. Exit")
        print("="*40)

    def _current_char_info(self) -> str:
        if self.char_choice is None:
            return "Not selected"
        name, hp, dmg = Character.CHARACTERS[self.char_choice]
        return f"{name}  (HP:{hp}  DMG:{dmg[0]}-{dmg[1]})"

    # ── start game ────────────────────────────────────────────────────────────

    def _start_game(self):
        if self.char_choice is None:
            print("\n[!] Kamu belum memilih karakter! Silakan pilih dulu.")
            self._character_select()
            if self.char_choice is None:
                return

        battle_data = SaveManager.load_battle()
        if battle_data:
            print("\nDitemukan save battle yang belum selesai.")
            print("  1. Lanjutkan battle")
            print("  2. Mulai battle baru")
            c = input("Pilih: ").strip()
            if c == "1":
                player_hp, monster_hp, dmg_r, mon_dmg_r, tl = battle_data
                print("Battle dilanjutkan!")
                BattleEngine(player_hp, monster_hp, dmg_r, mon_dmg_r, tl).run()
                return

        char    = Character(self.char_choice)
        monster = Monster(self.diff_choice)
        print(f"\n--- Battle Start ---")
        print(f"Character : {char}")
        print(f"{monster}")
        print(f"Timer     : {self.time_limit} seconds")
        BattleEngine(
            char.hp, monster.hp,
            char.damage_range, monster.damage_range,
            self.time_limit,
        ).run()

    # ── character select ──────────────────────────────────────────────────────

    def _character_select(self):
        print("\n--- Character Select ---")
        for key, (name, hp, dmg) in Character.CHARACTERS.items():
            marker = "  <-- (active)" if key == self.char_choice else ""
            print(f"  {key}. {name:8s}  HP:{hp:>3}  DMG:{dmg[0]}-{dmg[1]}{marker}")
        print("  0. Back")

        while True:
            try:
                c = int(input("Choose Your Character : "))
                if c == 0:
                    return
                if c in Character.CHARACTERS:
                    self.char_choice = c
                    char = Character(c)
                    print(f"Character dipilih: {char}")
                    self._save_profile()
                    return
            except ValueError:
                pass
            print("Invalid choice. Please choose again.")

    # ── options ───────────────────────────────────────────────────────────────

    def _options_menu(self):
        while True:
            print("\n--- Options ---")
            print(f"  1. Timer      (sekarang: {self.time_limit} seconds)")
            diff_name = Monster.DIFFICULTIES[self.diff_choice][0]
            print(f"  2. Difficulty (sekarang: {diff_name})")
            print("  0. Back")
            c = input("Choose: ").strip()

            if c == "0":
                return
            elif c == "1":
                self._pick_timer()
            elif c == "2":
                self._pick_difficulty()
            else:
                print("Invalid choice.")

    def _pick_timer(self):
        print("\n  Timer")
        print("  1. 20 Seconds")
        print("  2. 15 Seconds")
        print("  3. 10 Seconds")
        while True:
            try:
                t = int(input("  Choose: "))
                if t in self.TIMER_MAP:
                    self.time_limit = self.TIMER_MAP[t]
                    print(f"  Timer diset ke {self.time_limit} seconds.")
                    self._save_profile()
                    return
            except ValueError:
                pass
            print("  Invalid choice.")

    def _pick_difficulty(self):
        print("\n  Difficulty")
        for key, (name, hp, dmg) in Monster.DIFFICULTIES.items():
            marker = "  <-- (active)" if key == self.diff_choice else ""
            print(f"  {key}. {name:8s}  HP:{hp:>3}  DMG:{dmg[0]}-{dmg[1]}{marker}")
        while True:
            try:
                d = int(input("  Choose: "))
                if d in Monster.DIFFICULTIES:
                    self.diff_choice = d
                    print(f"  Difficulty diset ke {Monster.DIFFICULTIES[d][0]}.")
                    self._save_profile()
                    return
            except ValueError:
                pass
            print("  Invalid choice.")

    # ── helper ────────────────────────────────────────────────────────────────

    def _save_profile(self):
        if self.char_choice is not None:
            SaveManager.save_profile(self.char_choice, self.time_limit, self.diff_choice)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    Game().run()