import tkinter as tk
from tkinter import messagebox
import pygame
import json
import os
import time
import math
import random

# ============================================================
# TRACK 8 — THE JEBLOGS
# Spotify / Apple Music style lyric player
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(BASE_DIR, "Track 8 - The Jeblogs.mp3")
TIMING_FILE = os.path.join(BASE_DIR, "timings.json")

# ============================================================
# PASTE LIRIK YANG LU PUNYA DI SINI
#
# Satu baris = satu baris lirik.
#
# Contoh:
#
# LYRICS_TEXT = """
# Baris pertama
# Baris kedua
# Baris ketiga
# """
#
# Jangan kasih timestamp di sini.
# Sync Mode yang akan membuat timestamp otomatis.
# ============================================================

LYRICS_TEXT = """
Menengadah ke tempat kau tinggal
Ditumbuhi rambut awan sirus
Gemuruh merah di kepala
Melamun dipeluk bayang-bayang
Inginku berkitar bersamamu
Terbang bebas di atas sana
Menanam padi di langit luas
Namun sempitnya pikiran memenjara
Sesak dada hitam udara
Persis seperti baju Batmanmu
Nanar mata melihat belakang
Apa yang harus aku lakukan
Kita keliru seperti rabu
Hari terakhir kau dan aku
Duduk di antara kursi kosong
Diam sepakat meniadakan
Kilasan-kilasan
Kilometer sembilan
Selalu datang
Terus menggonggong
Terus merongrong
Seperti rokok terbakar
Di sela-sela jari
Kau dan aku
Berjalan mundur
Menuju akhir
Aku aku aku aku aku aku
Aku intip lebih dini ibu dari kitab-kitab
Untuk coba mencuri apa yang masih belum tersingkap
Berat menekan hingga berbusa
Berantakan di beranda
Mendesak dan membentang banyak rupanya
Banyak biasnya
Menengadah ke tempat kau tinggal
Ditumbuhi rambut awan sirus
Memecah kode di atas papirus
Masih ku kerap salah sangka
Hanya kira lelah bahagianya sisifus
Harapan yang hangus
Yang kadang terhapus
Virus atau vaksin
Obat atau toxin
Hampir tak kupercaya cahaya di ujung terowongan
Tak yakin kah ujung jalan atau kereta lain yang datang
Dan kamu kamu kamu kamu kamu
Bantah aku yang tak mampu
Mengukur dengan tepat
Kapan cepat dan kapan lambat
Kapan prasangka dan kapan khurafat
Keragu-raguan jadi ayat-ayat
Yang dirapal sepanjang hayat
Hingga tenang pun tak sempat
Berjuta juta sajak masih tak mampu usir resah
Berpura-pura anjak hanya hasilkan alkisah
Berbunga-bunga aku tebar di atas kubur mimpi-mimpi yang masih basah
Khawatir datang lebih dini
Selalu begitu bila kepala dan hati terpisah
Oleh tebasan pedang gelisah
Oleh kaburnya jurang pemisah
Hari yang lalu dan yang esok
Yang jadi hantu dan jadi momok
Untuk hari ini untuk hari ini
Untuk hari ini untuk hari ini
Untuk hari ini untuk hari ini
Untuk hari ini untuk hari ini
Untuk hari ini untuk hari ini
Tak kusayat leherku untuk hari ini
Tak kuikat nafasku untuk hari ini
Tak kulubangi dadaku untuk hari ini
Tak kuhamtam aspal untuk hari ini
Tak kutenggak racun untuk hari ini
Tak kutenggelamkanku untuk hari ini
Aku rawat gelisahku untuk hari ini
Aku rasa khawatirku untuk hari ini
Tangis menangisku untuk hari ini
Tawa tertawaku untuk hari ini
Untuk aku
Untuk kamu
Untuk hari ini
Sampai kapan kau diam di kepala
Sedang dunia begitu luasnya
Jangan mati membusuk di sana
Biarkan kakimu mengembara
Rasakan getar sinarnya
Nikmati lembut hembusnya
Selami tangis dan tawa
Menarilah bahagia
Yang telah pergi akan selalu terkenang
Dan sambutlah yang akan datang
Yang telah pergi akan selalu terkenang
Dan sambutlah yang akan datang
Rasakan getar sinarnya
Nikmati lembut hembusnya
Selami tangis dan tawa
Menarilah bahagia
"""

