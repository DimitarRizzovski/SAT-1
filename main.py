from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPainter, QPageSize, QTransform
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import Qt
import qd

class SelectableGraphicsView(QGraphicsView):
    def __init__(self, scene, page_number, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.isSelected = False
        self.page_number = page_number

    def mouseDoubleClickEvent(self, event):
        for view in self.parent().findChildren(SelectableGraphicsView):
            view.isSelected = False
            view.setStyleSheet("")
        self.isSelected = True
        self.setStyleSheet("border: 2px solid blue")
        self.parent().selectedPage = self
        super().mouseDoubleClickEvent(event)

class DraggableTextItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
class MyGui(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)
        self.scrollArea = self.findChild(QScrollArea, 'scrollArea')
        self.scrollAreaAnswers = self.findChild(QScrollArea, 'scrollAreaAnswers')
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.actionPDF.triggered.connect(self.save_pdf)
        self.questionPageCount = 0
        self.answerPageCount = 0
        self.addPage.clicked.connect(self.add_question_page)
        self.deletePage.clicked.connect(self.delete_page)
        self.searchMathEquations.textChanged.connect(self.search_equations)
        self.mathQuestions.itemDoubleClicked.connect(self.add_equation)
        self.actionClose.triggered.connect(exit)
        self.title_page(self.scrollAreaTitlePageWidgetContents)
        self.add_question_page()
        self.add_answer_page()
        self.scrollAreaWidgetContents.layout().itemAt(0).widget().isSelected = True
        self.scrollAreaWidgetContents.layout().itemAt(0).widget().setStyleSheet("border: 2px solid blue")
        self.equations = [r"Chapter 3: Quadratics", "  3A Expanding and collecting like terms", "  3B Factorising", "  3C Quadratic Equations", "  3D Graphing Quadratics", "  3F Completing The Square And Turning Points", "  3G Solving Quadratic Inequalities", "  3H The General Quadratic Formula", "  3I The Discriminant", "  3J Solving Simultaneous Linear and Quadratic Equations", "  3K Families of Quadratic Polynomial Functions", "  3L Quadratic Models"]
        for equation in self.equations:
            QListWidgetItem(equation, self.mathQuestions)
        self.showMaximized()
        self.show()

    def search_equations(self):
        search_text = self.searchMathEquations.text().lower()
        for i in range(self.mathQuestions.count()):
            item = self.mathQuestions.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def title_page(self, scrollAreaTitlePageWidgetContents):
        self.scene_intro = QGraphicsScene()
        view = SelectableGraphicsView(self.scene_intro, 0, self)
        view.setFixedSize(794, 1150)
        self.scene_intro.setSceneRect(0, 0, 794, 1123)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if scrollAreaTitlePageWidgetContents.layout() is None:
            scrollAreaTitlePageWidgetContents.setLayout(QVBoxLayout())
            scrollAreaTitlePageWidgetContents.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        scrollAreaTitlePageWidgetContents.layout().addWidget(view)
        view.setObjectName(f"Title Page")

    def add_question_page(self):
        self.questionPageCount += 1
        scene = QGraphicsScene()
        view = SelectableGraphicsView(scene, self.questionPageCount, self)
        view.setFixedSize(794, 1150)
        scene.setSceneRect(0, 0, 794, 1123)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if self.scrollAreaWidgetContents.layout() is None:
            self.scrollAreaWidgetContents.setLayout(QVBoxLayout())
            self.scrollAreaWidgetContents.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scrollAreaWidgetContents.layout().addWidget(view)

        # Make page number non-interactive
        pageNumberLabel = QGraphicsTextItem(f"Page {self.questionPageCount}")
        pageNumberLabel.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        pageNumberLabel.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        scene.addItem(pageNumberLabel)

        # Position page number at the bottom center
        x = (scene.width() - pageNumberLabel.boundingRect().width()) / 2
        y = scene.height() - pageNumberLabel.boundingRect().height()
        pageNumberLabel.setPos(x, y)
        view.setObjectName(f"Page {self.questionPageCount}")

    def add_answer_page(self):
        self.scene_answers = QGraphicsScene()
        view = SelectableGraphicsView(self.scene_answers, 1, self)
        view.setFixedSize(794, 1150)
        self.scene_answers.setSceneRect(0, 0, 794, 1123)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if self.scrollAreaAnswersWidgetContents.layout() is None:
            self.scrollAreaAnswersWidgetContents.setLayout(QVBoxLayout())
            self.scrollAreaAnswersWidgetContents.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scrollAreaAnswersWidgetContents.layout().addWidget(view)
        self.answerPageCount += 1
        view.setObjectName(f"Answer Page {self.answerPageCount}")

        # Make page number non-interactive
        pageNumberLabel = QGraphicsTextItem(f"Answer Page {self.answerPageCount}")
        pageNumberLabel.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        pageNumberLabel.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.scene_answers.addItem(pageNumberLabel)

        # Position page number at the bottom center
        x = (self.scene_answers.width() - pageNumberLabel.boundingRect().width()) / 2
        y = self.scene_answers.height() - pageNumberLabel.boundingRect().height()
        pageNumberLabel.setPos(x, y)

    def delete_page(self):
        try:
            if self.questionPageCount > 1:
                widgetToRemove = self.scrollAreaWidgetContents.layout().itemAt(
                    self.scrollAreaWidgetContents.layout().count() - 1).widget()
                if widgetToRemove.isSelected:
                    previousPage = self.scrollAreaWidgetContents.layout().itemAt(
                        self.scrollAreaWidgetContents.layout().count() - 2).widget()
                    previousPage.isSelected = True
                    previousPage.setStyleSheet("border: 2px solid blue")
                self.scrollAreaWidgetContents.layout().removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                self.questionPageCount -= 1
            if self.answerPageCount > 1:
                widgetToRemove = self.scrollAreaAnswers.layout().itemAt(
                    self.scrollAreaAnswers.layout().count() - 1).widget()
                if widgetToRemove.isSelected:
                    previousPage = self.scrollAreaAnswers.layout().itemAt(
                        self.scrollAreaAnswers.layout().count() - 2).widget()
                    previousPage.isSelected = True
                    previousPage.setStyleSheet("border: 2px solid blue")
                self.scrollAreaAnswers.layout().removeWidget(widgetToRemove)
                widgetToRemove.setParent(None)
                self.answerPageCount -= 1
        except Exception as e:
            print(e)

    def on_tab_changed(self, index):
        try:
            for view in self.findChildren(SelectableGraphicsView):
                view.isSelected = False
                view.setStyleSheet("")
            self.selectedPage = None
            if index == 0:
                selectedPage = self.scrollAreaTitlePageWidgetContents.layout().itemAt(0).widget()
            elif index == 1:
                selectedPage = self.scrollAreaWidgetContents.layout().itemAt(0).widget()
            elif index == 2:
                selectedPage = self.scrollAreaAnswersWidgetContents.layout().itemAt(0).widget()
            selectedPage.isSelected = True
            selectedPage.setStyleSheet("border: 2px solid blue")
            self.selectedPage = selectedPage
        except Exception as e:
            print(e)

    def save_pdf(self):
        try:
            printer = QPrinter()
            printer.setResolution(96)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            printer.setOutputFileName("output.pdf")
            painter = QPainter(printer)
            self.scene_intro.render(painter)
            for i in range(self.questionPageCount):
                printer.newPage()
                questionPage = self.scrollAreaWidgetContents.layout().itemAt(i).widget()
                questionPage.scene().render(painter)
            for i in range(self.answerPageCount):
                printer.newPage()
                answerPage = self.scrollAreaAnswersWidgetContents.layout().itemAt(i).widget()
                answerPage.scene().render(painter)
            painter.end()
        except Exception as e:
            print(e)

    def add_equation(self, item):
        for view in self.findChildren(SelectableGraphicsView):
            if view.isSelected:
                self.selectedPage = view
                break
        equation_type = item.text()
        if equation_type == "  3A Expanding and collecting like terms":
            qd.linear_equation_popup(self)
        elif equation_type == "  3B Factorising":
            qd.factorise_equation_popup(self)
        elif equation_type == "  3C Quadratic Equations":
            qd.quadratic(self)
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