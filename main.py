from PyQt6.QtWidgets import *
from PyQt6 import uic
from PyQt6.uic.properties import QtCore
from PyQt6 import QtCore, QtGui, QtWidgets, uic


class MyGui(QMainWindow):
    def __init__(self):
        super(MyGui, self).__init__()
        uic.loadUi('main.ui', self)

        # Initialize the page counts
        self.questionPageCount = 0
        self.answerPageCount = 0

        self.addPage.clicked.connect(lambda: self.add_question_page(self.scrollAreaWidgetContents))
        self.deletePage.clicked.connect(self.delete_page)

        self.scrollArea.setStyleSheet("background-color: grey;")
        self.scrollAreaAnswers.setStyleSheet("background-color: grey;")

        self.showMaximized()  # Maximize the window
        self.show()
        self.actionClose.triggered.connect(exit)

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

        self.intro_page(self.scrollAreaWidgetContents)
        self.add_question_page(self.scrollAreaWidgetContents)
        self.add_answer_page(self.scrollAreaAnswers)

    def intro_page(self, scrollArea):
        # Create a new page
        newPage = QWidget()
        newPage.setObjectName("Intro Page")  # Set the object name to the page name
        newPage.setFixedSize(794, 1123)  # Set the size to A4 dimensions (in pixels at 96 DPI)
        newPage.setStyleSheet("background-color: white;")  # Set the background color to white

        # Create a label at the bottom of the page to indicate the page number
        pageNumberLabel = QLabel(newPage)
        pageNumberLabel.setText("Intro Page")
        pageNumberLabel.move(0, newPage.height() - pageNumberLabel.height())

        # Create a layout for the scrollArea if it doesn't have one
        if scrollArea.layout() is None:
            scrollArea.setLayout(QVBoxLayout())

        # Add the new page to the layout
        scrollArea.layout().addWidget(newPage)
        print(self.answerPageCount)

    def add_question_page(self, scrollArea):
        # Create a new page
        newPage = QWidget()
        newPage.setObjectName("Question Page")  # Set the object name to the page name
        newPage.setFixedSize(794, 1123)  # Set the size to A4 dimensions (in pixels at 96 DPI)
        newPage.setStyleSheet("background-color: white;")  # Set the background color to white

        # Create a label at the bottom of the page to indicate the page number
        pageNumberLabel = QLabel(newPage)
        pageNumberLabel.setText("Question Page")
        pageNumberLabel.move(0, newPage.height() - pageNumberLabel.height())

        # Create a layout for the scrollArea if it doesn't have one
        if scrollArea.layout() is None:
            scrollArea.setLayout(QVBoxLayout())

        # Add the new page to the layout
        scrollArea.layout().addWidget(newPage)
        self.questionPageCount += 1
        print("Questions", self.questionPageCount)

    def add_answer_page(self, scrollArea):
        # Create a new page
        newPage = QWidget()
        newPage.setObjectName("Answer Page")  # Set the object name to the page name
        newPage.setFixedSize(794, 1123)  # Set the size to A4 dimensions (in pixels at 96 DPI)
        newPage.setStyleSheet("background-color: white;")  # Set the background color to white

        # Create a label at the bottom of the page to indicate the page number
        pageNumberLabel = QLabel(newPage)
        pageNumberLabel.setText("Answer Page")
        pageNumberLabel.move(0, newPage.height() - pageNumberLabel.height())

        # Create a layout for the scrollArea if it doesn't have one
        if scrollArea.layout() is None:
            scrollArea.setLayout(QVBoxLayout())

        # Add the new page to the layout
        scrollArea.layout().addWidget(newPage)
        self.answerPageCount += 1
        print(self.answerPageCount)



    def delete_page(self):
        try:
            if self.questionPageCount > 1:
                widgetToRemove = self.scrollAreaWidgetContents.layout().itemAt(
                    self.scrollAreaWidgetContents.layout().count() - 1).widget()
                self.scrollAreaWidgetContents.layout().removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                self.questionPageCount -= 1

            if self.answerPageCount > 1:
                widgetToRemove = self.scrollAreaAnswers.layout().itemAt(
                    self.scrollAreaAnswers.layout().count() - 1).widget()
                self.scrollAreaAnswers.layout().removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                self.answerPageCount -= 1
            print(self.answerPageCount)
        except Exception as e:
            print(e)



    def add_equation(self, item):
        equation_type = item.text()
        if equation_type == "  3A Expanding and collecting like terms":
            print("Not Done")
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