LYRICS = [
    line.strip()
    for line in LYRICS_TEXT.strip().splitlines()
    if line.strip()
]

# ============================================================
# AUDIO
# ============================================================

pygame.mixer.init()

if not os.path.exists(AUDIO_FILE):
    raise FileNotFoundError(
        f"MP3 tidak ditemukan:\n{AUDIO_FILE}\n\n"
        "Pastikan MP3 berada di folder yang sama dengan file Python."
    )

pygame.mixer.music.load(AUDIO_FILE)

# ============================================================
# COLORS
# ============================================================

BG = "#090909"
CARD = "#121212"
CARD_2 = "#181818"
WHITE = "#ffffff"
GRAY = "#888888"
DARK_GRAY = "#444444"
ACCENT = "#1ed760"

# ============================================================
# ROOT
# ============================================================

root = tk.Tk()

root.title("Track 8 — The Jeblogs")
root.geometry("1200x760")
root.minsize(900, 600)
root.configure(bg=BG)

try:
    root.state("zoomed")
except:
    pass

# ============================================================
# STATE
# ============================================================

paused = False
playing = False
volume = 0.8

current_index = 0
current_position = 0

sync_mode = False
sync_index = 0
sync_times = []

dragging = False

start_time = None
pause_position = 0

# ============================================================
# LOAD TIMINGS
# ============================================================

def load_timings():

    if not os.path.exists(TIMING_FILE):
        return []

    try:

        with open(TIMING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

    except Exception:
        pass

    return []


sync_times = load_timings()

# ============================================================
# SAVE TIMINGS
# ============================================================

def save_timings():

    try:

        with open(TIMING_FILE, "w", encoding="utf-8") as f:
            json.dump(sync_times, f, indent=4)

        return True

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Gagal menyimpan timings.json:\n{e}"
        )

        return False

# ============================================================
# HELPERS
# ============================================================

def format_time(seconds):

    seconds = max(0, int(seconds))

    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes:02d}:{seconds:02d}"


def get_position():

    if not playing:
        return pause_position

    pos = pygame.mixer.music.get_pos()

    if pos < 0:
        return pause_position

    return pos / 1000


def clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))

# ============================================================
# BACKGROUND
# ============================================================

canvas = tk.Canvas(
    root,
    bg=BG,
    highlightthickness=0
)

canvas.place(
    x=0,
    y=0,
    relwidth=1,
    relheight=1
)

background_blobs = []

for i in range(8):

    x = random.randint(-300, 1200)
    y = random.randint(-300, 800)
    size = random.randint(300, 650)

    blob = canvas.create_oval(
        x,
        y,
        x + size,
        y + size,
        fill="#111111",
        outline=""
    )

    background_blobs.append({
        "id": blob,
        "x": x,
        "y": y,
        "size": size,
        "speed": random.uniform(0.05, 0.2)
    })

# ============================================================
# MAIN CONTENT
# ============================================================

main = tk.Frame(
    root,
    bg=BG
)

main.place(
    relx=0.5,
    rely=0.5,
    anchor="center",
    relwidth=0.92,
    relheight=0.90
)

# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    main,
    bg=BG
)

header.pack(
    fill="x",
    pady=(10, 20)
)

title_frame = tk.Frame(
    header,
    bg=BG
)

title_frame.pack(
    side="left"
)

tk.Label(
    title_frame,
    text="TRACK 8",
    font=("Arial", 24, "bold"),
    fg=WHITE,
    bg=BG
).pack(anchor="w")

tk.Label(
    title_frame,
    text="THE JEBLOGS",
    font=("Arial", 11),
    fg=GRAY,
    bg=BG
).pack(anchor="w")

mode_label = tk.Label(
    header,
    text="LYRICS MODE",
    font=("Arial", 10, "bold"),
    fg=ACCENT,
    bg=BG
)

mode_label.pack(
    side="right",
    padx=15
)

# ============================================================
# LYRICS AREA
# ============================================================

lyrics_frame = tk.Frame(
    main,
    bg=BG
)

