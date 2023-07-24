import sys
import random
import pandas as pd
from PyQt5.QtWidgets import (
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
from enum import Enum

from typing import Literal


class MathGame(QWidget):
    def __init__(self, operator: Literal["+", "-", "*"] = "+", level: int = 1):
        super().__init__()

        pairs = {"+": "더하기", "-": "빼기", "*": "곱하기"}
        self.setWindowTitle(f"{pairs.get(operator)} 게임")
        self.level = level

        self.problem_generator = MathProblemFactory.get(operator, level=level)
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

        self.num2_label = QLabel()
        self.num2_label.setAlignment(Qt.AlignRight)
        self.num2_label.setStyleSheet("font-size: 72px")
        self.question_layout.addWidget(self.num2_label)

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

    @property
    def operator(self):
        return self.problem_generator.OPERATOR

    def new_question(self):
        values = self.problem_generator.get_terms()

        self.num1_label.setText(f"{str(values[0])}")
        self.num2_label.setText(f"{self.operator} {str(values[1])}")
        self.reset_timer()

        self.question_start_time = self.time_remaining

    def check_answer(self):
        try:
            user_answer = int(self.answer_input.text())
        except ValueError:
            QMessageBox.warning(self, "경고", "숫자를 입력하세요.")
            return

        self.questions.append(self.operator.join([str(value) for value in self.problem_generator.terms]))
        self.submitted_answers.append(user_answer)
        self.question_times.append(self.question_start_time - self.time_remaining)

        if user_answer == self.problem_generator.get_answer():
            QSound.play("assets/good.wav")

            self.correct_answers += 1
            self.answer_input.clear()
            self.new_question()

        else:
            QSound.play("assets/bad.wav")
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
        if self.problem_generator.get_answer() > 20:
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


class MathProblemFactory:
    @staticmethod
    def get(operator: Literal["+", "-", "*"], level: int):
        if operator == "+":
            return PlusProblemGenerator(level=level)
        else:
            raise NotImplementedError(operator)


class PlusProblemGenerator:
    OPERATOR = "+"

    def __init__(self, level: int, term_num: int = 2):
        self.level = level
        self.term_num = term_num
        self._terms = []

    def get_terms(self) -> list[int]:
        if self.level == 1:
            self._terms = [random.randint(1, 9) for _ in range(self.term_num)]
        elif self.level == 2:
            self._terms = [random.randint(1, 19) for _ in range(self.term_num)]
        elif self.level == 3:
            self._terms = [random.randint(10, 50) for _ in range(self.term_num)]

        return self.terms

    def get_answer(self) -> int:
        return sum(self.terms)

    @property
    def terms(self):
        return self._terms


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MathGame(operator="+")
    game.show()

    sys.exit(app.exec_())
