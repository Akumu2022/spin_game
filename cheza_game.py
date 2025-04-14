import tkinter as tk
from tkinter import messagebox
import random
import math

MINIMUM_STAKE = 100
ROUNDS_PER_CYCLE = 1

class Player:
    def __init__(self, name, stake):
        self.name = name
        self.stake = stake
        self.payout = 0
        self.rounds_played = 0
        self.wins = 0
        self.is_cycle_winner = False
        self.chosen_number = None

    def __str__(self):
        return f"{self.name} - Stake: ${self.stake:.2f}, Payout: ${self.payout:.2f}, Wins: {self.wins}"

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spin the Wheel Game")
        self.house_balance = 10000
        self.house_profits = 0
        self.cycle_number = 1

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=10, pady=10)

        self.totals_label = tk.Label(
            self.main_frame,
            text=f"House Totals: ${self.house_profits + self.house_balance:.2f}",
            font=("Arial", 12, "bold"),
        )
        self.totals_label.pack(pady=5)

        self.setup_frame = tk.Frame(self.main_frame, borderwidth=2, relief="groove")
        self.setup_frame.pack(padx=10, pady=10)
        tk.Label(
            self.setup_frame, text="Enter Player Details", font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=4, pady=10)

        self.player_entries = []
        for i in range(4):
            tk.Label(
                self.setup_frame, text=f"Player {i+1} Name:", font=("Arial", 12)
            ).grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")
            name_entry = tk.Entry(self.setup_frame, width=15, font=("Arial", 12))
            name_entry.grid(row=i + 1, column=1, padx=5, pady=5)
            tk.Label(self.setup_frame, text="Stake ($):", font=("Arial", 12)).grid(
                row=i + 1, column=2, padx=5, pady=5, sticky="e"
            )
            stake_entry = tk.Entry(self.setup_frame, width=10, font=("Arial", 12))
            stake_entry.grid(row=i + 1, column=3, padx=5, pady=5)
            self.player_entries.append((name_entry, stake_entry))

        tk.Button(
            self.setup_frame,
            text="Start Game",
            font=("Arial", 12),
            command=self.start_game,
        ).grid(row=5, column=0, columnspan=4, pady=10)

        self.game_frame = tk.Frame(self.main_frame)
        self.canvas = tk.Canvas(self.game_frame, width=300, height=300, bg="grey")
        self.canvas.pack(pady=10)

        self.num_segments = 10
        self.angle_per_segment = 360 / self.num_segments
        self.colors = ["red", "blue", "black", "green", "purple"] * 2
        self.radius = 100
        self.center_x, self.center_y = 150, 150

        self.number_frame = tk.Frame(self.game_frame)
        self.number_frame.pack()
        tk.Label(self.number_frame, text="Pick a number:", font=("Arial", 12)).pack(
            side="left"
        )
        self.number_var = tk.StringVar()
        self.number_menu = tk.OptionMenu(self.number_frame, self.number_var, "")
        self.number_menu.config(width=5, font=("Arial", 12))
        self.number_menu.pack(side="left", padx=5)
        self.spin_button = tk.Button(
            self.number_frame,
            text="Confirm Choice",
            font=("Arial", 12),
            command=self.spin_wheel,
        )
        self.spin_button.pack(side="left")

        self.status_label = tk.Label(
            self.game_frame, text="", font=("Arial", 12), wraplength=400
        )
        self.status_label.pack(pady=10)

        self.results_text = tk.Text(
            self.game_frame, height=10, width=60, font=("Arial", 12)
        )
        self.results_text.pack(pady=10)
        self.results_text.config(state="normal")

        self.available_numbers = []

    def start_game(self):
        self.players = []
        for name_entry, stake_entry in self.player_entries:
            name = name_entry.get().strip()
            stake_text = stake_entry.get().strip()
            if not name or not stake_text:
                messagebox.showerror(
                    "Error", "Please enter name and stake for all players."
                )
                return
            try:
                stake = float(stake_text)
                if stake < MINIMUM_STAKE:
                    messagebox.showerror(
                        "Error", f"Stake must be at least ${MINIMUM_STAKE}."
                    )
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid stake amount.")
                return
            self.players.append(Player(name, stake))

        self.setup_frame.pack_forget()
        self.game_frame.pack()
        self.totals_label.config(
            text=f"House Totals: ${self.house_profits + self.house_balance:.2f}"
        )
        self.start_cycle()

    def start_cycle(self):
        self.current_round = 0
        self.status_label.config(text=f"Cycle {self.cycle_number} - Select numbers...")
        winner = random.choice(self.players)
        winner.is_cycle_winner = True
        self.results_text.config(state="normal")
        self.results_text.insert(
            "end", f"\nCycle {self.cycle_number} (Round {self.cycle_number})\n"
        )
        self.results_text.config(state="disabled")
        self.current_player_index = 0
        self.update_wheel_numbers()
        self.totals_label.config(
            text=f"House Totals: ${self.house_profits + self.house_balance:.2f}"
        )
        self.play_round()

    def play_round(self):
        if self.current_round >= ROUNDS_PER_CYCLE:
            self.end_cycle()
            return
        self.current_round += 1
        self.current_player_index = 0
        self.results_text.config(state="normal")
        self.results_text.insert("end", f"\n===== ROUND {self.current_round} =====\n")
        self.results_text.config(state="disabled")
        self.prompt_player()

    def prompt_player(self):
        if self.current_player_index >= len(self.players):
            self.spin_wheel()
            return
        player = self.players[self.current_player_index]
        self.status_label.config(
            text=f"{player.name}, Round {self.current_round}: Pick a number from the wheel"
        )
        self.number_var.set("")
        menu = self.number_menu["menu"]
        menu.delete(0, "end")
        for num in sorted(self.available_numbers):  # Sort for consistency
            menu.add_command(
                label=num, command=lambda value=num: self.number_var.set(value)
            )
        self.draw_wheel()
        self.spin_button.config(state="normal")

    def update_wheel_numbers(self):
        if not hasattr(self, "wheel_numbers"):
            numbers = [13]
            winner = next(p for p in self.players if p.is_cycle_winner)
            winner_number = random.randint(1, 50)
            while winner_number in numbers:
                winner_number = random.randint(1, 50)
            numbers.append(winner_number)
            winner.chosen_number = winner_number 
            remaining_slots = self.num_segments - len(numbers)
            random_numbers = random.sample(
                [n for n in range(1, 51) if n not in numbers], remaining_slots
            )
            self.wheel_numbers = numbers + random_numbers
            random.shuffle(self.wheel_numbers)
            self.available_numbers = self.wheel_numbers.copy()
            self.winner_segment = self.wheel_numbers.index(winner_number)
        else:
            chosen_numbers = [p.chosen_number for p in self.players if p.chosen_number]
            self.available_numbers = [
                num for num in self.wheel_numbers if num not in chosen_numbers
            ]

    def draw_wheel(self, start_angle=0):
        self.canvas.delete("all")
        for i in range(self.num_segments):
            arc_start = start_angle + i * self.angle_per_segment
            arc_end = self.angle_per_segment - 0.1
            self.canvas.create_arc(
                self.center_x - self.radius,
                self.center_y - self.radius,
                self.center_x + self.radius,
                self.center_y + self.radius,
                start=arc_start,
                extent=arc_end,
                fill=self.colors[i],
                outline="black",
            )
            text_angle = math.radians(arc_start + self.angle_per_segment / 2)
            text_x = self.center_x + 0.7 * self.radius * math.cos(text_angle)
            text_y = self.center_y - 0.7 * self.radius * math.sin(text_angle)
            number = self.wheel_numbers[i] if hasattr(self, "wheel_numbers") else ""
            font_style = "bold" if number in [p.chosen_number for p in self.players if p.chosen_number] else "normal"
            font_style = "italic" if number == 13 else font_style
            self.canvas.create_text(
                text_x,
                text_y,
                text=str(number),
                font=("Arial", 12, font_style),
                fill="white",
            )
        # Arrow at the bottom, pointing upward toward the wheel
        self.canvas.create_polygon(
            self.center_x - 10, self.center_y + self.radius + 10,  
            self.center_x + 10, self.center_y + self.radius + 10,  
            self.center_x, self.center_y + self.radius,             
            fill="black",
        )

    def spin_wheel(self):
        if self.current_player_index < len(self.players):
            player = self.players[self.current_player_index]
            try:
                chosen = int(self.number_var.get())
                if chosen not in self.available_numbers:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error", "Please select a valid number from the wheel."
                )
                return
            player.chosen_number = chosen
            player.rounds_played += 1
            self.results_text.config(state="normal")
            self.results_text.insert("end", f"{player.name} chose: {chosen}\n")
            self.results_text.config(state="disabled")
            self.current_player_index += 1
            self.update_wheel_numbers()
            if self.current_player_index < len(self.players):
                self.prompt_player()
                return

        self.spin_button.config(text="Spin Wheel")
        winner = next(p for p in self.players if p.is_cycle_winner)
        self.winning_number = winner.chosen_number
        self.rotation_angle = 0
        self.update_count = 0
        self.animate_wheel()

    def animate_wheel(self):
        self.canvas.delete("all")
        self.draw_wheel(self.rotation_angle)
        self.rotation_angle = (self.rotation_angle + 10) % 360
        self.update_count += 1
        
        # Dynamic speed for more realistic animation
        if self.update_count < 20:
            speed = 20  # Start fast
        elif self.update_count < 100:
            speed = 30  # Slow down a bit
        elif self.update_count < 150:
            speed = 50  # Even slower
        else:
            speed = 80  # Very slow at the end
            
        if self.update_count < 250:
            self.root.after(speed, self.animate_wheel)
        else:
            # Find the winning number's position on the wheel
            winning_index = self.wheel_numbers.index(self.winning_number)
                
            segment_angle = self.angle_per_segment
            segment_center = winning_index * segment_angle + (segment_angle / 2)
            final_angle = (90 - segment_center + 180) % 360
            self.canvas.delete("all")
            self.draw_wheel(final_angle)
            
            self.results_text.config(state="normal")
            self.results_text.insert("end", f"Winning number: {self.winning_number}\n")
            winners = [p for p in self.players if p.chosen_number == self.winning_number]
            for p in winners:
                self.results_text.insert("end", f"{p.name}: 🎉 You WON!\n")
            for p in self.players:
                if p not in winners:
                    self.results_text.insert("end", f"{p.name}: No win.\n")
            self.results_text.config(state="disabled")
            self.spin_button.config(state="disabled")
            self.totals_label.config(
                text=f"House Totals: ${self.house_profits + self.house_balance:.2f}"
            )
            self.root.after(1000, self.end_cycle)  # Delay slightly to let users see result

    def end_cycle(self):
        total_stake_pool = sum(p.stake for p in self.players)
        cycle_winner = next(p for p in self.players if p.is_cycle_winner)
        winners = [p for p in self.players if p.chosen_number == cycle_winner.chosen_number]
        sum_winner_stakes = sum(p.stake for p in winners)
        total_winner_payout = sum_winner_stakes + 0.2 * total_stake_pool
        winner_outputs = []
        for p in winners:
            payout = total_winner_payout * (p.stake / sum_winner_stakes)
            p.payout += payout
            p.wins += 1
            winner_outputs.append((p.name, payout))

        if total_winner_payout > total_stake_pool:
            deficit = total_winner_payout - total_stake_pool
            self.house_balance -= deficit
            house_pool = 0
            bonus = 0
            bonus_player = None
        else:
            remaining_pool = total_stake_pool - total_winner_payout
            bonus = 0
            if random.random() < 0.1:
                bonus = 0.05 * remaining_pool
            house_pool = remaining_pool - bonus
            self.house_profits += house_pool

            bonus_player = None
            if bonus > 0:
                losers = [p for p in self.players if p not in winners]
                if losers:
                    bonus_player = random.choice(losers)
                    bonus_player.payout += bonus

        self.results_text.config(state="normal")
        self.results_text.insert("end", "\n===== PAYOUTS =====\n")
        for name, payout in winner_outputs:
            self.results_text.insert("end", f"{name}: ${payout:.2f}\n")
        if bonus_player:
            self.results_text.insert(
                "end", f"{bonus_player.name}: ${bonus:.2f} (Bonus)\n")
        self.results_text.insert("end", f"House Pool: ${house_pool:.2f}\n")
        self.results_text.insert(
            "end",
            f"House Totals: ${self.house_profits + self.house_balance:.2f}\n",
        )
        self.results_text.config(state="disabled")

        self.results_frame = tk.Frame(self.main_frame)
        self.results_frame.pack(pady=10)
        tk.Label(
            self.results_frame, text="===== FINAL RESULTS =====", font=("Arial", 14)
        ).pack(pady=10)
        for p in self.players:
            tk.Label(self.results_frame, text=str(p), font=("Arial", 12)).pack()
        tk.Label(
            self.results_frame,
            text=f"Total House Profits: ${self.house_profits:.2f}",
            font=("Arial", 12),
        ).pack(pady=5)
        tk.Label(
            self.results_frame,
            text=f"House Balance: ${self.house_balance:.2f}",
            font=("Arial", 12),
        ).pack(pady=5)
        tk.Label(
            self.results_frame,
            text=f"House Totals: ${self.house_profits + self.house_balance:.2f}",
            font=("Arial", 12),
        ).pack(pady=5)
        tk.Button(
            self.results_frame,
            text="Continue Playing",
            font=("Arial", 12),
            command=self.reset_game,
        ).pack(side="left", padx=5, pady=10)
        tk.Button(
            self.results_frame, text="Exit", font=("Arial", 12), command=self.root.quit
        ).pack(side="left", padx=5, pady=10)

        self.totals_label.config(
            text=f"House Totals: ${self.house_profits + self.house_balance:.2f}"
        )

    def reset_game(self):
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, "end")
        self.results_text.config(state="disabled")
        self.players = []
        self.cycle_number += 1
        self.results_frame.destroy()
        for name_entry, stake_entry in self.player_entries:
            name_entry.delete(0, "end")
            stake_entry.delete(0, "end")
        self.setup_frame.pack()
        self.game_frame.pack_forget()
        self.totals_label.config(
            text=f"House Totals: ${self.house_profits + self.house_balance:.2f}"
        )
        self.available_numbers = []
        if hasattr(self, "wheel_numbers"):
            delattr(self, "wheel_numbers")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()