import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
from datetime import datetime, date, timedelta
import calendar
import random

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "life_ledger.json")
BG_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
FUTURE_TINT = "#050810" 
CLOCK_TINT = "#080C18"  

QUOTES = [
    "It is not that we have a short time to live, but that we waste much of it.",
    "Death remains even when you are not looking.",
    "You could leave life right now. Let that determine what you do and say and think.",
    "Think of yourself as dead. You have lived your life. Now, live what's left properly.",
    "Waste no more time arguing what a good man should be. Be one.",
    "Remember how long you've been putting this off.",
    "He who fears death will never do anything worthy of a man who is alive."
]

STATES = {
    1: {"label": "PRODUCTIVE", "color": "#FFFFFF", "rgb": (255, 255, 255), "text": "#000000"},
    2: {"label": "SLIGHTLY", "color": "#707070", "rgb": (112, 112, 112), "text": "#FFFFFF"},
    3: {"label": "UNPRODUCTIVE", "color": "#333333", "rgb": (51, 51, 51), "text": "#FFFFFF"},
    4: {"label": "COUNTER-PROD", "color": "#0A0A0A", "rgb": (10, 10, 10), "text": "#FFFFFF"} 
}

class StoicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MEMENTO MORI")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG_COLOR)
        
        self.view_date = date.today().replace(day=1)
        self.data = self.load_data()
        
        self.main_wrapper = tk.Frame(self.root, bg=BG_COLOR)
        self.main_wrapper.pack(expand=True, fill="both", padx=50, pady=30)

        if "user_profile" not in self.data:
            self.ask_user_lifespan()
        else:
            self.start_date = date.fromisoformat(self.data["meta"]["start_date"])
            self.render_flow()
            self.update_live_clock()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f: return json.load(f)
            except: return {}
        return {}

    def save_to_disk(self):
        with open(DATA_FILE, "w") as f: json.dump(self.data, f)

    def render_flow(self):
        # Clear the screen
        for w in self.main_wrapper.winfo_children(): w.destroy()
        
        check_date = self.start_date
        today = date.today()

        # If there are days between start_date and today that aren't logged, show entry screen
        while check_date <= today:
            d_str = check_date.isoformat()
            if d_str not in self.data:
                self.show_entry_screen(check_date)
                return # Exit and wait for user input
            check_date += timedelta(days=1)
            
        # If everything is logged, show the grid (and the clock!)
        self.show_grid_screen()

    def show_grid_screen(self):
        for w in self.main_wrapper.winfo_children(): w.destroy()
        today = date.today()
        profile = self.data["user_profile"]
        birth_ts = datetime.fromisoformat(profile["birth_timestamp"])
        
        header_f = tk.Frame(self.main_wrapper, bg=BG_COLOR)
        header_f.pack(fill="x", pady=(0, 20))
        tk.Label(header_f, text="MEMENTO MORI", fg=TEXT_COLOR, bg=BG_COLOR, font=("Courier", 32, "bold")).pack(side="left")

        body = tk.Frame(self.main_wrapper, bg=BG_COLOR)
        body.pack(expand=True, fill="both")

        col1 = tk.Frame(body, bg=BG_COLOR, width=350) # Widened for bigger grid
        col1.pack(side="left", fill="y", padx=(0, 40))
        
        stats = {k: 0 for k in STATES}
        total_logged = 0
        for k, v in self.data.items():
            if len(k) == 10 and v in stats:
                stats[v] += 1; total_logged += 1

        tk.Label(col1, text="RATIOS", fg="#444", bg=BG_COLOR, font=("Courier", 10, "bold")).pack(anchor="w")
        for k, props in STATES.items():
            row = tk.Frame(col1, bg=BG_COLOR); row.pack(fill="x", pady=8)
            tk.Label(row, text=str(stats[k]), fg=TEXT_COLOR, bg=BG_COLOR, font=("Courier", 20, "bold"), width=3).pack(side="left")
            b_f = tk.Frame(row, bg=BG_COLOR); b_f.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(b_f, text=props["label"], fg="#555", bg=BG_COLOR, font=("Courier", 9, "bold")).pack(anchor="w")
            p = (stats[k]/total_logged) if total_logged > 0 else 0
            tk.Label(row, text=f"{p*100:.1f}%", fg="#666", bg=BG_COLOR, font=("Courier", 11, "bold")).pack(side="right")

        tk.Label(col1, text="LIFE GRID (White: remaining | Cross: passed)", fg="#444", bg=BG_COLOR, font=("Courier", 8, "bold")).pack(anchor="w", pady=(30, 10))
        grid_c = tk.Frame(col1, bg=BG_COLOR); grid_c.pack(anchor="w")
        days_lived = (datetime.now() - birth_ts).days
        curr_yr = days_lived // 365

        # BIGGER LIFE GRID BOXES (18x18 instead of 12x12)
        for i in range(80):
            bg_col = "#111" if i < curr_yr else "#FFFFFF"
            dot = tk.Frame(grid_c, width=18, height=18, bg=bg_col)
            dot.grid(row=i//10, column=i%10, padx=3, pady=3)
            
            if i < curr_yr:
                tk.Label(dot, text="✕", fg="#444", bg=bg_col, font=("Arial", 10, "bold")).place(relx=0.5, rely=0.5, anchor="center")
            elif i == curr_yr: 
                tk.Frame(dot, width=6, height=6, bg="#555").place(relx=0.5, rely=0.5, anchor="center")

        col2 = tk.Frame(body, bg=BG_COLOR)
        col2.pack(side="left", expand=True, fill="both")
        
        nav_area = tk.Frame(col2, bg=BG_COLOR, width=820, height=120)
        nav_area.pack(pady=(0, 15))
        nav_area.pack_propagate(False)

        # Stationary PREV / NEXT buttons
        tk.Button(nav_area, text="<", command=lambda: self.change_month(-1),
                  fg="#333", bg=BG_COLOR, activebackground=BG_COLOR, activeforeground="#FFF",
                  bd=0, font=("Courier", 30)).place(x=10, y=40, anchor="w")

        tk.Button(nav_area, text=">", command=lambda: self.change_month(1),
                  fg="#333", bg=BG_COLOR, activebackground=BG_COLOR, activeforeground="#FFF",
                  bd=0, font=("Courier", 30)).place(x=790, y=40, anchor="e")

        # Center editable Month / Year
        center_nav = tk.Frame(nav_area, bg=BG_COLOR)
        center_nav.place(relx=0.5, y=40, anchor="center")

        m_lbl = tk.Label(center_nav, text=calendar.month_name[self.view_date.month].upper(),
                         fg=TEXT_COLOR, bg=BG_COLOR, font=("Courier", 28, "bold"), cursor="hand2")
        m_lbl.pack(side="left", padx=10)
        m_lbl.bind("<Button-1>", lambda e: self.make_editable(m_lbl, "month"))

        y_lbl = tk.Label(center_nav, text=str(self.view_date.year),
                         fg=TEXT_COLOR, bg=BG_COLOR, font=("Courier", 28, "bold"), cursor="hand2")
        y_lbl.pack(side="left", padx=10)
        y_lbl.bind("<Button-1>", lambda e: self.make_editable(y_lbl, "year"))

        # Return to today directly beneath the centered date
        tk.Button(nav_area, text="RETURN TO TODAY", command=self.go_today,
                  bg=BG_COLOR, fg="#444", font=("Courier", 9, "bold"), bd=0,
                  activebackground=BG_COLOR, activeforeground="#AAA").place(relx=0.5, y=85, anchor="center")

        cal_f = tk.Frame(col2, bg=BG_COLOR); cal_f.pack(anchor="center")
        for i, day_name in enumerate(["MO", "TU", "WE", "TH", "FR", "SA", "SU"]):
            tk.Label(cal_f, text=day_name, fg="#333", bg=BG_COLOR, font=("Courier", 10, "bold")).grid(row=0, column=i, pady=5)

        cal = calendar.monthcalendar(self.view_date.year, self.view_date.month)
        for r, week in enumerate(cal):
            for c, d in enumerate(week):
                if d == 0: continue
                curr_d = date(self.view_date.year, self.view_date.month, d)
                d_str = curr_d.isoformat()
                has_data = d_str in self.data
                is_future = curr_d > today
                
                bg = FUTURE_TINT if (is_future and not has_data) else (STATES[self.data[d_str]]["color"] if has_data else "#000000")
                border = "#222" if is_future else ("#666" if has_data else ("#900" if curr_d == today else "#222"))
                
                # BIGGER CALENDAR BOXES (100x100 instead of 75x75)
                box = tk.Frame(cal_f, bg=bg, highlightthickness=1, highlightbackground=border, width=100, height=100)
                box.grid(row=r+1, column=c, padx=5, pady=5); box.grid_propagate(False)
                
                text_col = "#2A3A5A" if is_future else (STATES[self.data[d_str]]["text"] if has_data else "#444")
                tk.Label(box, text=str(d), fg=text_col, bg=bg, font=("Courier", 16, "bold")).place(relx=0.5, rely=0.5, anchor="center")
                
                if curr_d < today:
                    x_col = "#222" if not has_data else "#777"
                    tk.Label(box, text="✕", fg=x_col, bg=bg, font=("Arial", 36)).place(relx=0.5, rely=0.5, anchor="center")
                
                if self.start_date <= curr_d <= today: box.bind("<Button-1>", lambda e, ds=d_str: self.edit_day(ds))

        col3 = tk.Frame(body, bg=BG_COLOR, width=320)
        col3.pack(side="right", fill="y", padx=(40, 0))
        donation = self.render_donation_widget(col3)
        donation.pack(fill="x", pady=(0, 20))
        clk_box = tk.Frame(col3, bg=CLOCK_TINT, highlightthickness=1, highlightbackground="#1A3A5A", padx=25, pady=25)
        clk_box.pack(fill="x", side="top")
        tk.Label(clk_box, text="TIME REMAINING", fg="#4A6A8A", bg=CLOCK_TINT, font=("Courier", 10, "bold")).pack(anchor="w")
        self.clk_y = tk.Label(clk_box, text="", fg=TEXT_COLOR, bg=CLOCK_TINT, font=("Courier", 52, "bold"))
        self.clk_y.pack(anchor="w")
        self.clk_dh = tk.Label(clk_box, text="", fg="#8A9AAB", bg=CLOCK_TINT, font=("Courier", 22, "bold"))
        self.clk_dh.pack(anchor="w")
        self.clk_ms = tk.Label(clk_box, text="", fg="#4A6A8A", bg=CLOCK_TINT, font=("Courier", 14, "bold"))
        self.clk_ms.pack(anchor="w")

        tk.Frame(col3, bg=BG_COLOR, height=60).pack()

        age_box = tk.Frame(col3, bg="#0A0A0A", highlightthickness=1, highlightbackground="#222", padx=25, pady=25)
        age_box.pack(fill="x", side="top")
        tk.Label(age_box, text="CURRENT AGE", fg="#444", bg="#0A0A0A", font=("Courier", 10, "bold")).pack(anchor="w")
        self.age_y_lbl = tk.Label(age_box, text="", fg=TEXT_COLOR, bg="#0A0A0A", font=("Courier", 52, "bold"))
        self.age_y_lbl.pack(anchor="w")
        self.age_d_lbl = tk.Label(age_box, text="", fg="#888", bg="#0A0A0A", font=("Courier", 22, "bold"))
        self.age_d_lbl.pack(anchor="w")

        footer = tk.Frame(self.main_wrapper, bg=BG_COLOR)
        footer.pack(fill="x", side="bottom", pady=(20, 0))
        info_f = tk.Frame(footer, bg=BG_COLOR); info_f.pack(fill="x")
        
        self.perc_lbl = tk.Label(info_f, text="", fg="#999", bg=BG_COLOR, font=("Courier", 14, "bold"))
        self.perc_lbl.pack(side="left")
        
        tk.Label(info_f, text=f"LOGGED: {total_logged} DAYS", fg="#666", bg=BG_COLOR, font=("Courier", 12, "bold")).pack(side="right")

        avg_rgb = [sum(stats[k] * STATES[k]["rgb"][i] for k in STATES) // total_logged for i in range(3)] if total_logged > 0 else (255,255,255)
        prog_bar_bg = tk.Frame(footer, bg="#111", height=24)
        prog_bar_bg.pack(fill="x", pady=(10, 5))
        lived_perc_static = min(1.0, (days_lived / (80 * 365.25)))
        tk.Frame(prog_bar_bg, bg=f"#{avg_rgb[0]:02x}{avg_rgb[1]:02x}{avg_rgb[2]:02x}", height=24).place(relx=0, rely=0, relwidth=lived_perc_static)
        
        tk.Label(footer, text=f"\"{random.choice(QUOTES)}\"", fg="#444", bg=BG_COLOR, font=("Courier", 14, "italic")).pack(pady=(10, 0))

    def make_editable(self, label, mode):
        curr = label.cget("text")
        parent = label.master
        label.pack_forget()
        e = tk.Entry(parent, bg=BG_COLOR, fg=TEXT_COLOR, font=("Courier", 28, "bold"), bd=0, width=len(curr)+1, justify="center", insertbackground="white")
        e.insert(0, curr); e.pack(side="left"); e.focus_set()
        e.bind("<Return>", lambda event: self.apply_edit(e, mode))
        e.bind("<FocusOut>", lambda event: self.show_grid_screen())

    def apply_edit(self, entry, mode):
        val = entry.get().strip()
        try:
            if mode == "year": self.view_date = self.view_date.replace(year=int(val))
        except: pass
        self.show_grid_screen()

    def change_month(self, delta):
        m = self.view_date.month + delta
        y = self.view_date.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        self.view_date = self.view_date.replace(year=y, month=m); self.show_grid_screen()

    def go_today(self):
        self.view_date = date.today().replace(day=1); self.show_grid_screen()

    def edit_day(self, d_str): self.show_entry_screen(date.fromisoformat(d_str))
    
    def show_entry_screen(self, target_date):
        for w in self.main_wrapper.winfo_children(): w.destroy()
        f = tk.Frame(self.main_wrapper, bg=BG_COLOR); f.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(f, text=target_date.strftime("%d %B %Y").upper(), fg=TEXT_COLOR, bg=BG_COLOR, font=("Courier", 28, "bold")).pack(pady=40)
        
        for val, props in STATES.items():
            lbl = tk.Label(
                f,
                text=props["label"],
                bg=props["color"],
                fg=props["text"],
                font=("Courier", 16, "bold"),
                width=40,
                height=2
            )
            lbl.pack(pady=10)

            lbl.bind(
                "<Button-1>",
                lambda e, v=val: self.submit(target_date.isoformat(), v)
            )
    def submit(self, d_str, v):
        self.data[d_str] = v; self.save_to_disk(); self.render_flow()
    def render_donation_widget(self, parent):
        container = tk.Frame(parent, bg="#080C18")

        txt = tk.Label(
            container,
            text="If this helped you reflect,\nconsider supporting the project.",
            bg="#080C18",
            fg="#888888",
            font=("Courier", 10),
            justify="center"
        )
        txt.pack(padx=10, pady=(8, 4))

        donate_btn = tk.Label(
            container,
            text="☕ Buy Me a Coffee",
            bg="#11162A",
            fg="#00FFAA",
            font=("Courier", 11, "bold"),
            padx=12,
            pady=6,
            cursor="hand2"
        )
        donate_btn.pack(pady=(0, 8))

        donate_btn.bind("<Button-1>", lambda e: self.open_donation_link())

        return container
    def open_donation_link(self):
        import webbrowser
        webbrowser.open("https://razorpay.me/@garvgarg")  # Replace with your actual donation link 
    def save_init(self, dob_input):
        ts = None
        # Support optional time
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                ts = datetime.strptime(dob_input.strip(), fmt)
                break
            except ValueError:
                continue
        
        if ts:
            # We must set both the data dict AND the class variable start_date
            self.data = {
                "user_profile": {"birth_timestamp": ts.isoformat(), "limit": 80},
                "meta": {"start_date": date.today().isoformat()}
            }
            self.start_date = date.today() 
            self.save_to_disk()
            
            # Immediately move to the flow (Entry Screen -> Grid Screen)
            self.render_flow()
        else:
            messagebox.showerror("Error", "Invalid Date. Use YYYY-MM-DD or YYYY-MM-DD HH:MM")

    def ask_user_lifespan(self):
        for w in self.main_wrapper.winfo_children(): w.destroy()
        f = tk.Frame(self.main_wrapper, bg=BG_COLOR)
        f.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(f, text="INITIALIZE LIFE SPECTRUM", fg=TEXT_COLOR, bg=BG_COLOR, font=("Courier", 27, "bold")).pack()
        tk.Label(f, text="ENTER BIRTH DATE AND TIME(OPTIONAL) [YYYY:MM:DD]", fg="#444", bg=BG_COLOR, font=("Courier", 14)).pack(pady=(5, 15))
        
        e = tk.Entry(f, font=("Courier", 38, "bold"), bg=BG_COLOR, fg=TEXT_COLOR, bd=0, justify="center", insertbackground="white", width=20)
        e.insert(0, "1995-01-01 12:00")
        e.pack(pady=20)
        e.focus_set()
        
        tk.Button(f, text="START COUNTDOWN", command=lambda: self.save_init(e.get()), bg="#FFF", fg="#000", font=("Courier", 14, "bold"), padx=25, pady=12, bd=0).pack()
    
    def update_live_clock(self):
        # 1. Only run logic if profile exists
        if "user_profile" in self.data:
            profile = self.data["user_profile"]
            birth_ts = datetime.fromisoformat(profile["birth_timestamp"])
            limit_yrs = profile.get("limit", 80)
            now = datetime.now()
            # 2. Only update if all clock labels exist
            required = ('clk_y','clk_dh','clk_ms','age_y_lbl','age_d_lbl','perc_lbl')
            if all(hasattr(self, w) and getattr(self, w).winfo_exists() for w in required):
                try:
                    # CURRENT AGE
                    age_y = now.year - birth_ts.year - ((now.month, now.day) < (birth_ts.month, birth_ts.day))
                    try:
                        last_bday = birth_ts.replace(year=birth_ts.year + age_y)
                    except ValueError: last_bday = birth_ts.replace(year=birth_ts.year + age_y, day=28)
                    
                    age_d = (now - last_bday).days
                    self.age_y_lbl.config(text=f"{age_y}Y")
                    self.age_d_lbl.config(text=f"{age_d}D OLD")

                    # REMAINING TIME
                    try:
                        death_dt = birth_ts.replace(year=birth_ts.year + limit_yrs)
                    except ValueError: death_dt = birth_ts.replace(year=birth_ts.year + limit_yrs, day=28)
                    
                    rem = death_dt - now
                    if rem.total_seconds() > 0:
                        rem_y = death_dt.year - now.year - ((death_dt.month, death_dt.day) < (now.month, now.day))
                        h, m_rem = divmod(rem.seconds, 3600)
                        m, s = divmod(m_rem, 60)

                        self.clk_y.config(text=f"{rem_y}Y")
                        remaining_days = (death_dt - now.replace(year=now.year + rem_y)).days
                        self.clk_dh.config(text=f"{remaining_days}D {h}H")
                        self.clk_ms.config(text=f"{m:02}M {s:02}S")

                    # PERCENTAGE
                    total_life_sec = (death_dt - birth_ts).total_seconds()
                    lived_sec = (now - birth_ts).total_seconds()
                    perc = min(100.0, (lived_sec / total_life_sec) * 100)
                    if hasattr(self, 'perc_lbl') and self.perc_lbl.winfo_exists():
                        self.perc_lbl.config(text=f"LIFE COMPLETION: {perc:.7f}%")
                except Exception as e:
                    print(f"Clock update skipped: {e}") # Debugging info

        # 3. Always keep the loop alive
        self.root.after(200, self.update_live_clock)


if __name__ == "__main__":
    root = tk.Tk(); app = StoicApp(root); root.mainloop()