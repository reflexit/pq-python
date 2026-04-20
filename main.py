import tkinter as tk
import threading
import os

from player import Player
from constants import *


class ProgressQuestGUI:
    def __init__(self):
        # load save file if it exists, otherwise generate a new character
        if os.path.isfile("save.pq"):
            self.player = Player.load_game()
            self.game_thread = threading.Thread(target=self.player.dispatch, daemon=True)
        else:
            self.player = Player()
            self.game_thread = threading.Thread(target=self.player.new_game, daemon=True)

        # start Tkinter
        self.root = tk.Tk()
        self.root.geometry("800x600")
        self.root.title("Progress Quest")
        self.setup_gui()
        self.update_gui()

        # handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # launch game processing in a daemon thread 
        self.game_thread.start()

        self.root.mainloop()

    def setup_gui(self):
        # ---------------- 1. Character Sheet ----------------
        self.char_frame = tk.LabelFrame(self.root, text="Character Sheet")
        self.char_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nswe")

        self.lbl_level = tk.Label(self.char_frame, text="", anchor="w", justify=tk.LEFT, font=("Consolas", 10, "bold"))
        self.lbl_level.grid(row=0, column=0, padx=5, pady=2, sticky="we")

        self.lbl_stats = tk.Label(self.char_frame, text="", anchor="w", justify=tk.LEFT, font=("Consolas", 10))
        self.lbl_stats.grid(row=1, column=0, padx=5, pady=2, sticky="we")

        self.lbl_hp_mp = tk.Label(self.char_frame, text="", anchor="w", justify=tk.LEFT, font=("Consolas", 10))
        self.lbl_hp_mp.grid(row=2, column=0, padx=5, pady=2, sticky="we")

        # ---------------- 2. Equipment ----------------
        self.equip_frame = tk.LabelFrame(self.root, text="Equipment")
        self.equip_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nswe")

        self.lst_equip = tk.Listbox(self.equip_frame, height=12, font=("Arial", 10))
        self.lst_equip.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ---------------- 3. Spell Book ----------------
        self.spell_frame = tk.LabelFrame(self.root, text="Spell Book")
        self.spell_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nswe")

        self.lst_spell = tk.Listbox(self.spell_frame, font=("Arial", 10))
        self.lst_spell.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ---------------- 4. Inventory ----------------
        self.inv_frame = tk.LabelFrame(self.root, text="Inventory")
        self.inv_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nswe")

        self.lbl_gold = tk.Label(self.inv_frame, text="", font=("Arial", 10, "bold"))
        self.lbl_gold.pack(anchor="w", padx=5, pady=2)

        self.lst_inv = tk.Listbox(self.inv_frame, font=("Arial", 10))
        self.lst_inv.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ---------------- 5. Plot Development ----------------
        self.plot_frame = tk.LabelFrame(self.root, text="Plot Development")
        self.plot_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nswe")

        self.lbl_plot = tk.Label(self.plot_frame, text="", font=("Arial", 10, "bold"))
        self.lbl_plot.pack(anchor="w", padx=5, pady=2)

        self.lbl_plot_prog = tk.Label(self.plot_frame, text="", font=("Arial", 10))
        self.lbl_plot_prog.pack(anchor="w", padx=5, pady=2)

        # ---------------- 6. Quests ----------------
        self.quest_frame = tk.LabelFrame(self.root, text="Quests")
        self.quest_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nswe")

        self.lbl_quest = tk.Label(self.quest_frame, text="", font=("Arial", 10, "bold"))
        self.lbl_quest.pack(anchor="w", padx=5, pady=2)

        self.lbl_quest_prog = tk.Label(self.quest_frame, text="", font=("Arial", 10))
        self.lbl_quest_prog.pack(anchor="w", padx=5, pady=2)

        # ---------------- 7. Status Log ----------------
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        self.lbl_status = tk.Label(self.status_frame, text="", relief=tk.SUNKEN, anchor="w", bg="white")
        self.lbl_status.pack(fill=tk.X)

        # configure layout weights
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

    def update_listbox(self, listbox, new_items):
        # helper to avoid flickering: updates listbox only if contents have changed
        current_items = listbox.get(0, tk.END)
        if tuple(current_items) != tuple(new_items):
            listbox.delete(0, tk.END)
            for item in new_items:
                listbox.insert(tk.END, item)

    def update_gui(self):
        p = self.player

        # 1. update Character Sheet
        self.lbl_level.config(text=f"Level {p.level}\nEXP: {p.exp} / {p.exp_needed}")
        self.lbl_hp_mp.config(text=f"HP Max: {p.HP}\nMP Max: {p.MP}")

        stats = [f"{k}: {p.stats[k]}" for k in p.stats]
        stats_text = f"{stats[0]}\n{stats[1]}\n{stats[2]}\n{stats[3]}\n{stats[4]}\n{stats[5]}"
        self.lbl_stats.config(text=stats_text)

        # 2. update Equipment
        equips_list = [f"{pt}: {p.equip_name(e) if e[0] else ''}" for pt, e in zip(EQUIPMENT_PARTS, p.equips)]
        self.update_listbox(self.lst_equip, equips_list)

        # 3. update Spell Book
        spells_list = [p.spell_name(s) for s in p.spells.items()]
        self.update_listbox(self.lst_spell, spells_list)

        # 4. update Inventory
        inv_cap = p.stats["STR"] + 10
        self.lbl_gold.config(text=f"Gold: {p.gold}    (Items: {sum(p.items.values())} / {inv_cap})")
        inv_list = [f"{qty}x {item}" for item, qty in p.items.items()]
        self.update_listbox(self.lst_inv, inv_list)

        # 5. update Plot Development
        self.lbl_plot.config(text=p.act_caption)
        plot_pct = (p.act_progress / p.act_time) * 100 if p.act_time else 0
        self.lbl_plot_prog.config(text=f"Progress: {plot_pct:.2f}%")

        # 6. update Quests
        self.lbl_quest.config(text=p.quest_caption if p.quest_caption else "Awaiting Destiny...")
        self.lbl_quest_prog.config(text=f"Progress: {p.quest_progress}%")

        # 7. update Current Status
        self.lbl_status.config(text=p.msg)

        # schedule next update in 1 second
        self.root.after(1000, self.update_gui)

    def on_closing(self):
        self.player.save_game()
        self.root.destroy()


if __name__ == "__main__":
    ProgressQuestGUI()
