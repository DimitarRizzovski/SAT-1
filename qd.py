from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap, QIntValidator
from PyQt6.QtCore import QPointF

import mgen
import random
from matplotlib import pyplot as plt
from io import BytesIO




class EditableTextItem(QGraphicsPixmapItem):
    def __init__(self, equation_type, difficulty, answer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.equation_type = equation_type  # Store the equation type
        self.difficulty = difficulty  # Store the difficulty level
        self.drag_offset = QPointF(0, 0)  # Store the offset of the mouse click
        self.answer = answer  # Add 'answer' attribute here

    def mouseDoubleClickEvent(self, event):
        try:
            # Create a dialog for input
            dialog = QDialog()
            dialog.setWindowTitle(self.equation_type)  # Set the title to the equation type
            layout = QVBoxLayout()

            # Create labels for the question, answer, and difficulty
            question_label = QLabel(f"Question: {self.text}")
            answer_label = QLabel(f"Answer: {self.answer}")  # Assuming 'self.answer' contains the answer
            difficulty_label = QLabel(
                f"Difficulty: {self.difficulty}")  # Assuming 'self.difficulty' contains the difficulty level

            layout.addWidget(question_label)
            layout.addWidget(answer_label)
            layout.addWidget(difficulty_label)

            # Create OK button
            ok_btn = QPushButton('OK')
            ok_btn.clicked.connect(dialog.accept)
            layout.addWidget(ok_btn)

            # Set dialog layout
            dialog.setLayout(layout)

            # Show dialog and wait for user to press OK
            dialog.exec()
        except Exception as e:
            print(f"An error occurred: {e}")

    def mousePressEvent(self, event):
        try:
            # Store the offset of the mouse click relative to the top-left corner of the box
            self.drag_offset = event.pos() - self.boundingRect().topLeft()
            super().mousePressEvent(event)
        except Exception as e:
            print(e)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            new_pos = event.scenePos() - self.drag_offset
            self.setPos(new_pos)
        else:
            super().mouseMoveEvent(event)

    def setPlainText(self, text):
        self.text = text
        fig = plt.figure(figsize=(6, 5))  # Adjust the figure size here

        text_obj = plt.text(0, 0, f'${text}$', size=20, ha='center', va='center')  # Align text to the left
        plt.axis('off')

        renderer = fig.canvas.get_renderer()
        bbox = text_obj.get_window_extent(renderer)

        # Adjust the figure size to make the bounding box slightly bigger
        fig.set_size_inches(bbox.width / renderer.dpi * 0.5, bbox.height / renderer.dpi * 0.5)

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')  # Remove padding around the figure
        plt.close(fig)
        buf.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        self.setPixmap(pixmap)

class ExampleTextItem(QGraphicsPixmapItem):
    def __init__(self, equation_type, difficulty, answer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equation_type = equation_type  # Store the equation type
        self.difficulty = difficulty  # Store the difficulty level
        self.answer = answer  # Add 'answer' attribute here

    def setPlainText(self, text):
        self.text = text
        fig = plt.figure(figsize=(6, 5))  # Adjust the figure size here

        # Align text to the left and set color to black
        text_obj = plt.text(-10, 0.5, f'${text}$', size=15, ha='left', va='center', color='black')

        # Add the answer below the question in smaller red text
        plt.text(-10, -2, f'Answer: {self.answer}', size=10, ha='left', va='center', color='red')

        plt.axis('off')

        renderer = fig.canvas.get_renderer()
        bbox = text_obj.get_window_extent(renderer)

        # Adjust the figure size to make the bounding box slightly bigger
        fig.set_size_inches(bbox.width / renderer.dpi * 0.5, bbox.height / renderer.dpi * 0.5)

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')  # Remove padding around the figure
        plt.close(fig)
        buf.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        self.setPixmap(pixmap)


def linear_equation_popup(self):
    try:
        diff = "Easy"
        dialog = loadUi('questiondialog.ui')
        dialog.setFixedSize(dialog.size())
        dialog.cancelButton.clicked.connect(dialog.close)
        scene = QGraphicsScene()
        dialog.questionView.setScene(scene)
        for i in range(4):
            difficulty, equation_text, answer = mgen.generate_linear_equation(diff)
            equation_item = ExampleTextItem(equation_text, difficulty, answer)
            equation_item.setPlainText(equation_text)
            equation_item.setPos(0, 20 + i * 100)  # Changed from 10 to 50
            scene.addItem(equation_item)
        validator = QIntValidator(0, 99)
        dialog.numofqueLine.setValidator(validator)
        dialog.okButton.setEnabled(False)
        dialog.addButton.setEnabled(False)

        def enable_buttons():
            if dialog.numofqueLine.text():
                dialog.okButton.setEnabled(True)
                dialog.addButton.setEnabled(True)
            else:
                dialog.okButton.setEnabled(False)
                dialog.addButton.setEnabled(False)

        dialog.numofqueLine.textChanged.connect(enable_buttons)
        button_group = QButtonGroup()
        button_group.addButton(dialog.easyButton)
        button_group.addButton(dialog.mediumButton)
        button_group.addButton(dialog.hardButton)

        def difficultybuttons(d):
            nonlocal diff
            diff = d
            scene.clear()
            for i in range(4):
                difficulty, equation_text, answer = mgen.generate_linear_equation(diff)
                equation_item = ExampleTextItem(equation_text, difficulty, answer)
                equation_item.setPlainText(equation_text)
                equation_item.setPos(0, 20 + i * 100)
                scene.addItem(equation_item)

        dialog.easyButton.clicked.connect(lambda: difficultybuttons("Easy"))
        dialog.mediumButton.clicked.connect(lambda: difficultybuttons("Medium"))
        dialog.hardButton.clicked.connect(lambda: difficultybuttons("Hard"))
        dialog.easyButton.setChecked(True)
        button_group.setExclusive(True)

        def process_equation_and_close():
            add_equation()
            dialog.close()

        def add_equation():
            num_of_equations = int(dialog.numofqueLine.text())
            for _ in range(num_of_equations):
                difficulty, equation_text, answer = mgen.generate_linear_equation(diff)
                equation_item = EditableTextItem(equation_text, difficulty, answer)
                equation_item.setPlainText(equation_text)
                if self.selectedPage is not None:
                    self.selectedPage.scene().addItem(equation_item)
                    x = random.uniform(0,
                                       self.selectedPage.scene().width() - equation_item.boundingRect().width())
                    y = random.uniform(0,
                                       self.selectedPage.scene().height() - equation_item.boundingRect().height())
                    equation_item.setPos(x, y)
            dialog.easyButton.setChecked(True)

        dialog.okButton.clicked.connect(process_equation_and_close)
        dialog.addButton.clicked.connect(add_equation)
        dialog.exec()
    except Exception as e:
        print(f"An error occurred: {e}")

def factorise_equation_popup(self):
    try:
        diff = "Easy"
        dialog = loadUi('questiondialog.ui')
        dialog.setFixedSize(dialog.size())
        dialog.setFixedSize(dialog.size())
        scene = QGraphicsScene()
        dialog.questionView.setScene(scene)
        for i in range(4):
            difficulty, equation_text, answer = mgen.generate_factorise_equation(diff)
            equation_item = ExampleTextItem(equation_text, difficulty, answer)
            equation_item.setPlainText(equation_text)
            equation_item.setPos(0, 20 + i * 100)  # Changed from 10 to 50
            scene.addItem(equation_item)
        validator = QIntValidator(0, 99)
        dialog.numofqueLine.setValidator(validator)
        dialog.okButton.setEnabled(False)
        dialog.addButton.setEnabled(False)

        def enable_buttons():
            if dialog.numofqueLine.text():
                dialog.okButton.setEnabled(True)
                dialog.addButton.setEnabled(True)
            else:
                dialog.okButton.setEnabled(False)
                dialog.addButton.setEnabled(False)

        dialog.numofqueLine.textChanged.connect(enable_buttons)
        button_group = QButtonGroup()
        button_group.addButton(dialog.easyButton)
        button_group.addButton(dialog.mediumButton)
        button_group.addButton(dialog.hardButton)

        def difficultybuttons(d):
            nonlocal diff
            diff = d
            scene.clear()
            for i in range(4):
                difficulty, equation_text, answer = mgen.generate_factorise_equation(diff)
                equation_item = ExampleTextItem(equation_text, difficulty, answer)
                equation_item.setPlainText(equation_text)
                equation_item.setPos(0, 20 + i * 100)
                scene.addItem(equation_item)

        dialog.easyButton.clicked.connect(lambda: difficultybuttons("Easy"))
        dialog.mediumButton.clicked.connect(lambda: difficultybuttons("Medium"))
        dialog.hardButton.clicked.connect(lambda: difficultybuttons("Hard"))
        dialog.easyButton.setChecked(True)
        button_group.setExclusive(True)

        def process_equation_and_close():
            add_equation()
            dialog.close()

        def add_equation():
            num_of_equations = int(dialog.numofqueLine.text())
            for _ in range(num_of_equations):
                difficulty, equation_text, answer = mgen.generate_factorise_equation(diff)
                equation_item = EditableTextItem(equation_text, difficulty, answer)
                equation_item.setPlainText(equation_text)
                if self.selectedPage is not None:
                    self.selectedPage.scene().addItem(equation_item)
                    x = random.uniform(0,
                                       self.selectedPage.scene().width() - equation_item.boundingRect().width())
                    y = random.uniform(0,
                                       self.selectedPage.scene().height() - equation_item.boundingRect().height())
                    equation_item.setPos(x, y)
            dialog.easyButton.setChecked(True)

        dialog.okButton.clicked.connect(process_equation_and_close)
        dialog.addButton.clicked.connect(add_equation)
        dialog.exec()
    except Exception as e:
        print(f"An error occurred: {e}")

def quadratic(self):
    try:
        diff = "Easy"
        dialog = loadUi('questiondialog.ui')
        dialog.setFixedSize(dialog.size())
        dialog.setFixedSize(dialog.size())
        scene = QGraphicsScene()
        dialog.questionView.setScene(scene)
        for i in range(4):
            difficulty, equation_text, answer = mgen.construct_quadratic(diff)
            equation_item = ExampleTextItem(equation_text, difficulty, answer)
            equation_item.setPlainText(equation_text)
            equation_item.setPos(0, 20 + i * 100)  # Changed from 10 to 50
            scene.addItem(equation_item)
        validator = QIntValidator(0, 99)
        dialog.numofqueLine.setValidator(validator)
        dialog.okButton.setEnabled(False)
        dialog.addButton.setEnabled(False)

        def enable_buttons():
            if dialog.numofqueLine.text():
                dialog.okButton.setEnabled(True)
                dialog.addButton.setEnabled(True)
            else:
                dialog.okButton.setEnabled(False)
                dialog.addButton.setEnabled(False)

        dialog.numofqueLine.textChanged.connect(enable_buttons)
        button_group = QButtonGroup()
        button_group.addButton(dialog.easyButton)
        button_group.addButton(dialog.mediumButton)
        button_group.addButton(dialog.hardButton)

        def difficultybuttons(d):
            nonlocal diff
            diff = d
            scene.clear()
            for i in range(4):
                difficulty, equation_text, answer = mgen.construct_quadratic(diff)
                equation_item = ExampleTextItem(equation_text, difficulty, answer)
                equation_item.setPlainText(equation_text)
                equation_item.setPos(0, 20 + i * 100)
                scene.addItem(equation_item)

        dialog.easyButton.clicked.connect(lambda: difficultybuttons("Easy"))
        dialog.mediumButton.clicked.connect(lambda: difficultybuttons("Medium"))
        dialog.hardButton.clicked.connect(lambda: difficultybuttons("Hard"))
        dialog.easyButton.setChecked(True)
        button_group.setExclusive(True)

        def process_equation_and_close():
            add_equation()
            dialog.close()

        def add_equation():
            num_of_equations = int(dialog.numofqueLine.text())
            for _ in range(num_of_equations):
                difficulty, equation_text, answer = mgen.construct_quadratic(diff)
                equation_item = EditableTextItem(equation_text, difficulty, answer)
                equation_item.setPlainText(equation_text)
                if self.selectedPage is not None:
                    self.selectedPage.scene().addItem(equation_item)
                    x = random.uniform(0,
                                       self.selectedPage.scene().width() - equation_item.boundingRect().width())
                    y = random.uniform(0,
                                       self.selectedPage.scene().height() - equation_item.boundingRect().height())
                    equation_item.setPos(x, y)
            dialog.easyButton.setChecked(True)

        dialog.okButton.clicked.connect(process_equation_and_close)
        dialog.addButton.clicked.connect(add_equation)
        dialog.exec()
    except Exception as e:
        print(f"An error occurred: {e}")