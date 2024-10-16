import PySimpleGUI as sg
from string import ascii_uppercase
from random import choice
import winsound

winsound.Beep(60, 60)
MAX_WRONG_GUESSES = 6

class Hangman:
    def __init__(self) -> None:
        self._window = sg.Window(
            title="Hangman",
            layout=[
                [
                    self._build_canvas_frame(),
                    self._build_letters_frame(),
                ],
                [
                    self._build_guessed_words_frame(),
                ],
                [
                    self._build_action_buttons_frame(),
                ],
            ],
            finalize=True,
            margins=(150, 150),
        )
        self._canvas = self._window["-CANVAS-"]
        self._new_game()
        self.quit = False
        self._played_games = 0
        self._won_games = 0

    def read_event(self):
        event = self._window.read()
        event_id = event[0] if event is not None else None
        return event_id

    def process_event(self, event):
        if event[:8] == "-letter-":
            self._play(letter=event[8])
        elif event == "-RESTART-":
            self._restart_game()
        elif event == "-NEW-":
            self._new_game()

    def is_over(self):
        return any(
            [
                self._wrong_guesses == MAX_WRONG_GUESSES,
                set(self._target_word) <= self._guessed_letters,
            ]
        )

    def check_winner(self):
        self._played_games += 1
        answer = sg.PopupYesNo(
            "You've Won! Congratulations!\n"
            f"That's {self._won_games + 1} out of {self._played_games}!\n"
            "Another Round?",
            title="WINNER!"
        ) if self._wrong_guesses < MAX_WRONG_GUESSES else sg.PopupYesNo(
            f"You've lost! The word was '{self._target_word}'.\n"
            f"That's {self._won_games} out of {self._played_games}!\n"
            "Another Round?",
            title="Oops! You will get it next time!"
        )
        self.quit = answer == "No"
        if not self.quit:
            self._new_game()

    def close(self):
        self._window.close()

    def _play_sound(self, sound_file):
        winsound.PlaySound(sound_file, winsound.SND_ASYNC | winsound.SND_NODEFAULT)

    def _build_canvas_frame(self):
        return sg.Frame(
            "Hangman",
            [
                [
                    sg.Graph(
                        key="-CANVAS-",
                        canvas_size=(200, 400),
                        graph_bottom_left=(0, 0),
                        graph_top_right=(200, 400),
                    )
                ]
            ]
        )

    def _build_letters_frame(self):
        letter_groups = [
            ascii_uppercase[i: i + 4] for i in range(0, len(ascii_uppercase), 4)
        ]
        letter_buttons = [
            [
                sg.Button(
                    button_text=f" {letter} ",
                    font="Courier 20",
                    border_width=0,
                    button_color=(None, sg.theme_background_color()),
                    key=f"-letter-{letter}-",
                    enable_events=True,
                )
                for letter in row
            ]
            for row in letter_groups
        ]

        overlays = [
            [
                sg.Text(
                    text="",
                    key=f"-overlay-{letter}-",
                    font="Courier 20",
                    justification="center",
                    background_color=sg.theme_background_color(),
                    visible=False,
                )
                for letter in row
            ]
            for row in letter_groups
        ]

        return sg.Frame(
            "Letters",
            [
                [
                    sg.Column(
                        [
                            letter_buttons[i] + overlays[i]
                        ],
                        justification="center",
                        key=f"-letter-column-{i}-",
                    )
                ]
                for i in range(len(letter_buttons))
            ],
        )

    def _build_guessed_words_frame(self):
        return sg.Frame(
            "",
            [
                [
                    sg.Text(
                        key="-DISPLAY-WORD-",
                        font="Courier 20",
                    )
                ]
            ],
            element_justification="center"
        )

    def _build_action_buttons_frame(self):
        return sg.Frame(
            "",
            [
                [
                    sg.Sizer(h_pixels=90),
                    sg.Button(
                        button_text="New Game",
                        key="-NEW-",
                        font="Any 20",
                        enable_events=True,
                    ),
                    sg.Sizer(h_pixels=60),
                    sg.Button(
                        button_text="Restart",
                        key="-RESTART-",
                        font="Any 20",
                        enable_events=True,
                    ),
                    sg.Sizer(h_pixels=60),
                    sg.Button(
                        button_text="Quit",
                        key="-QUIT-",
                        font="Any 20",
                        enable_events=True,
                    ),
                    sg.Sizer(h_pixels=90)
                ]
            ],
            font="Any 20",
        )

    def _draw_scaffold(self):
        lines = [
            ((40, 55), (180, 55), 10),
            ((165, 60), (165, 365), 10),
            ((160, 360), (100, 360), 10),
            ((100, 365), (100, 330), 10),
            ((100, 330), (100, 310), 1),
        ]
        for *points, width in lines:
            self._canvas.DrawLine(*points, color="black", width=width)

    def _draw_hanged_man(self):
        head = (100, 290)
        torso = [((100, 270), (100, 170))]
        left_arm = [
            ((100, 250), (80, 250)),
            ((80, 250), (60, 210)),
            ((60, 210), (60, 190)),
        ]
        right_arm = [
            ((100, 250), (120, 250)),
            ((120, 250), (140, 210)),
            ((140, 210), (140, 190)),
        ]
        left_leg = [
            ((100, 170), (80, 170)),
            ((80, 170), (70, 140)),
            ((70, 140), (70, 80)),
            ((70, 80), (60, 80)),
        ]
        right_leg = [
            ((100, 170), (120, 170)),
            ((120, 170), (130, 140)),
            ((130, 140), (130, 80)),
            ((130, 80), (140, 80)),
        ]
        body = [
            torso,
            left_arm,
            right_arm,
            left_leg,
            right_leg,
        ]
        if self._wrong_guesses == 1:
            self._canvas.DrawCircle(
                head,
                20,
                line_color="white",
                line_width=2,
            )
        elif self._wrong_guesses > 1:
            for part in body[self._wrong_guesses - 2]:
                self._canvas.DrawLine(*part, color="white", width=2)

    def _select_word(self):
        with open("g:/dev/hangman/words.txt", mode="r", encoding="utf-8") as words:
            word_list = words.readlines()
        return choice(word_list).strip().upper()

    def _build_guessed_word_frame(self):
        current_letters = [letter if letter in self._guessed_letters else "_" for letter in self._target_word]
        return " ".join(current_letters)

    def _new_game(self):
        self._target_word = self._select_word()
        self._restart_game()

    def _restart_game(self):
        self._guessed_letters = set()
        self._wrong_guesses = 0
        self._guessed_word = self._build_guessed_word_frame()
        # RESTART GUI
        self._canvas.erase()
        self._draw_scaffold()
        for letter in ascii_uppercase:
            self._window[f"-letter-{letter}-"].update(disabled=False)
        self._window["-DISPLAY-WORD-"].update(self._guessed_word)

    def _play(self, letter):
        if letter not in self._target_word:
            self._wrong_guesses += 1
        self._guessed_letters.add(letter)
        self._guessed_word = self._build_guessed_word_frame()
        # UPDATE GUI
        self._window[f"-letter-{letter}-"].update(disabled=True)
        overlay_key = f"-overlay-{letter}-"
        self._window[overlay_key].update("X")  # Display an X over the guessed letter
        self._window["-DISPLAY-WORD-"].update(self._guessed_word)
        self._draw_hanged_man()
        self._play_sound("g:/dev/hangman/button_click.wav")

if __name__ == "__main__":
    game = Hangman()
    while not game.quit:
        event_id = game.read_event()
        if event_id in {sg.WIN_CLOSED, "-QUIT-"}:
            game.quit = True
            break
        game.process_event(event_id)
        if game.is_over() and not game.quit:
            game.check_winner()
    game.close()