lyrics_frame.pack(
    fill="both",
    expand=True
)

lyrics_canvas = tk.Canvas(
    lyrics_frame,
    bg=BG,
    highlightthickness=0
)

lyrics_canvas.pack(
    fill="both",
    expand=True
)

# ============================================================
# LYRIC TEXT OBJECTS
# ============================================================

lyric_objects = []


def rebuild_lyrics():

    global lyric_objects

    lyrics_canvas.delete("all")
    lyric_objects = []

    if not LYRICS:
        lyric_objects.append(
            lyrics_canvas.create_text(
                600,
                300,
                text="Paste lirik lu ke bagian LYRICS_TEXT",
                fill=GRAY,
                font=("Arial", 24, "bold"),
                anchor="center"
            )
        )
        return

    for i, lyric in enumerate(LYRICS):

        obj = lyrics_canvas.create_text(
            600,
            0,
            text=lyric,
            fill=DARK_GRAY,
            font=("Arial", 22, "bold"),
            anchor="center",
            width=900
        )

        lyric_objects.append(obj)


rebuild_lyrics()

# ============================================================
# DRAW LYRICS
# ============================================================

def draw_lyrics():

    if not LYRICS:
        return

    width = lyrics_canvas.winfo_width()
    height = lyrics_canvas.winfo_height()

    center_y = height / 2

    visible_range = 4

    for i, obj in enumerate(lyric_objects):

        distance = i - current_index

        y = center_y + distance * 58

        lyrics_canvas.coords(
            obj,
            width / 2,
            y
        )

        if i == current_index:

            lyrics_canvas.itemconfig(
                obj,
                fill=WHITE,
                font=("Arial", 28, "bold")
            )

        elif abs(distance) == 1:

            lyrics_canvas.itemconfig(
                obj,
                fill="#777777",
                font=("Arial", 21, "bold")
            )

        elif abs(distance) == 2:

            lyrics_canvas.itemconfig(
                obj,
                fill="#444444",
                font=("Arial", 19, "bold")
            )

        elif abs(distance) == 3:

            lyrics_canvas.itemconfig(
                obj,
                fill="#292929",
                font=("Arial", 17, "bold")
            )

        else:

            lyrics_canvas.itemconfig(
                obj,
                fill=BG,
                font=("Arial", 16)
            )

# ============================================================
# FIND CURRENT LYRIC
# ============================================================

def update_current_lyric(position):

    global current_index

    if not sync_times:
        return

    if len(sync_times) != len(LYRICS):
        return

    index = 0

    for i, timestamp in enumerate(sync_times):

        if position >= timestamp:
            index = i
        else:
            break

    current_index = index

# ============================================================
# CONTROLS
# ============================================================

controls = tk.Frame(
    main,
    bg=BG
)

controls.pack(
    fill="x",
    pady=(15, 5)
)

# ============================================================
# PROGRESS
# ============================================================

progress_frame = tk.Frame(
    controls,
    bg=BG
)

progress_frame.pack(
    fill="x"
)

progress = tk.Canvas(
    progress_frame,
    height=5,
    bg="#333333",
    highlightthickness=0
)

progress.pack(
    fill="x",
    padx=5
)

progress_bar = progress.create_rectangle(
    0,
    0,
    0,
    5,
    fill=ACCENT,
    outline=""
)

time_frame = tk.Frame(
    controls,
    bg=BG
)

time_frame.pack(
    fill="x",
    pady=(6, 10)
)

current_time_label = tk.Label(
    time_frame,
    text="00:00",
    fg=GRAY,
    bg=BG,
    font=("Arial", 10)
)

current_time_label.pack(side="left")

duration_label = tk.Label(
    time_frame,
    text="--:--",
    fg=GRAY,
    bg=BG,
    font=("Arial", 10)
)

duration_label.pack(side="right")

# ============================================================
# BUTTON FRAME
# ============================================================

button_frame = tk.Frame(
    controls,
    bg=BG
)

button_frame.pack(
    pady=5
)


def style_button(text, command, width=8):

    return tk.Button(
        button_frame,
        text=text,
        command=command,
        width=width,
        bg="#151515",
        fg=WHITE,
        activebackground="#252525",
        activeforeground=WHITE,
        relief="flat",
        bd=0,
        font=("Arial", 12, "bold"),
        cursor="hand2"
    )

