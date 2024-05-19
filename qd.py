from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap, QIntValidator, QImage
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
        self.answer = answer

    def mouseDoubleClickEvent(self, event):
        try:
            dialog = QDialog()
            dialog.setWindowTitle(self.equation_type)
            layout = QVBoxLayout()

            question_label = QLabel(f"Question: {self.text}")
            layout.addWidget(question_label)

            if isinstance(self.answer, QPixmap):
                answer_label = QLabel()
                answer_label.setPixmap(self.answer)
                layout.addWidget(answer_label)
            else:
                answer_label = QLabel(f"Answer: {self.answer}")
                layout.addWidget(answer_label)

            difficulty_label = QLabel(f"Difficulty: {self.difficulty}")
            layout.addWidget(difficulty_label)

            ok_btn = QPushButton('OK')
            ok_btn.clicked.connect(dialog.accept)
            layout.addWidget(ok_btn)

            dialog.setLayout(layout)
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

            # Snap to 10px grid
            grid_size = 10
            new_x = round(new_pos.x() / grid_size) * grid_size
            new_y = round(new_pos.y() / grid_size) * grid_size
            snapped_pos = QPointF(new_x, new_y)

            self.setPos(snapped_pos)
        else:
            super().mouseMoveEvent(event)

    def setPlainText(self, text):
        self.text = text
        fig = plt.figure(figsize=(6, 5), facecolor='none')  # Set transparent background

        text_obj = plt.text(0, 0, f'${text}$', size=20, ha='center', va='center', color='black')  # Set text color
        plt.axis('off')

        renderer = fig.canvas.get_renderer()
        bbox = text_obj.get_window_extent(renderer)

        fig.set_size_inches(bbox.width / renderer.dpi * 0.5, bbox.height / renderer.dpi * 0.5)

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)  # Set transparency
        plt.close(fig)
        buf.seek(0)

        # Load as QImage for transparency
        image = QImage()
        image.loadFromData(buf.read())

        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap)


class ExampleTextItem(QGraphicsPixmapItem):
    def __init__(self, equation_type, difficulty, answer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equation_type = equation_type  # Store the equation type
        self.difficulty = difficulty  # Store the difficulty level
        self.answer = answer  # Add 'answer' attribute here

    def setPlainText(self, text):
        self.text = text
        fig = plt.figure(figsize=(6, 5), facecolor='none')  # Set transparent background

        text_obj = plt.text(-10, 0.5, f'${text}$', size=15, ha='left', va='center', color='black')
        if self.answer != "None":
            plt.text(-10, -2, f'Answer: {self.answer}', size=10, ha='left', va='center', color='red')

        plt.axis('off')

        renderer = fig.canvas.get_renderer()
        bbox = text_obj.get_window_extent(renderer)

        fig.set_size_inches(bbox.width / renderer.dpi * 0.5, bbox.height / renderer.dpi * 0.5)

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)  # Set transparency
        plt.close(fig)
        buf.seek(0)

        # Load as QImage for transparency
        image = QImage()
        image.loadFromData(buf.read())

        pixmap = QPixmap.fromImage(image)
        self.setPixmap(pixmap)


def create_question_dialog(self, equation_type, generate_equation_func):
    try:
        diff = "Easy"  # Initial difficulty, but will be updated
        dialog = loadUi('questiondialog.ui')
        dialog.setFixedSize(dialog.size())
        dialog.setWindowTitle(equation_type)
        dialog.cancelButton.clicked.connect(dialog.close)
        scene = QGraphicsScene()
        dialog.questionView.setScene(scene)

        def update_example_equations():
            nonlocal diff  # Access and modify the 'diff' variable
            scene.clear()
            y_pos = 20  # Initialize y position

            for i in range(4):
                difficulty, equation_text, answer = generate_equation_func(diff)

                # Check equation type for image answers
                if equation_type == "Graphing Quadratics":
                    # Display the question text (for all question types)
                    equation_item = ExampleTextItem(equation_type, difficulty, "None")
                    equation_item.setPlainText(equation_text) # Don't pass the answer here
                    equation_item.setPos(0, y_pos)
                    scene.addItem(equation_item)

                    # Update y_pos for the next question
                    y_pos += equation_item.boundingRect().height() + 20
                    # If it's a "Graphing Quadratics" question, display the graph
                    pixmap_item = QGraphicsPixmapItem(answer)

                    # Scale the image
                    max_width = 200  # Set the maximum width you want
                    pixmap_item.setScale(max_width / pixmap_item.pixmap().width())

                    scene.addItem(pixmap_item)
                    pixmap_item.setPos(0, y_pos)  # Position below question

                    # Update y_pos for the next question, considering scaled image height
                    y_pos += pixmap_item.boundingRect().height() + 20
                else:
                    # If it's not a "Graphing Quadratics" question, display the text answer
                    equation_item = ExampleTextItem(equation_type, difficulty, answer)
                    equation_item.setPlainText(equation_text)
                    equation_item.setPos(0, y_pos)
                    scene.addItem(equation_item)

                    # Update y_pos for the next question
                    y_pos += equation_item.boundingRect().height() + 20

        def set_difficulty(new_diff):
            nonlocal diff
            diff = new_diff
            update_example_equations()

        dialog.easyButton.clicked.connect(lambda: set_difficulty("Easy"))
        dialog.mediumButton.clicked.connect(lambda: set_difficulty("Medium"))
        dialog.hardButton.clicked.connect(lambda: set_difficulty("Hard"))
        dialog.easyButton.setChecked(True)

        update_example_equations()

        # Number of Questions Input
        validator = QIntValidator(0, 99)
        dialog.numofqueLine.setValidator(validator)

        def enable_buttons():
            if dialog.numofqueLine.text():
                dialog.okButton.setEnabled(True)
                dialog.addButton.setEnabled(True)
            else:
                dialog.okButton.setEnabled(False)
                dialog.addButton.setEnabled(False)

        dialog.numofqueLine.textChanged.connect(enable_buttons)

        def add_equations():
            num_of_equations = int(dialog.numofqueLine.text())

            # Keep track of the y-position for stacking
            y_pos = 0

            for _ in range(num_of_equations):
                difficulty, equation_text, answer = generate_equation_func(diff)
                equation_item = EditableTextItem(equation_text, difficulty, answer)
                equation_item.setPlainText(equation_text)
                if self.selectedPage is not None:
                    self.selectedPage.scene().addItem(equation_item)

                    # Position below the previous item
                    x = 0  # Align to the left
                    y = y_pos
                    equation_item.setPos(x, y)

                    # Update y_pos for the next item
                    y_pos += equation_item.boundingRect().height() + 10  # Add some spacing

        dialog.okButton.clicked.connect(lambda: add_equations() and dialog.close())
        dialog.addButton.clicked.connect(add_equations)
        dialog.exec()
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
def linear_equation_popup(self):
    create_question_dialog(self, "Linear Equation", mgen.generate_linear_equation)


def factorise_equation_popup(self):
    create_question_dialog(self, "Factorise Equation", mgen.generate_factorise_equation)


def quadratic(self):
    create_question_dialog(self, "Quadratic Equation", mgen.construct_quadratic)


def graph_quadratic(self):
    create_question_dialog(self, "Graphing Quadratics", mgen.generate_graphing_quadratic)