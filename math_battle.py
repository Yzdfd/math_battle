import random
import time
import json
import os
from enum import Enum


# ══════════════════════════════════════════════════════════════════════════════
#  ENUMS
# ══════════════════════════════════════════════════════════════════════════════

class GameMode(Enum):
    STAGE   = "stage"
    ENDLESS = "endless"


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
    """
    Menyimpan data monster.
    Mode Stage  : stat monster di-scale per level (1-10).
    Mode Endless: stat monster di-scale per wave.
    """

    DIFFICULTIES = {
        1: ("Easy",    100, (7,  12)),
        2: ("Medium",  200, (10, 15)),
        3: ("Hard",    250, (13, 18)),
        4: ("Extreme", 450, (25, 70)),
    }

    def __init__(self, diff: int, level: int = 1):
        """
        level : nomor level (1-10) untuk Stage, atau nomor wave untuk Endless.
                Dipakai untuk scaling HP dan damage monster.
        """
        name, base_hp, base_dmg = self.DIFFICULTIES[diff]
        self.name  = name
        self.level = level

        # Scaling: setiap level/wave nambah 10% HP dan 1 flat damage
        scale      = 1 + (level - 1) * 0.10
        self.hp            = int(base_hp  * scale)
        self.damage_range  = (
            base_dmg[0] + (level - 1),
            base_dmg[1] + (level - 1),
        )

    def __str__(self):
        return (f"Monster HP : {self.hp}, "
                f"Monster Damage Range : {self.damage_range}")


# ══════════════════════════════════════════════════════════════════════════════
#  MATH QUESTION  (multiple-choice, difficulty-aware, integer results)
# ══════════════════════════════════════════════════════════════════════════════

