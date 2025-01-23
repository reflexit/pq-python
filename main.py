import time
import datetime
import os
import random
import collections
import pickle

from constants import *


class Player:
    def __init__(self):
        # stats
        self.state = "kill"
        self.level = 1
        self.exp = 0
        self.exp_needed = self.level_up_time(1)
        self.stats = self.roll()
        self.HP = max(1, random.randrange(8) + self.stats[1] // 6)
        self.MP = max(1, random.randrange(8) + self.stats[3] // 6)

        # inventory
        self.gold = 0
        self.equips = [("Sharp Stick", 0)] + [("", 0)] * 10
        self.spells = collections.Counter()
        self.items = collections.Counter()

        # act
        self.act = 1
        self.act_time = 60 * 60 * 6
        self.act_progress = 0
        self.act_caption = "Act I"

        # quest
        self.quest_progress = 0
        self.quest_caption = ""

        # debug only
        self.cheat = False

    def roll(self):
        while True:
            res = []
            for _ in range(6):
                res.append(3 + random.randrange(6) + random.randrange(6) + random.randrange(6))
            print("STR {:d}, CON {:d}, DEX {:d}, INT {:d}, WIS {:d}, CHA {:d}".format(*res))
            ans = input("Go? (Y/N) ")
            if ans == "Y" or ans == "y":
                return res

    def new_game(self):
        self.char_sheet()
        self.print_log("Loading...", 2)
        self.print_log("Experiencing an enigmatic and foreboding night vision...", 10)
        self.print_log("Much is revealed about that wise old bastard you'd underestimated...", 6)
        self.print_log("A shocking series of events leaves you alone and bewildered, but resolute...", 6)
        self.print_log("Drawing upon an unexpected reserve of determination, you set out on a long and dangerous journey...", 4)
        self.print_log("Loading " + self.act_caption + "...", 2)
        self.new_quest()
        self.save_game()
        self.dispatch()

    def dispatch(self):
        while True:
            if self.state == "sell":
                self.print_log("Heading to market to sell loot...", 4)
                for item in list(self.items):
                    self.print_log("Selling " + str(self.items[item]) + " " + item + "...", 1)
                    price = self.items[item] * self.level
                    if " of " in item:
                        price *= (1 + random.randrange(10)) * (1 + random.randrange(self.level))
                    self.gold += price
                    del self.items[item]

                if self.gold >= self.equip_price():
                    self.state = "buy"
                else:
                    self.state = "kill"
            elif self.state == "buy":
                self.print_log("Negotiating purchase of better equipment...", 5)
                self.gold -= self.equip_price()
                self.win_equip()

                if self.gold >= self.equip_price():
                    self.state = "buy"
                else:
                    self.state = "kill"
            elif self.state == "kill":
                # special case where the inventory is full after loading game
                if sum(self.items.values()) >= self.stats[0] + 10:
                    self.state = "sell"
                    continue

                self.print_log("Heading to the killing fields...", 4)
                while sum(self.items.values()) < self.stats[0] + 10:
                    name, orig_name, lev, loot, qty = self.monster_task()
                    if lev > self.level + 5:
                        exp = 7
                    elif lev < self.level - 5:
                        exp = 5
                    else:
                        exp = 6
                    if qty > 1:
                        self.print_log("Executing " + str(qty) + " " + name + "...", exp)
                    else:
                        self.print_log("Executing " + name + "...", exp)
                    if loot == "*":
                        self.win_item()
                    else:
                        self.items[orig_name + " " + loot] += 1

                    self.exp += exp
                    if self.exp >= self.exp_needed:
                        self.level_up()

                    self.act_progress += exp
                    if self.act_progress >= self.act_time:
                        self.complete_act()

                    self.quest_progress += exp
                    if self.quest_progress >= 100:
                        self.complete_quest()

                self.state = "sell"

    def monster_task(self):
        # decide target monster level
        level = self.level
        for i in range(self.level):
            if random.random() < 0.4:
                if random.random() < 0.5:
                    level += 1
                else:
                    level -= 1
        if level < 1:
            level = 1

        # choose monster
        if random.random() < 0.04:  # use an NPC every once in a while
            monster = " " + random.choice(RACES)
            if random.random() < 0.5:
                monster = "passing" + monster + " " + random.choice(KLASSES)
            else:
                monster = random.choice(TITLES) + " " + self.generate_name() + " the" + monster
            lev = level
            monster = (monster, level, "*")
        else:   # pick the monster out of so many random ones closest to the level we want
            monster = random.choice(MONSTERS)
            lev = monster[1]
            for i in range(5):
                m1 = random.choice(MONSTERS)
                if abs(level - m1[1]) < abs(level - lev):
                    monster = m1
                    lev = monster[1]

        # decide monster quantity
        qty = 1
        if level - lev > 10:
            # lev is too low. multiply...
            qty = (level + random.randrange(max(lev, 1))) // max(lev, 1)
            if qty < 1:
                qty = 1
            level = level // qty

        # add modifiers
        name = monster[0]
        if level - lev <= -10:
            name = "imaginary " + name
        elif level - lev < -5:
            i = 10 + (level - lev)
            i = 5 - random.randrange(i + 1)
            name = self.sick(i, self.young((lev - level) - i, name))
        elif level - lev < 0 and random.random() < 0.5:
            name = self.sick(level - lev, name)
        elif level - lev < 0:
            name = self.young(level - lev, name)
        elif level - lev >= 10:
            name = "messianic " + name
        elif level - lev > 5:
            i = 10 - (level - lev)
            i = 5 - random.randrange(i + 1)
            name = self.big(i, self.special((level - lev) - i, name))
        elif level - lev > 0 and random.random() < 0.5:
            name = self.big(level - lev, name)
        elif level - lev > 0:
            name = self.special(level - lev, name)

        # full name, original name, level, loot, quantity
        return name, monster[0], lev, monster[2], qty

    def complete_act(self):
        self.print_log(self.act_caption + " completed")
        self.act += 1
        self.act_time = 60 * 60 * (1 + 5 * self.act)    # 1 hr + 5 per act
        self.act_progress = 0
        self.act_caption = "Act " + self.int_to_roman(self.act)
        if self.act > 2:
            self.win_item()
        if self.act > 3:
            self.win_equip()
        self.char_sheet()
        self.save_game()
        self.interplot_cinematic()

    def complete_quest(self):
        self.print_log("Quest completed: " + self.quest_caption)
        reward = random.randrange(4)
        if reward == 0:
            self.win_spell()
        elif reward == 1:
            self.win_equip()
        elif reward == 2:
            self.win_stat()
        elif reward == 3:
            self.win_item()
        self.char_sheet()
        self.new_quest()
        self.save_game()

    def new_quest(self):
        self.quest_progress = 0
        quest_type = random.randrange(5)
        if quest_type == 0:
            for i in range(4):
                m = random.choice(MONSTERS)
                if i == 0 or abs(m[1] - self.level) < abs(level - self.level):
                    level = m[1]
                    monster = m
            self.quest_caption = "Exterminate " + monster[0]
        elif quest_type == 1:
            self.quest_caption = "Seek " + self.interesting_item()
        elif quest_type == 2:
            self.quest_caption = "Deliver this " + self.boring_item()
        elif quest_type == 3:
            self.quest_caption = "Fetch me " + self.boring_item()
        elif quest_type == 4:
            for i in range(2):
                m = random.choice(MONSTERS)
                if i == 0 or abs(m[1] - self.level) < abs(level - self.level):
                    level = m[1]
                    monster = m
            self.quest_caption = "Placate " + monster[0]
        self.print_log("New quest: " + self.quest_caption)

    def char_sheet(self):
        print("[CHARACTER SHEET]")
        print("Level {:d} ({:d}/{:d})".format(self.level, self.exp, self.exp_needed))
        print("STR {:d}, CON {:d}, DEX {:d}, INT {:d}, WIS {:d}, CHA {:d}".format(*self.stats))
        print("HP Max {:d}, MP Max {:d}".format(self.HP, self.MP))
        print("Plot Stage: {:s} ({:.2%})".format(self.act_caption, self.act_progress / self.act_time))
        print("Inventory: {:d}/{:d}    Gold: {:d}".format(sum(self.items.values()), self.stats[0] + 10, self.gold))
        print("Prized Item: {:s}".format(self.best_equip()))
        if self.spells:
            print("Specialty: {:s}".format(self.best_spells()))

    def interplot_cinematic(self):
        r = random.randrange(3)
        if r == 0:
            self.print_log("Exhausted, you arrive at a friendly oasis in a hostile land...", 1)
            self.print_log("You greet old friends and meet new allies...", 2)
            self.print_log("You are privy to a council of powerful do-gooders...", 2)
            self.print_log("There is much to be done. You are chosen!", 1)
        elif r == 1:
            self.print_log("Your quarry is in sight, but a mighty enemy bars your path!", 1)
            nemesis = self.named_monster(self.level + 3)
            self.print_log("A desperate struggle commences with " + nemesis + "...", 4)
            s = random.randrange(3)
            for _ in range(self.act):
                s += 1 + random.randrange(2)
                if s % 3 == 0:
                    self.print_log("Locked in grim combat with " + nemesis + "...", 2)
                elif s % 3 == 1:
                    self.print_log(nemesis + " seems to have the upper hand...", 2)
                else:
                    self.print_log("You seem to gain the advantage over " + nemesis + "...", 2)
            self.print_log("Victory! " + nemesis + " is slain! Exhausted, you lose conciousness...", 3)
            self.print_log("You awake in a friendly place, but the road awaits...", 2)
        else:
            nemesis = self.impressive_guy()
            self.print_log("Oh sweet relief! You've reached the kind protection of " + nemesis + "...", 2)
            self.print_log("There is rejoicing, and an unnerving encouter with " + nemesis + " in private...", 3)
            self.print_log("You forget your " + self.boring_item() + " and go back to get it...", 2)
            self.print_log("What's this!? You overhear something shocking!", 2)
            self.print_log("Could " + nemesis + " be a dirty double-dealer?", 2)
            self.print_log("Who can possibly be trusted with this news!? -- Oh yes, of course...", 3)
        self.print_log("Loading " + self.act_caption + "...", 2)

    def named_monster(self, level):
        lev = 0
        res = ""
        for i in range(5):
            m = random.choice(MONSTERS)
            if abs(level - m[1]) < abs(level - lev):
                res = m[0]
                lev = m[1]
        return self.generate_name() + " the " + res

    def impressive_guy(self):
        res = random.choice(IMPRESSIVE_TITLES)
        if random.random() < 0.5:
            res = "the " + res + " of the " + random.choice(RACES)
        else:
            res = res + " " + self.generate_name() + " of " + self.generate_name()
        return res

    def generate_name(self):
        res = ""
        for i in range(6):
            res += random.choice(NAME_PARTS[i % 3])
        res = res.capitalize()
        return res

    def level_up_time(self, level):
        # ~20 minutes for level 1, eventually dominated by exponential
        return round((20 + 1.15 ** level) * 60)

    def equip_price(self):
        return 5 * self.level * self.level + 10 * self.level + 20

    def level_up(self):
        self.level += 1
        self.HP += self.stats[1] // 3 + 1 + random.randrange(4)
        self.MP += self.stats[3] // 3 + 1 + random.randrange(4)
        for i in range(2):
            self.win_stat()
        self.win_spell()
        self.exp = 0
        self.exp_needed = self.level_up_time(self.level)
        self.char_sheet()
        self.save_game()

    def win_spell(self):
        stuff = SPELLS
        if self.stats[4] + self.level < len(stuff):
            stuff = stuff[:self.stats[4] + self.level]
        spell = random.choice(stuff)
        self.spells[spell] += 1
        self.print_log("Gained spell: " + spell)

    def win_equip(self):
        # determine equipment slot
        posn = random.randrange(len(self.equips))
        if posn == 0:
            stuff = WEAPONS
            better = OFFENSE_ATTRIB
            worse = OFFENSE_BAD
        else:
            better = DEFENSE_ATTRIB
            worse = DEFENSE_BAD
            if posn == 1:
                stuff = SHIELDS
            else:
                stuff = ARMORS

        # choose equipment
        if self.level < len(stuff):
            stuff = stuff[:self.level]
        name = random.choice(stuff)
        plus = self.level - name[1]
        name = name[0]
        if plus < 0:
            better = worse
        count = 0
        while count < 2 and plus != 0:
            modifier = random.choice(better)
            if modifier[0] in name:     # no repeats
                break
            if abs(plus) < abs(modifier[1]):    # too much
                break
            name = modifier[0] + " " + name
            plus -= modifier[1]
            count += 1
        self.equips[posn] = (name, plus)
        self.print_log("Gained equipment: " + self.equip_name((name, plus)))

    def win_stat(self):
        if random.random() < 0.5:
            i = random.randrange(len(self.stats))
        else:
            # favor the best stats so they will tend to clump
            t = 0
            for i in range(len(self.stats)):
                t += self.stats[i] * self.stats[i]
            t = 0x3FFFFFFFFFFFFFFF % t
            i = -1
            while t >= 0:
                i += 1
                t -= self.stats[i] * self.stats[i]
        self.stats[i] += 1
        self.print_log("Gained stat: " + self.idx_to_stat(i))

    def win_item(self):
        if max(250, random.randrange(999)) < len(self.items):
            item = random.choice(list(self.items.keys()))
        else:
            item = self.special_item()
        self.items[item] += 1
        self.print_log("Gained item: " + item)

    def special_item(self):
        return self.interesting_item() + " of " + random.choice(ITEM_OFS)

    def interesting_item(self):
        return random.choice(ITEM_ATTRIB) + " " + random.choice(SPECIALS)

    def boring_item(self):
        return random.choice(BORING_ITEMS)

    def best_equip(self):
        equips = [equip for equip in self.equips if equip[0]]
        equips.sort(key=lambda x: x[1], reverse=True)
        return self.equip_name(equips[0])

    def best_spells(self):
        spells = list(self.spells.items())
        spells.sort(key=lambda x: x[1], reverse=True)
        if len(spells) > 3:
            spells = spells[:3]
        spells = [self.spell_name(spell) for spell in spells]
        return ", ".join(spells)

    def equip_name(self, equip):
        if equip[1] == 0:
            return equip[0]
        else:
            return "{:+d} {:s}".format(equip[1], equip[0])

    def spell_name(self, spell):
        return "{:s} {:s}".format(spell[0], self.int_to_roman(spell[1]))

    def idx_to_stat(self, idx):
        if idx == 0:
            return "STR"
        elif idx == 1:
            return "CON"
        elif idx == 2:
            return "DEX"
        elif idx == 3:
            return "INT"
        elif idx == 4:
            return "WIS"
        elif idx == 5:
            return "CHA"
        else:
            raise

    def sick(self, m, s):
        if m == -5 or m == 5:
            return "dead " + s
        elif m == -4 or m == 4:
            return "comatose " + s
        elif m == -3 or m == 3:
            return "crippled " + s
        elif m == -2 or m == 2:
            return "sick " + s
        elif m == -1 or m == 1:
            return "undernourished " + s
        else:
            return s

    def young(self, m, s):
        if m == -5 or m == 5:
            return "foetal " + s
        elif m == -4 or m == 4:
            return "baby " + s
        elif m == -3 or m == 3:
            return "preadolescent " + s
        elif m == -2 or m == 2:
            return "teenage " + s
        elif m == -1 or m == 1:
            return "underage " + s
        else:
            return s

    def big(self, m, s):
        if m == -5 or m == 5:
            return "titanic " + s
        elif m == -4 or m == 4:
            return "giant " + s
        elif m == -3 or m == 3:
            return "enormous " + s
        elif m == -2 or m == 2:
            return "massive " + s
        elif m == -1 or m == 1:
            return "greater " + s
        else:
            return s

    def special(self, m, s):
        if m == -5 or m == 5:
            return "demon " + s
        elif m == -4 or m == 4:
            return "undead " + s
        elif m == -3 or m == 3:
            if " " in s:
                return "warrior " + s
            else:
                return "Were-" + s
        elif m == -2 or m == 2:
            return "cursed " + s
        elif m == -1 or m == 1:
            if " " in s:
                return "veteran " + s
            else:
                return "Battle-" + s
        else:
            return s

    def save_game(self):
        if os.path.isfile("save.pq"):
            os.replace("save.pq", "save.pq.bak")
        with open("save.pq", "wb") as fout:
            pickle.dump(self, fout)

    @classmethod
    def load_game(cls):
        with open("save.pq", "rb") as fin:
            return pickle.load(fin)

    def print_log(self, msg, sec=0):
        print("[{:s}] {:s}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
        if sec > 0 and not self.cheat:
            time.sleep(sec)

    def int_to_roman(self, n):
        # I = 1
        # V = 5
        # X = 10
        # L = 50
        # C = 100
        # D = 500
        # M = 1000
        # A = 5000
        # T = 10000
        # P = 50000
        # E = 100000
        res = ""
        while n >= 100000:
            res += "E"
            n -= 100000
        if n >= 90000:
            res += "TE"
            n -= 90000
        if n >= 50000:
            res += "P"
            n -= 50000
        if n >= 40000:
            res += "TP"
            n -= 40000
        while n >= 10000:
            res += "T"
            n -= 10000
        if n >= 9000:
            res += "MT"
            n -= 9000
        if n >= 5000:
            res += "A"
            n -= 5000
        if n >= 4000:
            res += "MA"
            n -= 4000
        while n >= 1000:
            res += "M"
            n -= 1000
        if n >= 900:
            res += "CM"
            n -= 900
        if n >= 500:
            res += "D"
            n -= 500
        if n >= 400:
            res += "CD"
            n -= 400
        while n >= 100:
            res += "C"
            n -= 100
        if n >= 90:
            res += "XC"
            n -= 90
        if n >= 50:
            res += "L"
            n -= 50
        if n >= 40:
            res += "XL"
            n -= 40
        while n >= 10:
            res += "X"
            n -= 10
        if n >= 9:
            res += "IX"
            n -= 9
        if n >= 5:
            res += "V"
            n -= 5
        if n >= 4:
            res += "IV"
            n -= 4
        while n >= 1:
            res += "I"
            n -= 1
        return res


if __name__ == "__main__":
    if os.path.isfile("save.pq"):
        player = Player.load_game()
        player.dispatch()
    else:
        player = Player()
        player.new_game()
