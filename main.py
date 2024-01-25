from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPainter, QPixmap, QIntValidator, QPageSize
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import Qt, QPointF
import mgen
import random
from matplotlib import pyplot as plt
from io import BytesIO

class EditableTextItem(QGraphicsPixmapItem):
    def __init__(self, equation_type, difficulty, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.text = ""
        self.equation_type = equation_type  # Store the equation type
        self.difficulty = difficulty  # Store the difficulty level
        self.drag_offset = QPointF(0, 0)  # Store the offset of the mouse click
        self.answer = ""  # Add 'answer' attribute here

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

class SelectableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    def mouseDoubleClickEvent(self, event):
        # Deselect all other views
        for view in self.parent().findChildren(SelectableGraphicsView):
            if view != self:
                view.setStyleSheet("")

        # Draw a blue rectangle around the view
        self.setStyleSheet("border: 2px solid blue")

        # Update the selectedPage in the parent (MyGui)
        self.parent().selectedPage = self  # Update this line

        # Call the superclass implementation
        super().mouseDoubleClickEvent(event)

class DraggableTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def mousePressEvent(self, event):
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

class MyGui(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)

        self.scrollArea = self.findChild(QScrollArea, 'scrollArea')
        self.scrollAreaAnswers = self.findChild(QScrollArea, 'scrollAreaAnswers')

        # Initialize the dictionary to store the last selected page for each tab
        self.lastSelectedPage = {}

        # Connect the currentChanged signal to a slot
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        self.actionPDF.triggered.connect(self.save_pdf)

        self.introPageWidget = QWidget()
        # Initialize the page counts
        self.questionPageCount = 0
        self.answerPageCount = 0

        self.addPage.clicked.connect(lambda: self.add_question_page(self.scrollAreaWidgetContents))
        self.deletePage.clicked.connect(self.delete_page)

        self.showMaximized()  # Maximize the window
        self.show()
        self.actionClose.triggered.connect(exit)

        self.intro_page(self.scrollAreaTitlePageWidgetContents)
        self.add_question_page(self.scrollAreaWidgetContents)
        self.add_answer_page(self.scrollAreaAnswersWidgetContents)

        # Select the first page
        selectedPage = self.scrollAreaWidgetContents.layout().itemAt(0).widget()
        selectedPage.setStyleSheet("border: 2px solid blue")

        self.searchMathEquations.textChanged.connect(self.search_equations)

        self.mathQuestions.itemDoubleClicked.connect(self.add_equation)
        self.equations = [r"Chapter 3: Quadratics",
                          "  3A Expanding and collecting like terms",
                          "  3B Factorising",
                          "  3C Quadratic Equations",
                          "  3D Graphing Quadratics",
                          "  3F Completing The Square And Turning Points",
                          "  3G Solving Quadratic Inequalities",
                          "  3H The General Quadratic Formula",
                          "  3I The Discriminant",
                          "  3J Solving Simultaneous Linear and Quadratic Equations",
                          "  3K Families of Quadratic Polynomial Functions",
                          "  3L Quadratic Models"]
        for equation in self.equations:
            QListWidgetItem(equation, self.mathQuestions)

    def search_equations(self):
        # Get the text from the QLineEdit
        search_text = self.searchMathEquations.text().lower()

        # Loop over each item in the QListWidget
        for i in range(self.mathQuestions.count()):
            item = self.mathQuestions.item(i)

            # If the item's text contains the search text, show the item, otherwise hide it
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def intro_page(self, scrollAreaTitlePageWidgetContents):
        # Create a QGraphicsScene and a SelectableGraphicsView for this page
        self.scene_intro = QGraphicsScene()  # Make scene an attribute of MyGui
        view = SelectableGraphicsView(self.scene_intro, self)

        # Set the size to A4 dimensions (in pixels at 96 DPI)
        view.setFixedSize(794, 1150)
        self.scene_intro.setSceneRect(0, 0, 794, 1123)

        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set the QGraphicsView to expand and fill the available space
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a layout for the scrollAreaTitlePageWidgetContents if it doesn't have one
        if scrollAreaTitlePageWidgetContents.layout() is None:
            scrollAreaTitlePageWidgetContents.setLayout(QVBoxLayout())
            scrollAreaTitlePageWidgetContents.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the layout

        # Add the QGraphicsView to the layout
        scrollAreaTitlePageWidgetContents.layout().addWidget(view)
        view.setObjectName(f"Title Page")

    def add_question_page(self, scrollAreaAnswers):
        # Create a QGraphicsScene and a SelectableGraphicsView for this page
        self.scene_questions = QGraphicsScene()  # Make scene an attribute of MyGui
        view = SelectableGraphicsView(self.scene_questions, self)

        # Set the size to A4 dimensions (in pixels at 96 DPI)
        view.setFixedSize(794, 1150)
        self.scene_questions.setSceneRect(0, 0, 794, 1123)

        # Hide the scrollbars
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set the QGraphicsView to expand and fill the available space
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a layout for the scrollArea if it doesn't have one
        if scrollAreaAnswers.layout() is None:
            scrollAreaAnswers.setLayout(QVBoxLayout())
            scrollAreaAnswers.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the layout

        # Add the QGraphicsView to the layout
        scrollAreaAnswers.layout().addWidget(view)

        # Create a QGraphicsTextItem for the page number
        pageNumberLabel = DraggableTextItem(f"Page {self.questionPageCount + 2}")  # Set the page number
        self.scene_questions.addItem(pageNumberLabel)

        # Calculate the position for the pageNumberLabel to align it to the bottom center of the page
        x = (self.scene_questions.width() - pageNumberLabel.boundingRect().width()) / 2
        y = self.scene_questions.height() - pageNumberLabel.boundingRect().height()

        # Set the position of the pageNumberLabel
        pageNumberLabel.setPos(x, y)

        # Set the object name to "Page " followed by the page number
        view.setObjectName(f"Page {self.questionPageCount + 2}")

        self.questionPageCount += 1

    def add_answer_page(self, scrollAreaAnswers):
        # Create a QGraphicsScene and a SelectableGraphicsView for this page
        self.scene_answers = QGraphicsScene()  # Make scene an attribute of MyGui
        view = SelectableGraphicsView(self.scene_answers, self)

        # Set the size to A4 dimensions (in pixels at 96 DPI)
        view.setFixedSize(794, 1150)
        self.scene_answers.setSceneRect(0, 0, 794, 1123)

        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set the QGraphicsView to expand and fill the available space
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create a layout for the scrollAreaAnswers if it doesn't have one
        if scrollAreaAnswers.layout() is None:
            scrollAreaAnswers.setLayout(QVBoxLayout())
            scrollAreaAnswers.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the layout

        # Add the QGraphicsView to the layout
        scrollAreaAnswers.layout().addWidget(view)
        self.answerPageCount += 1
        view.setObjectName(f"Answer Page {self.answerPageCount}")

    def delete_page(self):
        try:
            if self.questionPageCount > 1:
                widgetToRemove = self.scrollAreaWidgetContents.layout().itemAt(
                    self.scrollAreaWidgetContents.layout().count() - 1).widget()

                # Check if the page being deleted is the currently selected page
                if widgetToRemove.styleSheet() == "border: 2px solid blue":
                    # If so, select the previous page
                    previousPage = self.scrollAreaWidgetContents.layout().itemAt(
                        self.scrollAreaWidgetContents.layout().count() - 2).widget()
                    previousPage.setStyleSheet("border: 2px solid blue")

                self.scrollAreaWidgetContents.layout().removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                self.questionPageCount -= 1

            if self.answerPageCount > 1:
                widgetToRemove = self.scrollAreaAnswers.layout().itemAt(
                    self.scrollAreaAnswers.layout().count() - 1).widget()

                # Check if the page being deleted is the currently selected page
                if widgetToRemove.styleSheet() == "border: 2px solid blue":
                    # If so, select the previous page
                    previousPage = self.scrollAreaAnswers.layout().itemAt(
                        self.scrollAreaAnswers.layout().count() - 2).widget()
                    previousPage.setStyleSheet("border: 2px solid blue")

                self.scrollAreaAnswers.layout().removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                self.answerPageCount -= 1

        except Exception as e:
            print(e)

    def deselect_all_pages(self):
        # Deselect all pages
        for view in self.findChildren(SelectableGraphicsView):
            if view.styleSheet() == "border: 2px solid blue":
                view.setStyleSheet("")
        self.selectedPage = None

    def on_tab_changed(self, index):
        try:
            # Deselect all pages
            self.deselect_all_pages()

            # Select the first page of the new tab
            if index == 0:
                selectedPage = self.scrollAreaTitlePageWidgetContents.layout().itemAt(0).widget()
            elif index == 1:
                selectedPage = self.scrollAreaWidgetContents.layout().itemAt(0).widget()
            elif index == 2:
                selectedPage = self.scrollAreaAnswersWidgetContents.layout().itemAt(0).widget()

            # Draw a blue rectangle around the view
            selectedPage.setStyleSheet("border: 2px solid blue")

            # Update the selectedPage in the parent (MyGui)
            self.selectedPage = selectedPage
        except Exception as e:
            print(e)

    def save_pdf(self):
        try:
            # Create a QPrinter object
            printer = QPrinter()
            printer.setResolution(96)  # Set the resolution to 300 DPI
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))  # Set the page size to A4
            printer.setOutputFileName("output.pdf")  # Set the output file name

            # Create a QPainter object and begin painting onto the printer
            painter = QPainter(printer)

            # Render the intro scene onto the printer
            self.scene_intro.render(painter)

            # Start a new page for each question scene
            for i in range(self.questionPageCount):
                printer.newPage()
                questionPage = self.scrollAreaWidgetContents.layout().itemAt(i).widget()
                questionPage.scene().render(painter)

            # Start a new page for each answer scene
            for i in range(self.answerPageCount):
                printer.newPage()
                answerPage = self.scrollAreaAnswersWidgetContents.layout().itemAt(i).widget()
                answerPage.scene().render(painter)

            # End painting
            painter.end()
        except Exception as e:
            print(e)

    def add_equation(self, item):
        # Check all pages and set the selected page if it has the border style
        for view in self.findChildren(SelectableGraphicsView):
            if view.styleSheet() == "border: 2px solid blue":
                self.selectedPage = view
                break

        equation_type = item.text()
        if equation_type == "  3A Expanding and collecting like terms":
            try:
                diff = "Easy"
                # Load UI file
                dialog = loadUi('questiondialog.ui')

                # Set validator for numofqueLine
                validator = QIntValidator(0, 99)  # Allow numbers from 0 to 99
                dialog.numofqueLine.setValidator(validator)

                # Create a button group
                button_group = QButtonGroup()

                # Add the buttons to the group
                button_group.addButton(dialog.easyButton)
                button_group.addButton(dialog.mediumButton)
                button_group.addButton(dialog.hardButton)

                def difficultybuttons(d):
                    nonlocal diff  # This allows us to modify the 'diff' variable in the outer scope
                    diff = d

                dialog.easyButton.clicked.connect(lambda: difficultybuttons("Easy"))
                dialog.mediumButton.clicked.connect(lambda: difficultybuttons("Medium"))
                dialog.hardButton.clicked.connect(lambda: difficultybuttons("Hard"))

                # Set easyButton as the default checked button
                dialog.easyButton.setChecked(True)

                # Ensure that one of the buttons is always checked
                button_group.setExclusive(True)

                # Define a function to process the equation and close the dialog
                def process_equation_and_close():
                    dialog.close()

                # Define a function to add the equation without closing the dialog
                def add_equation():
                    difficulty, equation_text, answer = mgen.generate_linear_equation(diff)

                    # Create a QGraphicsTextItem with the equation text
                    equation_item = EditableTextItem(equation_text, difficulty)
                    equation_item.setPlainText(equation_text)
                    equation_item.answer = answer

                    # Add the QGraphicsTextItem to the scene of the selected page
                    if self.selectedPage is not None:
                        self.selectedPage.scene().addItem(equation_item)

                        # Generate random coordinates within the bounds of the scene
                        x = random.uniform(0, self.selectedPage.scene().width() - equation_item.boundingRect().width())
                        y = random.uniform(0,
                                           self.selectedPage.scene().height() - equation_item.boundingRect().height())

                        # Set the position of the equation_item in the scene
                        equation_item.setPos(x, y)

                    # Reset easyButton to checked
                    dialog.easyButton.setChecked(True)

                # Connect the clicked signal of the okButton to the slot
                dialog.okButton.clicked.connect(process_equation_and_close)

                # Connect the clicked signal of the addButton to the slot
                dialog.addButton.clicked.connect(add_equation)

                # Show dialog and wait for user to press OK
                dialog.exec()
            except Exception as e:
                print(f"An error occurred: {e}")


        elif equation_type == "  3B Factorising":
            print("Not Done")
        elif equation_type == "  3C Quadratic Equations":
            print("Not Done")
        elif equation_type == "  3D Graphing Quadratics":
            print("Not Done")
        elif equation_type == "  3F Completing The Square And Turning Points":
            print("Not Done")
        elif equation_type == "  3G Solving Quadratic Inequalities":
            print("Not Done")
        elif equation_type == "  3H The General Quadratic Formula":
            print("Not Done")
        elif equation_type == "  3I The Discriminant":
            print("Not Done")
        elif equation_type == "  3J Solving Simultaneous Linear and Quadratic Equations":
            print("Not Done")
        elif equation_type == "  3K Families of Quadratic Polynomial Functions":
            print("Not Done")
        elif equation_type == "  3L Quadratic Models":
            print("Not Done")
        else:
            print("Not Valid")
def main():
    app = QApplication([])
    window = MyGui()
    app.exec()


if __name__ == '__main__':
    main()