# ============================================================
# PLAY / PAUSE
# ============================================================

def play_pause():

    global paused
    global playing
    global pause_position

    if not playing:

        pygame.mixer.music.play(
            start=pause_position
        )

        playing = True
        paused = False

        return

    if paused:

        pygame.mixer.music.unpause()

        paused = False

    else:

        pygame.mixer.music.pause()

        pause_position = get_position()
        paused = True


# ============================================================
# STOP
# ============================================================

def stop():

    global playing
    global paused
    global pause_position
    global current_index

    pygame.mixer.music.stop()

    playing = False
    paused = False
    pause_position = 0
    current_index = 0

# ============================================================
# PREVIOUS LINE
# ============================================================

def previous_line():

    global current_index
    global pause_position

    if current_index <= 0:
        return

    current_index -= 1

    if sync_times and current_index < len(sync_times):

        pause_position = sync_times[current_index]

        pygame.mixer.music.play(
            start=pause_position
        )

        pygame.mixer.music.pause()

# ============================================================
# NEXT LINE
# ============================================================

def next_line():

    global current_index
    global pause_position

    if current_index >= len(LYRICS) - 1:
        return

    current_index += 1

    if sync_times and current_index < len(sync_times):

        pause_position = sync_times[current_index]

        pygame.mixer.music.play(
            start=pause_position
        )

        pygame.mixer.music.pause()

# ============================================================
# VOLUME
# ============================================================

def volume_up():

    global volume

    volume = clamp(
        volume + 0.1,
        0,
        1
    )

    pygame.mixer.music.set_volume(volume)


def volume_down():

    global volume

    volume = clamp(
        volume - 0.1,
        0,
        1
    )

    pygame.mixer.music.set_volume(volume)

# ============================================================
# SYNC MODE
# ============================================================

def enter_sync_mode():

    global sync_mode
    global sync_index
    global sync_times

    if not LYRICS:
        messagebox.showwarning(
            "Lirik kosong",
            "Paste lirik lu terlebih dahulu."
        )
        return

    answer = messagebox.askyesno(
        "Sync Mode",
        "Sync Mode akan menghapus timing lama dan membuat timing baru.\n\n"
        "Cara kerja:\n\n"
        "1. Lagu dimulai dari awal.\n"
        "2. Saat baris sedang dinyanyikan, tekan ENTER.\n"
        "3. Program mencatat timestamp.\n"
        "4. Tekan ENTER untuk setiap baris.\n\n"
        "Mulai sinkronisasi sekarang?"
    )

    if not answer:
        return

    sync_mode = True
    sync_index = 0
    sync_times = []

    mode_label.config(
        text="SYNC MODE — ENTER",
        fg="#ffcc00"
    )

    current_index = 0

    pygame.mixer.music.stop()
    pygame.mixer.music.play()

    root.focus_force()

# ============================================================
# REGISTER SYNC TIMESTAMP
# ============================================================

def register_sync(event=None):

    global sync_index

    if not sync_mode:
        return

    position = pygame.mixer.music.get_pos() / 1000

    if sync_index >= len(LYRICS):

        finish_sync()
        return

    sync_times.append(
        round(position, 3)
    )

    print(
        f"[SYNC] "
        f"{sync_index + 1}/{len(LYRICS)} "
        f"{position:.3f}s "
        f"→ {LYRICS[sync_index]}"
    )

    sync_index += 1

    if sync_index >= len(LYRICS):

        finish_sync()

# ============================================================
# FINISH SYNC
# ============================================================

def finish_sync():

    global sync_mode

    sync_mode = False

    pygame.mixer.music.pause()

    save_timings()

    mode_label.config(
        text="LYRICS MODE",
        fg=ACCENT
    )

    messagebox.showinfo(
        "Sync selesai",
        "Sinkronisasi selesai!\n\n"
        "Timing disimpan ke:\n"
        "timings.json"
    )

# ============================================================
# SYNC INDICATOR
# ============================================================

sync_hint = tk.Label(
    root,
    text="",
    fg="#ffcc00",
    bg=BG,
    font=("Arial", 11, "bold")
)