class MathQuestion:
    LABELS = ['A', 'B', 'C', 'D']

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

    def _rand_num(self) -> int:
        return random.randint(10, 99)

    def _build_expression(self) -> tuple:
        ops_pool, min_ops, max_ops = self.DIFF_CONFIG[self.diff]
        n_ops = random.randint(min_ops, max_ops)

        for _ in range(30):
            operators = [random.choice(ops_pool) for _ in range(n_ops)]
            numbers   = self._safe_numbers(operators)
            result    = numbers[0]
            for i, op in enumerate(operators):
                result = self._apply(result, op, numbers[i + 1])
            if result <= 0 or result > 10_000_000:
                continue
            parts = [str(numbers[0])]
            for i, op in enumerate(operators):
                parts.append(op if op != '^' else '**')
                parts.append(str(numbers[i + 1]))
            return ' '.join(parts), int(result)

        a, b = random.randint(10, 99), random.randint(10, 99)
        op = random.choice(['+', '-'])
        if op == '-' and b > a:
            a, b = b, a
        return f"{a} {op} {b}", self._apply(a, op, b)

    def _safe_numbers(self, operators: list) -> list:
        acc = self._rand_num()
        numbers = [acc]
        for op in operators:
            if op == '/':
                if acc < 2:
                    acc = random.randint(10, 99)
                    numbers[-1] = acc
                divisor = random.randint(2, min(9, acc))
                acc = acc * divisor
                numbers[-1] = acc
                numbers.append(divisor)
                acc = acc // divisor
            elif op == '^':
                base = random.randint(2, 12)
                exp  = random.randint(2, 3)
                numbers[-1] = base
                acc = base
                numbers.append(exp)
                acc = acc ** exp
            elif op == '%':
                if acc < 2:
                    acc = random.randint(10, 99)
                    numbers[-1] = acc
                for _ in range(50):
                    divisor = random.randint(2, min(9, max(2, acc - 1)))
                    if acc % divisor != 0:
                        break
                else:
                    divisor = 2
                    acc += 1
                    numbers[-1] = acc
                numbers.append(divisor)
                acc = acc % divisor
            else:
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

    def _make_choices(self) -> tuple:
        correct = self.answer
        decoys  = set()
        for _ in range(500):
            abs_c = abs(correct)
            if abs_c <= 100:
                delta = random.randint(1, 8)
            elif abs_c <= 999:
                delta = random.randint(5, 30)
            else:
                delta = max(1, abs_c * random.randint(1, 5) // 100)
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

    def display(self):
        print(f"\nSoal: {self.expression} = ?")
        for label, val in self.choices.items():
            print(f"  {label}. {val}")

    def ask(self) -> tuple:
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
#  BATTLE RESULT  — data class kembalian BattleEngine
# ══════════════════════════════════════════════════════════════════════════════

class BattleResult:
    def __init__(self, won: bool, player_hp_left: int,
                 took_damage: bool, duration: float, score: int = 0):
        self.won           = won
        self.player_hp_left = player_hp_left
        self.took_damage   = not took_damage   # True = NO damage taken
        self.no_damage     = not took_damage
        self.duration      = duration          # detik total pertarungan
        self.score         = score


# ══════════════════════════════════════════════════════════════════════════════
#  BATTLE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class BattleEngine:
    """Loop pertarungan utama. Kembalikan BattleResult setelah selesai."""

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
        self._took_damage         = False
        self._score               = 0

    def run(self) -> BattleResult:
        start_time = time.time()

        while self.player_hp > 0 and self.monster_hp > 0:
            print("\nPlayer HP :", self.player_hp)
            print("Monster HP:", self.monster_hp)

            question       = MathQuestion(self.diff)
            label, elapsed = question.ask()

            if question.is_correct(label) and elapsed <= self.time_limit:
                self._handle_correct(elapsed)
            else:
                self._handle_wrong(elapsed)

        duration = time.time() - start_time
        won      = self.player_hp > 0

        if won:
            print(f"\nYou Win! Your remaining HP is {self.player_hp}")
        else:
            print(f"\nYou Lose! Monster's remaining HP is {self.monster_hp}")

        return BattleResult(
            won            = won,
            player_hp_left = max(0, self.player_hp),
            took_damage    = self._took_damage,
            duration       = duration,
            score          = self._score,
        )

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
        self._score     += damage + self.combo_damage + (self.combo * 10)

    def _handle_wrong(self, elapsed: float):
        self.combo        = 0
        self.combo_damage = 0
        damage            = random.randint(*self.monster_damage_range)
        self.player_hp   -= damage
        self._took_damage = True
        print("Combo Reset")
        print(f"Wrong! The Monster deals {damage} damage to you.")
        print(f"Time taken: {elapsed:.2f} seconds")


# ══════════════════════════════════════════════════════════════════════════════
#  SAVE MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class SaveManager:
    FILE = "savegame.json"

    # ── profile (karakter + settings) ────────────────────────────────────────

    @staticmethod
    def save_profile(char_choice: int, time_limit: int, diff_choice: int):
        data = SaveManager._load_raw() or {}
        data.update({
            "char_choice": char_choice,
            "time_limit":  time_limit,
            "diff_choice": diff_choice,
        })
        SaveManager._write(data)

    @staticmethod
    def load_profile():
        data = SaveManager._load_raw()
        if data and "char_choice" in data:
            return data
        return None

    # ── stage stars ───────────────────────────────────────────────────────────
    # Disimpan per key  "stars_{diff}_{level}"  → int 0-3

    @staticmethod
    def get_stars(diff: int, level: int) -> int:
        data = SaveManager._load_raw() or {}
        return data.get(f"stars_{diff}_{level}", 0)

    @staticmethod
    def set_stars(diff: int, level: int, stars: int):
        """Simpan bintang hanya jika lebih baik dari yang tersimpan."""
        data    = SaveManager._load_raw() or {}
        key     = f"stars_{diff}_{level}"
        current = data.get(key, 0)
        if stars > current:
            data[key] = stars
            SaveManager._write(data)

    # ── endless highscore ─────────────────────────────────────────────────────
    # Disimpan per key  "hs_{diff}"  → int

    @staticmethod
    def get_highscore(diff: int) -> int:
        data = SaveManager._load_raw() or {}
        return data.get(f"hs_{diff}", 0)

    @staticmethod
    def set_highscore(diff: int, score: int):
        data    = SaveManager._load_raw() or {}
        key     = f"hs_{diff}"
        current = data.get(key, 0)
        if score > current:
            data[key] = score
            SaveManager._write(data)

    # ── internal ──────────────────────────────────────────────────────────────

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
#  STAGE MANAGER  (level 1 – 10)
# ══════════════════════════════════════════════════════════════════════════════

class StageManager:
    """
    Mengelola sesi Stage Mode.

    Level 1-10, tiap level monster di-scale.
    Bintang per level:
      ★☆☆  = menang (selalu dapat ini kalau menang)
      ★★☆  = menang tanpa kena damage sama sekali
      ★★★  = menang dalam waktu < 70 detik
      (bintang ATAU, bukan AND — ambil yang terbaik per attempt,
       lalu OR dengan yang tersimpan agar bintang tidak hilang)
    """

    MAX_LEVEL  = 10
    STAR_TIME  = 70.0   # detik untuk bintang ke-3

    def __init__(self, char_choice: int, diff: int, time_limit: int):
        self.char_choice = char_choice
        self.diff        = diff
        self.time_limit  = time_limit

    def run(self):
        print("\n" + "="*40)
        print("        STAGE MODE")
        print("="*40)
        self._print_stage_map()

        level = self._pick_level()
        if level is None:
            return

        while True:
            result = self._play_level(level)
            if not result.won:
                print("\n[STAGE] Kamu kalah. Mau coba lagi?")
                print("  1. Ulangi level ini")
                print("  0. Kembali ke menu")
                c = input("  Pilih: ").strip()
                if c == "1":
                    continue
                return
            else:
                # Hitung bintang attempt ini
                new_stars = self._calc_stars(result)
                self._show_stars(level, new_stars)

                # Merge dengan bintang tersimpan (OR per posisi bintang)
                saved    = SaveManager.get_stars(self.diff, level)
                merged   = self._merge_stars(saved, new_stars)
                SaveManager.set_stars(self.diff, level, merged)

                if level < self.MAX_LEVEL:
                    print(f"\nLevel {level} selesai!")
                    print("  1. Lanjut ke level berikutnya")
                    print("  2. Pilih level lain")
                    print("  0. Kembali ke menu")
                    c = input("  Pilih: ").strip()
                    if c == "1":
                        level += 1
                        continue
                    elif c == "2":
                        self._print_stage_map()
                        level = self._pick_level()
                        if level is None:
                            return
                        continue
                    else:
                        return
                else:
                    print("\nSelamat! Kamu telah menyelesaikan semua 10 level!")
                    return

    # ── level select ──────────────────────────────────────────────────────────

    def _print_stage_map(self):
        diff_name = Monster.DIFFICULTIES[self.diff][0]
        print(f"\n  Difficulty: {diff_name}")
        print("  Level  Stars")
        print("  " + "-"*22)
        for lv in range(1, self.MAX_LEVEL + 1):
            stars  = SaveManager.get_stars(self.diff, lv)
            filled = "★" * stars + "☆" * (3 - stars)
            print(f"   {lv:>2}.   {filled}")
        print()

    def _pick_level(self):
        while True:
            try:
                raw = input("  Pilih level (1-10) atau 0 untuk kembali: ").strip()
                n   = int(raw)
                if n == 0:
                    return None
                if 1 <= n <= self.MAX_LEVEL:
                    return n
            except ValueError:
                pass
            print("  Input tidak valid.")

    # ── satu level ────────────────────────────────────────────────────────────

    def _play_level(self, level: int) -> BattleResult:
        char    = Character(self.char_choice)
        monster = Monster(self.diff, level)
        print(f"\n--- Level {level} ---")
        print(f"Character : {char}")
        print(f"{monster}")
        print(f"Timer     : {self.time_limit} seconds")

        engine = BattleEngine(
            char.hp, monster.hp,
            char.damage_range, monster.damage_range,
            self.time_limit, self.diff,
        )
        return engine.run()

    # ── bintang ───────────────────────────────────────────────────────────────

    @staticmethod
    def _calc_stars(result: BattleResult) -> int:
        """
        Hitung bintang dari satu attempt:
          3 = menang < 70 detik
          2 = menang tanpa kena damage
          1 = menang
          0 = kalah
        """
        if not result.won:
            return 0
        if result.duration < StageManager.STAR_TIME:
            return 3
        if result.no_damage:
            return 2
        return 1

    @staticmethod
    def _merge_stars(saved: int, new: int) -> int:
        """
        Gabungkan bintang lama dan baru secara OR per posisi:
        Misal saved=1 (hanya ★☆☆) dan new=2 (★★☆) → merged=2 (★★☆)
        Misal saved=2 (★★☆) dan new=1 (★☆☆)       → merged=2 (tetap ★★☆)
        Misal saved=1 dan new=3                    → merged=3
        Karena bintang bersifat kumulatif (1 ⊂ 2 ⊂ 3), cukup ambil max.
        Tapi sesuai permintaan: "beda letak bintangnya bakal jadi 1"
        artinya bintang ★☆★ bisa ada → kita track per-bit (3 bit).
        """
        # Encode bintang ke bitmask:
        # bit0 = bintang 1 (menang)
        # bit1 = bintang 2 (no damage)
        # bit2 = bintang 3 (< 70 detik)
        def to_bits(s: int) -> int:
            if s >= 1: bits = 0b001
            else:      return 0
            if s >= 2: bits |= 0b010
            if s >= 3: bits |= 0b100
            return bits

        def count_bits(b: int) -> int:
            return bin(b).count('1')

        saved_bits = to_bits(saved)
        new_bits   = to_bits(new)
        merged_bits = saved_bits | new_bits
        return count_bits(merged_bits)

    @staticmethod
    def _show_stars(level: int, stars: int):
        filled = "★" * stars + "☆" * (3 - stars)
        print(f"\n  Level {level} — Bintang kamu: {filled}")
        if stars == 3:
            print("  Luar biasa! Menang dalam waktu kurang dari 70 detik!")
        elif stars == 2:
            print("  Bagus! Menang tanpa kena damage!")
        elif stars == 1:
            print("  Menang!")


# ══════════════════════════════════════════════════════════════════════════════
#  ENDLESS MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class EndlessManager:
    """
    Mengelola sesi Endless Mode.

    Tiap wave monster lebih kuat. Score bertambah per wave.
    Highscore tersimpan per difficulty.
    """

    SCORE_PER_WAVE = 100   # bonus score flat per wave selesai

    def __init__(self, char_choice: int, diff: int, time_limit: int):
        self.char_choice = char_choice
        self.diff        = diff
        self.time_limit  = time_limit

    def run(self):
        print("\n" + "="*40)
        print("       ENDLESS MODE")
        print("="*40)
        hs = SaveManager.get_highscore(self.diff)
        diff_name = Monster.DIFFICULTIES[self.diff][0]
        print(f"  Difficulty : {diff_name}")
        print(f"  Highscore  : {hs}")
        print()

        wave        = 1
        total_score = 0
        # HP player tidak reset antar wave — terus berlanjut
        char        = Character(self.char_choice)
        player_hp   = char.hp

        while True:
            print(f"\n  === Wave {wave} ===")
            monster = Monster(self.diff, wave)
            print(f"  {monster}")
            print(f"  Score saat ini: {total_score}")

            engine = BattleEngine(
                player_hp, monster.hp,
                char.damage_range, monster.damage_range,
                self.time_limit, self.diff,
            )
            result = engine.run()

            if not result.won:
                print(f"\n[ENDLESS] Game Over pada Wave {wave}!")
                print(f"  Total Score : {total_score}")
                hs = SaveManager.get_highscore(self.diff)
                if total_score > hs:
                    print(f"  NEW HIGHSCORE! {total_score}")
                    SaveManager.set_highscore(self.diff, total_score)
                else:
                    print(f"  Highscore   : {hs}")
                return

            # Update score dan HP player
            wave_score   = result.score + self.SCORE_PER_WAVE * wave
            total_score += wave_score
            player_hp    = result.player_hp_left

            print(f"\n  Wave {wave} selesai!")
            print(f"  Score wave  : +{wave_score}")
            print(f"  Total score : {total_score}")
            print(f"  Player HP   : {player_hp}")

            wave += 1


# ══════════════════════════════════════════════════════════════════════════════
#  GAME  (main menu + sub-menu)
# ══════════════════════════════════════════════════════════════════════════════

class Game:
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
            if   choice == "1": self._mode_select()
            elif choice == "2": self._character_select()
            elif choice == "3": self._options_menu()
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    # ── main menu ─────────────────────────────────────────────────────────────

    def _print_main_menu(self):
        char_info = self._current_char_info()
        diff_name = Monster.DIFFICULTIES[self.diff_choice][0]
        hs        = SaveManager.get_highscore(self.diff_choice)

        print("\n" + "="*40)
        print("          MATH BATTLE")
        print("="*40)
        print(f"  Character  : {char_info}")
        print(f"  Difficulty : {diff_name}")
        print(f"  Timer      : {self.time_limit} seconds")
        print(f"  Endless HS : {hs}")
        print("-"*40)
        print("  1. Play")
        print("  2. Character Select")
        print("  3. Options")
        print("  4. Exit")
        print("="*40)

    def _current_char_info(self) -> str:
        if self.char_choice is None:
            return "Not selected"
        name, hp, dmg = Character.CHARACTERS[self.char_choice]
        return f"{name}  (HP:{hp}  DMG:{dmg[0]}-{dmg[1]})"

    # ── mode select ───────────────────────────────────────────────────────────

    def _mode_select(self):
        if self.char_choice is None:
            print("\n[!] Kamu belum memilih karakter!")
            self._character_select()
            if self.char_choice is None:
                return

        print("\n--- Pilih Mode ---")
        print("  1. Stage Mode  (Level 1-10, dapat bintang)")
        print("  2. Endless Mode (Berapa lama kamu bertahan?)")
        print("  0. Back")
        c = input("  Pilih: ").strip()

        if c == "1":
            StageManager(
                self.char_choice, self.diff_choice, self.time_limit
            ).run()
        elif c == "2":
            EndlessManager(
                self.char_choice, self.diff_choice, self.time_limit
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
                    print(f"Character dipilih: {Character(c)}")
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
            if   c == "0": return
            elif c == "1": self._pick_timer()
            elif c == "2": self._pick_difficulty()
            else:          print("Invalid choice.")

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
            SaveManager.save_profile(
                self.char_choice, self.time_limit, self.diff_choice
            )


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    Game().run()