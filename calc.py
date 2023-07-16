import sys
import random
import pandas as pd
from PyQt5.QtWidgets import (
    QFrame,
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer
import pygame
from PyQt5.QtMultimedia import QSound
from datetime import datetime

from typing import Literal


class MathGame(QWidget):
    def __init__(self, type_: Literal["+", "-", "*"] = "+"):
        super().__init__()

        pairs = {"+": "더하기", "-": "빼기", "*": "곱하기"}
        self.setWindowTitle(f"{pairs.get(type_)} 게임")

        self.type_ = type_
        self.correct_answers = 0
        self.wrong_answers = 0
        self.questions = []
        self.submitted_answers = []
        self.question_times = []

        pygame.mixer.init()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.time_label = QLabel("남은 시간: 10초")
        self.time_label.setStyleSheet("font-size: 24px")
        top_layout.addWidget(self.time_label, alignment=Qt.AlignRight)

        layout.addLayout(top_layout)

        self.question_layout = QVBoxLayout()
        self.num1_label = QLabel()
        self.num1_label.setAlignment(Qt.AlignRight)
        self.num1_label.setStyleSheet("font-size: 72px")
        self.question_layout.addWidget(self.num1_label)

        self.num2_and_operator_label = QLabel()
        self.num2_and_operator_label.setAlignment(Qt.AlignRight)
        self.num2_and_operator_label.setStyleSheet("font-size: 72px")
        self.question_layout.addWidget(self.num2_and_operator_label)

        layout.addLayout(self.question_layout)

        self.answer_input = QLineEdit()
        self.answer_input.setAlignment(Qt.AlignCenter)
        self.answer_input.setStyleSheet("font-size: 36px")
        self.answer_input.returnPressed.connect(self.check_answer)
        layout.addWidget(self.answer_input)

        submit_button = QPushButton("제출")
        submit_button.setStyleSheet("font-size: 24px")
        submit_button.clicked.connect(self.check_answer)
        layout.addWidget(submit_button)

        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 24px")
        layout.addWidget(self.score_label)

        self.setLayout(layout)
        self.new_question()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1500)

    def new_question(self):
        self.num1 = random.randint(1, 20)
        self.num2 = random.randint(1, 20)

        if self.type_ == "-":
            self.num1, self.num2 = max(self.num1, self.num2), min(self.num1, self.num2)

        # self.question_label.setText(f'{self.num1} {self.type_} {self.num2} =')
        self.num1_label.setText(f"{str(self.num1)}")
        self.num2_and_operator_label.setText(f"{self.type_} {str(self.num2)}")  # 연산자를 두 번째 숫자 앞에 추가, 우측 정렬을 위해 공백 추가
        self.reset_timer()

        self.reset_timer()

        self.question_start_time = self.time_remaining

    def check_answer(self):
        try:
            user_answer = int(self.answer_input.text())
        except ValueError:
            QMessageBox.warning(self, "경고", "숫자를 입력하세요.")
            return

        self.questions.append(f"{self.num1} {self.type_} {self.num2}")
        self.submitted_answers.append(user_answer)
        self.question_times.append(self.question_start_time - self.time_remaining)

        match self.type_:
            case "+":
                correct = self.num1 + self.num2
            case "-":
                correct = self.num1 - self.num2
            case "*":
                correct = self.num1 * self.num2

        if user_answer == correct:
            QSound.play("good.wav")

            self.correct_answers += 1
            self.answer_input.clear()
            self.new_question()

        else:
            QSound.play("bad.wav")
            self.wrong_answers += 1
            self.answer_input.clear()

        self.update_score()

    def update_score(self):
        self.score_label.setText(f"정답: {self.correct_answers}, 오답: {self.wrong_answers}")

    def update_timer(self):
        self.time_remaining -= 1
        self.time_label.setText(f"남은 시간: {self.time_remaining}초")

        if self.time_remaining == 0:
            QMessageBox.warning(self, "시간 초과", "시간이 초과되었습니다. 새로운 문제를 풀어보세요.")
            self.wrong_answers += 1
            self.new_question()
            self.update_score()

    def reset_timer(self):
        if self.num1 + self.num2 > 20:
            self.time_remaining = 30
        else:
            self.time_remaining = 20
        self.time_label.setText(f"남은 시간: {self.time_remaining}초")

    def closeEvent(self, event):
        self.export_to_excel()
        event.accept()

    def export_to_excel(self):
        data = {"문제": self.questions, "제출한 답": self.submitted_answers, "문제 풀이 시간(초)": self.question_times}

        df = pd.DataFrame(data)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%y%m%d_%H%M")
        file_name = f"{formatted_time}.xlsx"

        df.to_excel(file_name, index=False)
        print(f"{file_name} 에 저장되었습니다.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MathGame(type_="+")
    game.show()

    sys.exit(app.exec_())