# ============================================================
# BUTTONS
# ============================================================

style_button(
    "⏮",
    previous_line,
    5
).pack(side="left", padx=4)

play_button = style_button(
    "▶ / ❚❚",
    play_pause,
    10
)

play_button.pack(
    side="left",
    padx=4
)

style_button(
    "⏹",
    stop,
    5
).pack(side="left", padx=4)

style_button(
    "⏭",
    next_line,
    5
).pack(side="left", padx=4)

style_button(
    "−",
    volume_down,
    5
).pack(side="left", padx=(20, 4))

style_button(
    "+",
    volume_up,
    5
).pack(side="left", padx=4)

style_button(
    "SYNC",
    enter_sync_mode,
    8
).pack(side="left", padx=(20, 4))

# ============================================================
# PROGRESS CLICK
# ============================================================

def seek(event):

    global pause_position

    if sync_mode:
        return

    width = progress.winfo_width()

    if width <= 0:
        return

    ratio = event.x / width

    ratio = clamp(
        ratio,
        0,
        1
    )

    # Estimasi durasi menggunakan audio file.
    try:

        sound = pygame.mixer.Sound(AUDIO_FILE)
        duration = sound.get_length()

    except:
        return

    new_position = duration * ratio

    pause_position = new_position

    pygame.mixer.music.play(
        start=new_position
    )

    if paused:
        pygame.mixer.music.pause()

progress.bind(
    "<Button-1>",
    seek
)

# ============================================================
# KEYBOARD
# ============================================================

root.bind(
    "<space>",
    lambda event: play_pause()
)

root.bind(
    "<Left>",
    lambda event: previous_line()
)

root.bind(
    "<Right>",
    lambda event: next_line()
)

root.bind(
    "<Up>",
    lambda event: volume_up()
)

root.bind(
    "<Down>",
    lambda event: volume_down()
)

root.bind(
    "<Return>",
    register_sync
)

root.bind(
    "<Escape>",
    lambda event: root.destroy()
)

# ============================================================
# GET DURATION
# ============================================================

try:

    sound = pygame.mixer.Sound(AUDIO_FILE)
    duration = sound.get_length()

    duration_label.config(
        text=format_time(duration)
    )

except:

    duration = 0

# ============================================================
# UPDATE UI
# ============================================================

def update_ui():

    global current_position

    current_position = get_position()

    # --------------------------------------------------------
    # NORMAL MODE
    # --------------------------------------------------------

    if not sync_mode:

        if sync_times:

            update_current_lyric(
                current_position
            )

    # --------------------------------------------------------
    # SYNC MODE
    # --------------------------------------------------------

    else:

        if sync_index < len(LYRICS):

            mode_label.config(
                text=f"SYNC {sync_index + 1}/{len(LYRICS)} — ENTER",
                fg="#ffcc00"
            )

            current_index = sync_index

    # --------------------------------------------------------
    # DRAW LYRICS
    # --------------------------------------------------------

    draw_lyrics()

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    current_time_label.config(
        text=format_time(current_position)
    )

    if duration > 0:

        ratio = clamp(
            current_position / duration,
            0,
            1
        )

        width = progress.winfo_width()

        progress.coords(
            progress_bar,
            0,
            0,
            width * ratio,
            5
        )

    # --------------------------------------------------------
    # ANIMATION
    # --------------------------------------------------------

    animate_background()

    # --------------------------------------------------------
    # LOOP
    # --------------------------------------------------------

    root.after(
        50,
        update_ui
    )

# ============================================================
# BACKGROUND ANIMATION
# ============================================================

animation_time = 0


def animate_background():

    global animation_time

    animation_time += 0.015

    for i, blob in enumerate(background_blobs):

        offset_x = math.sin(
            animation_time * blob["speed"] * 10 + i
        ) * 20

        offset_y = math.cos(
            animation_time * blob["speed"] * 8 + i
        ) * 20

        x = blob["x"] + offset_x
        y = blob["y"] + offset_y

        size = blob["size"]

        canvas.coords(
            blob["id"],
            x,
            y,
            x + size,
            y + size
        )

# ============================================================
# START
# ============================================================

update_ui()

root.mainloop()