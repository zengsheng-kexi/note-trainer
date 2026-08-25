import tkinter as tk
import random

NOTE_NAMES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
NATURAL_SEMITONE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def midi_to_note_name(midi):
    octave = midi // 12 - 1
    name = NOTE_NAMES[midi % 12]
    return f"{name}{octave}"

def note_name_to_midi(name, octave):
    semitone = NATURAL_SEMITONE[name]
    return (octave + 1) * 12 + semitone

class PianoTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("五线谱音符练习")
        self.root.geometry("900x700")
        self.canvas = tk.Canvas(root, width=900, height=700, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.clef = 'treble'
        self.score = 0
        self.correct_count = 0
        self.attempt_count = 0
        self.current_midi = None
        self.current_note_name = None
        self.show_note_name = tk.BooleanVar(value=False)

        self.keyboard_start_midi = 36  # C2
        self.keyboard_end_midi = 84    # C6
        self.white_keys = []
        self.black_keys = []

        self.staff_base_y = 250
        self.staff_step = 12
        self.staff_left = 150
        self.staff_right = 750

        self.create_controls()
        self.draw_staff()
        self.draw_keyboard()
        self.new_note()

        self.canvas.bind("<Button-1>", self.on_click)

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(control_frame, text="谱号:").pack(side=tk.LEFT, padx=5)
        self.clef_var = tk.StringVar(value='treble')
        tk.Radiobutton(control_frame, text="高音谱号", variable=self.clef_var,
                       value='treble', command=self.change_clef).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(control_frame, text="低音谱号", variable=self.clef_var,
                       value='bass', command=self.change_clef).pack(side=tk.LEFT, padx=5)

        tk.Checkbutton(control_frame, text="显示音名", variable=self.show_note_name,
                       command=self.refresh_note_display).pack(side=tk.LEFT, padx=20)

        self.score_label = tk.Label(control_frame, text="得分: 0  正确: 0  尝试: 0")
        self.score_label.pack(side=tk.LEFT, padx=20)

        tk.Button(control_frame, text="重置", command=self.reset).pack(side=tk.LEFT, padx=10)

    def change_clef(self):
        self.clef = self.clef_var.get()
        self.draw_staff()
        self.new_note()

    def reset(self):
        self.score = 0
        self.correct_count = 0
        self.attempt_count = 0
        self.update_score_label()
        self.new_note()

    def update_score_label(self):
        self.score_label.config(text=f"得分: {self.score}  正确: {self.correct_count}  尝试: {self.attempt_count}")

    def draw_staff(self):
        self.canvas.delete("staff")
        for i in range(5):
            y = self.staff_base_y - i * self.staff_step
            self.canvas.create_line(self.staff_left, y, self.staff_right, y,
                                    fill='black', width=2, tags="staff")
        if self.clef == 'treble':
            text = "高音谱号"
        else:
            text = "低音谱号"
        self.canvas.create_text(self.staff_left - 20, self.staff_base_y - 2 * self.staff_step,
                                text=text, anchor='e', font=('Arial', 14), tags="staff")

    def note_y_position(self, midi):
        octave = midi // 12 - 1
        name = NOTE_NAMES[midi % 12]
        natural_index = NOTE_NAMES.index(name)
        natural_num = octave * 7 + natural_index
        if self.clef == 'treble':
            base_natural = 30  # E4
            y = self.staff_base_y - (natural_num - base_natural) * self.staff_step / 2
        else:
            base_natural = 24  # F3
            y = self.staff_base_y - (natural_num - base_natural) * self.staff_step / 2
        return y

    def draw_note(self, midi, color='black'):
        self.canvas.delete("note")
        y = self.note_y_position(midi)
        x = (self.staff_left + self.staff_right) // 2
        self.canvas.create_oval(x - 8, y - 6, x + 8, y + 6, fill=color, outline=color, tags="note")
        if self.show_note_name.get():
            self.canvas.create_text(x, y - 25, text=midi_to_note_name(midi),
                                    font=('Arial', 14), fill='blue', tags="note")

    def get_note_pool(self):
        if self.clef == 'treble':
            pool = []
            for octave in [4, 5]:
                for name in NOTE_NAMES:
                    midi = note_name_to_midi(name, octave)
                    if midi <= 81:  # A5
                        pool.append(midi)
            return pool
        else:
            pool = []
            for octave in [2, 3, 4]:
                for name in NOTE_NAMES:
                    midi = note_name_to_midi(name, octave)
                    if note_name_to_midi('E', 2) <= midi <= note_name_to_midi('C', 4):
                        pool.append(midi)
            return pool

    def new_note(self):
        pool = self.get_note_pool()
        self.current_midi = random.choice(pool)
        self.current_note_name = midi_to_note_name(self.current_midi)
        self.draw_note(self.current_midi)
        self.canvas.delete("highlight")
        self.update_score_label()

    def draw_keyboard(self):
        self.canvas.delete("keyboard")
        self.white_keys.clear()
        self.black_keys.clear()

        keyboard_top = 420
        keyboard_bottom = 650
        margin = 20
        total_width = 860
        total_white_keys = sum(1 for midi in range(self.keyboard_start_midi, self.keyboard_end_midi + 1)
                               if midi % 12 in [0, 2, 4, 5, 7, 9, 11])
        white_key_width = total_width / total_white_keys
        black_key_width = white_key_width * 0.6
        black_key_height = (keyboard_bottom - keyboard_top) * 0.6

        x = margin
        white_positions = []
        for midi in range(self.keyboard_start_midi, self.keyboard_end_midi + 1):
            if midi % 12 in [0, 2, 4, 5, 7, 9, 11]:
                x2 = x + white_key_width
                self.canvas.create_rectangle(x, keyboard_top, x2, keyboard_bottom,
                                             fill='white', outline='black', width=1, tags="keyboard")
                self.white_keys.append((x, keyboard_top, x2, keyboard_bottom, midi))
                white_positions.append((x, x2, midi))
                x += white_key_width

        # 绘制黑键
        for x1, x2, midi in white_positions:
            if midi % 12 in [0, 2, 5, 7, 9]:
                next_midi = midi + 1
                if next_midi % 12 in [1, 3, 6, 8, 10] and next_midi <= self.keyboard_end_midi:
                    black_x1 = x2 - black_key_width / 2
                    black_x2 = x2 + black_key_width / 2
                    self.canvas.create_rectangle(black_x1, keyboard_top,
                                                 black_x2, keyboard_top + black_key_height,
                                                 fill='black', outline='black', tags="keyboard")
                    self.black_keys.append((black_x1, keyboard_top, black_x2,
                                            keyboard_top + black_key_height, next_midi))

    def on_click(self, event):
        for x1, y1, x2, y2, midi in self.black_keys:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.check_answer(midi)
                return
        for x1, y1, x2, y2, midi in self.white_keys:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.check_answer(midi)
                return

    def check_answer(self, midi):
        self.attempt_count += 1
        if midi == self.current_midi:
            self.correct_count += 1
            self.score += 10
            self.update_score_label()
            self.draw_note(self.current_midi, color='green')
            self.root.after(500, self.new_note)
        else:
            self.score = max(0, self.score - 2)
            self.update_score_label()
            self.canvas.delete("feedback")
            self.canvas.create_text(450, 380, text="错误，再试试！",
                                    fill='red', font=('Arial', 16), tags="feedback")
            self.root.after(800, lambda: self.canvas.delete("feedback"))
            self.highlight_key(self.current_midi)

    def highlight_key(self, midi):
        self.canvas.delete("highlight")
        for x1, y1, x2, y2, key_midi in self.white_keys + self.black_keys:
            if key_midi == midi:
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             outline='red', width=3, tags="highlight")
                break

    def refresh_note_display(self):
        if self.current_midi is not None:
            self.draw_note(self.current_midi)

if __name__ == "__main__":
    root = tk.Tk()
    app = PianoTrainer(root)
    root.mainloop()