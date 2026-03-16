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
#  MATH QUESTION  (multiple-choice, difficulty-aware, integer results)
# ══════════════════════════════════════════════════════════════════════════════

class MathQuestion:
    """
    Membuat soal multi-operasi berdasarkan difficulty, hasil selalu bilangan bulat.

    Difficulty  | Operasi                        | Jumlah operasi | Range angka
    ------------|--------------------------------|----------------|------------
    Easy   (1)  | + -                            | 3-4            | 10-99
    Medium (2)  | + - *                          | 3-4            | 10-99
    Hard   (3)  | * / ^                          | 2-3            | 10-99
    Extreme(4)  | * / ^ %                        | 3-4            | 10-99

    Strategi integer-safe:
    - Pembagian  : generate pembagi dulu, kalikan ke akumulator agar habis dibagi
    - Sisa bagi  : pastikan num % div != 0 agar hasilnya tidak trivial (0)
    - Pangkat    : basis 2-9, eksponen 2-3 agar hasil tidak meledak
    """

    LABELS = ['A', 'B', 'C', 'D']

    # Konfigurasi per difficulty: (operator_pool, min_ops, max_ops)
    DIFF_CONFIG = {
        1: (['+', '-'],           3, 4),
        2: (['+', '-', '*'],      3, 4),
        3: (['*', '/', '^'],      2, 3),
        4: (['*', '/', '^', '%'], 3, 4),
    }

    def __init__(self, diff: int = 1):
        self.diff = diff
        self.expression, self.answer = self._build_expression()
        self.choices, self.correct_label = self._make_choices()

    # ── expression builder ────────────────────────────────────────────────────

    def _rand_num(self) -> int:
        """Angka 2-3 digit: 10-99."""
        return random.randint(10, 99)

    def _build_expression(self) -> tuple:
        """
        Buat ekspresi multi-operasi yang hasilnya pasti integer non-negatif.
        Kembalikan (string_soal, jawaban_int).
        Jika hasil terlalu besar (> 10^9), generate ulang (max 30x).
        """
        ops_pool, min_ops, max_ops = self.DIFF_CONFIG[self.diff]
        n_ops = random.randint(min_ops, max_ops)

        for _ in range(30):
            operators = [random.choice(ops_pool) for _ in range(n_ops)]
            numbers   = self._safe_numbers(operators)

            result = numbers[0]
            for i, op in enumerate(operators):
                result = self._apply(result, op, numbers[i + 1])

            # Tolak jika hasil negatif, nol, atau terlalu besar
            if result <= 0 or result > 10_000_000:
                continue

            display_ops = {'*': '*', '/': '/', '^': '**', '+': '+', '-': '-', '%': '%'}
            parts = [str(numbers[0])]
            for i, op in enumerate(operators):
                parts.append(op if op != '^' else '**')
                parts.append(str(numbers[i + 1]))
            return ' '.join(parts), int(result)

        # Fallback: soal sederhana 2 angka jika terus gagal
        a, b = random.randint(10, 99), random.randint(10, 99)
        op = random.choice(['+', '-'])
        if op == '-' and b > a:
            a, b = b, a
        return f"{a} {op} {b}", self._apply(a, op, b)

    def _safe_numbers(self, operators: list) -> list:
        """
        Generate daftar angka agar setiap operasi menghasilkan integer non-negatif.
        Evaluasi kiri ke kanan:  acc  op[i]  num[i+1]
        """
        acc = self._rand_num()
        numbers = [acc]

        for op in operators:
            if op == '/':
                # Pastikan acc cukup besar untuk dibagi
                if acc < 2:
                    acc = random.randint(10, 99)
                    numbers[-1] = acc
                divisor = random.randint(2, min(9, acc))
                acc = acc * divisor
                numbers[-1] = acc
                numbers.append(divisor)
                acc = acc // divisor

            elif op == '^':
                # Reset ke basis kecil agar tidak overflow
                base = random.randint(2, 12)
                exp  = random.randint(2, 3)
                numbers[-1] = base
                acc = base
                numbers.append(exp)
                acc = acc ** exp

            elif op == '%':
                # Pastikan acc >= 2 agar ada sisa yang bermakna
                if acc < 2:
                    acc = random.randint(10, 99)
                    numbers[-1] = acc
                # Pilih pembagi yang tidak habis membagi dan tidak 0
                for _ in range(50):
                    divisor = random.randint(2, min(9, max(2, acc - 1)))
                    if acc % divisor != 0:
                        break
                else:
                    divisor = 2
                    acc += 1          # paksa ada sisa
                    numbers[-1] = acc
                numbers.append(divisor)
                acc = acc % divisor

            else:  # + atau -
                if op == '-':
                    max_sub = max(1, acc - 1)
                    b = random.randint(1, min(max_sub, 99))
                else:
                    b = self._rand_num()
                numbers.append(b)
                acc = self._apply(acc, op, b)

        return numbers

    @staticmethod
    def _apply(a, op: str, b) -> int:
        if op == '+':  return a + b
        if op == '-':  return a - b
        if op == '*':  return a * b
        if op == '/':  return a // b
        if op == '^':  return a ** b
        if op == '%':  return a % b

    # ── decoy generator ───────────────────────────────────────────────────────

    def _make_choices(self) -> tuple:
        """
        Buat 3 decoy yang 'tipis' bedanya:
        - Jawaban kecil  (<= 100) : delta ±1-8
        - Jawaban sedang (101-999): delta ±5-30
        - Jawaban besar  (>= 1000): delta ±1-5% dari jawaban (integer)
        Jika jawaban terlalu besar untuk float (>10^15), pakai persentase integer murni.
        """
        correct = self.answer
        decoys  = set()

        for _ in range(500):
            abs_correct = abs(correct)
            if abs_correct <= 100:
                delta = random.randint(1, 8)
            elif abs_correct <= 999:
                delta = random.randint(5, 30)
            else:
                pct = random.randint(1, 5)
                delta = max(1, abs_correct * pct // 100)  # integer arithmetic, no float

            candidate = correct + random.choice([-1, 1]) * delta
            if candidate != correct:
                decoys.add(candidate)
            if len(decoys) == 3:
                break

        options = list(decoys)[:3] + [correct]
        random.shuffle(options)

        choices = {label: val for label, val in zip(self.LABELS, options)}
        correct_label = next(k for k, v in choices.items() if v == correct)
        return choices, correct_label

    # ── display / input ───────────────────────────────────────────────────────

    def display(self):
        print(f"\nSoal: {self.expression} = ?")
        for label, val in self.choices.items():
            print(f"  {label}. {val}")

    def ask(self) -> tuple:
        """Kembalikan (label_dipilih, elapsed_seconds)."""
        self.display()
        start = time.time()
        while True:
            raw = input("Your Answer (A/B/C/D) : ").strip().upper()
            if raw in self.LABELS:
                return raw, time.time() - start
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
                 time_limit: int, diff: int = 1):
        self.player_hp            = player_hp
        self.monster_hp           = monster_hp
        self.damage_range         = damage_range
        self.monster_damage_range = monster_damage_range
        self.time_limit           = time_limit
        self.diff                 = diff
        self.combo                = 0
        self.combo_damage         = 0

    def run(self):
        while self.player_hp > 0 and self.monster_hp > 0:
            print("\nPlayer HP :", self.player_hp)
            print("Monster HP:", self.monster_hp)

            question       = MathQuestion(self.diff)
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
                BattleEngine(player_hp, monster_hp, dmg_r, mon_dmg_r, tl,
                             self.diff_choice).run()
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
            self.diff_choice,
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