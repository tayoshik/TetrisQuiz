import tkinter as tk
from tkinter import messagebox, ttk
import random
import json

class Tetris:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tetris with Quiz")
        
        # ゲーム設定
        self.BOARD_WIDTH = 10
        self.BOARD_HEIGHT = 20
        self.BLOCK_SIZE = 30
        self.SHAPES = [
            [[1, 1, 1, 1]],  # I
            [[1, 1], [1, 1]],  # O
            [[1, 1, 1], [0, 1, 0]],  # T
            [[1, 1, 1], [1, 0, 0]],  # L
            [[1, 1, 1], [0, 0, 1]],  # J
            [[1, 1, 0], [0, 1, 1]],  # S
            [[0, 1, 1], [1, 1, 0]]   # Z
        ]
        self.COLORS = ['cyan', 'yellow', 'purple', 'orange', 'blue', 'green', 'red']
        
        # ゲーム状態
        self.board = [[0 for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_shape_index = 0
        self.score = 0
        self.quiz_score = 0  # クイズの得点
        self.is_game_over = False  # ゲームオーバーフラグ
        
        # キャンバスの作成
        self.canvas = tk.Canvas(
            self.root,
            width=self.BLOCK_SIZE * self.BOARD_WIDTH,
            height=self.BLOCK_SIZE * self.BOARD_HEIGHT,
            bg='black'
        )
        self.canvas.grid(row=0, column=0)
        
        # クイズセクションの作成
        self.quiz_frame = tk.Frame(self.root, bg='white', width=200)
        self.quiz_frame.grid(row=0, column=1, sticky="ns")
        self.create_quiz_ui()
        
        # スコア表示
        self.score_label = tk.Label(self.root, text=f"Tetris Score: {self.score}")
        self.score_label.grid(row=1, column=0, sticky="w")
        
        self.quiz_score_label = tk.Label(self.quiz_frame, text=f"Quiz Score: {self.quiz_score}")
        self.quiz_score_label.pack(pady=10)
        
        # キー入力のバインド
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Down>', self.move_down)
        self.root.bind('<Up>', self.rotate)
        
        # ゲームスタート
        self.new_piece()
        self.update()
    
    def move_left(self, event=None):
        """ピースを左に移動"""
        if self.current_piece and self.is_valid_move(self.current_piece, self.current_x - 1, self.current_y):
            self.current_x -= 1
            self.draw()

    def move_right(self, event=None):
        """ピースを右に移動"""
        if self.current_piece and self.is_valid_move(self.current_piece, self.current_x + 1, self.current_y):
            self.current_x += 1
            self.draw()

    def move_down(self, event=None):
        """ピースを下に移動"""
        if self.current_piece and self.is_valid_move(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
            self.draw()
        else:
            self.merge_piece()
            self.clear_lines()
            self.new_piece()
            self.draw()

    def rotate(self, event=None):
        """ピースを回転"""
        if self.current_piece:
            rotated = list(zip(*self.current_piece[::-1]))
            if self.is_valid_move(rotated, self.current_x, self.current_y):
                self.current_piece = rotated
                self.draw()
    
    def update(self):
        """ゲームの更新（自動落下）"""
        if not self.is_game_over:
            self.move_down()  # ピースを1マス下に移動
            self.root.after(1000, self.update)  # 1秒ごとに再実行

    def is_valid_move(self, piece, x, y):
        """移動が有効かチェック"""
        for piece_y, row in enumerate(piece):
            for piece_x, cell in enumerate(row):
                if cell:
                    new_x, new_y = x + piece_x, y + piece_y
                    # ボード外チェック
                    if (new_x < 0 or new_x >= self.BOARD_WIDTH or
                        new_y >= self.BOARD_HEIGHT or
                        (new_y >= 0 and self.board[new_y][new_x])):
                        return False
        return True

    def draw(self):
        """ゲーム画面の描画"""
        self.canvas.delete('all')  # 既存の描画をクリア
        
        # 固定されたブロックの描画
        for y in range(self.BOARD_HEIGHT):
            for x in range(self.BOARD_WIDTH):
                if self.board[y][x]:
                    self.draw_block(x, y, self.COLORS[self.board[y][x] - 1])
        
        # 現在のピースの描画
        if self.current_piece:
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        self.draw_block(
                            self.current_x + x,
                            self.current_y + y,
                            self.COLORS[self.current_shape_index]
                        )
    
    def draw_block(self, x, y, color):
        """ブロックを描画"""
        self.canvas.create_rectangle(
            x * self.BLOCK_SIZE,
            y * self.BLOCK_SIZE,
            (x + 1) * self.BLOCK_SIZE,
            (y + 1) * self.BLOCK_SIZE,
            fill=color,
            outline='white'
        )

    def merge_piece(self):
        """現在のピースをボードに固定"""
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_y + y][self.current_x + x] = self.current_shape_index + 1

        # 新しいピースを生成
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        """完成したラインを削除"""
        lines_cleared = 0
        y = self.BOARD_HEIGHT - 1
        while y >= 0:
            if all(self.board[y]):  # 現在の行がすべて埋まっている場合
                lines_cleared += 1
                # 行を上からずらす
                for move_y in range(y, 0, -1):
                    self.board[move_y] = self.board[move_y - 1][:]
                self.board[0] = [0] * self.BOARD_WIDTH  # 一番上の行を空にする
            else:
                y -= 1  # 次の行を確認
        
        # スコア更新
        self.score += lines_cleared * 100
        self.score_label.config(text=f"Tetris Score: {self.score}")


    def create_quiz_ui(self):
        """クイズセクションのUI作成"""
        self.quiz_label = tk.Label(self.quiz_frame, text="Quiz", font=("Arial", 16))
        self.quiz_label.pack(pady=10)
        
        self.quiz_question = tk.Label(self.quiz_frame, text="", wraplength=180, justify="left")
        self.quiz_question.pack(pady=10)
        
        self.quiz_var = tk.IntVar(value=-1)
        self.quiz_options = []
        for i in range(10):
            radio = ttk.Radiobutton(self.quiz_frame, text="", variable=self.quiz_var, value=i)
            radio.pack(anchor="w")
            self.quiz_options.append(radio)
        
        self.quiz_button = tk.Button(self.quiz_frame, text="Submit Answer", command=self.submit_answer)
        self.quiz_button.pack(pady=10)
        
        # 問題のセットアップ
        self.load_quiz()
        self.next_question()
              
    def load_quiz(self):
        """クイズの問題をJSONから読み込む"""
        try:
            with open("quiz.json", "r", encoding="utf-8") as file:
                base_questions = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "quiz.json not found!")
            self.root.destroy()
            return
        
        self.quiz_data = []
        for _ in range(10000):
            question = random.choice(base_questions)
            options = question["options"][:]
            random.shuffle(options)
            correct_index = options.index(question["options"][question["answer"]])
            self.quiz_data.append({
                "question": question["question"],
                "options": options,
                "answer": correct_index
            })

        self.current_question_index = 0
    
    def next_question(self):
        """次のクイズを表示"""
        if self.current_question_index < len(self.quiz_data):
            question_data = self.quiz_data[self.current_question_index]
            self.quiz_question.config(text=question_data["question"])
            for i, option in enumerate(question_data["options"]):
                self.quiz_options[i].config(text=option)
            self.quiz_var.set(-1)  # ラジオボタンのリセット
        else:
            messagebox.showinfo("Quiz", "No more questions!")
    
    def submit_answer(self):
        """クイズの回答をチェック"""
        if self.quiz_var.get() == -1:
            messagebox.showwarning("Quiz", "Please select an answer!")
            return
        
        question_data = self.quiz_data[self.current_question_index]
        if self.quiz_var.get() == question_data["answer"]:
            self.quiz_score += 1
            messagebox.showinfo("Quiz", "Correct!")
        else:
            self.quiz_score -= 1
            messagebox.showinfo("Quiz", "Wrong!")
        
        # スコア表示を更新
        self.quiz_score_label.config(text=f"Quiz Score: {self.quiz_score}")
        
        # スコアが4になったらI型ピースを落とす
        if self.quiz_score == 4:
            self.add_bonus_piece()
            self.quiz_score = 0  # ボーナス後にリセット
        
        # 次の問題へ
        self.current_question_index += 1
        self.next_question()
        
    def add_bonus_piece(self):
        """ボーナスピース（I型）を追加"""
        self.current_piece = self.SHAPES[0]  # I型ピース
        self.current_x = self.BOARD_WIDTH // 2 - 1
        self.current_y = 0

    # その他のゲームロジック（new_piece, move_down, move_left など）はそのまま
    def new_piece(self):
        self.current_shape_index = random.randint(0, len(self.SHAPES) - 1)
        self.current_piece = self.SHAPES[self.current_shape_index]
        self.current_x = self.BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = Tetris()
    game.run()
