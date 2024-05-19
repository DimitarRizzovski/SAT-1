from PyQt6.QtWidgets import *
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPainter, QPageSize
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
            view.setStyleSheet("border: 2px solid black")
        self.isSelected = True
        self.setStyleSheet("border: 2px solid blue")
        self.parent().selectedPage = self
        super().mouseDoubleClickEvent(event)


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

    def create_page(self, scene, scroll_area_widget_contents, page_count, page_type):

        view = SelectableGraphicsView(scene, page_count, self)
        view.setFixedSize(794, 1150)
        scene.setSceneRect(0, 0, 794, 1123)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        if scroll_area_widget_contents.layout() is None:
            scroll_area_widget_contents.setLayout(QVBoxLayout())
            scroll_area_widget_contents.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_area_widget_contents.layout().addWidget(view)

        # Add page number label
        if page_type != "Title":
            page_number_label = QGraphicsTextItem(f"Page {page_count}")
            scene.addItem(page_number_label)
            x = (scene.width() - page_number_label.boundingRect().width()) / 2
            y = scene.height() - page_number_label.boundingRect().height()
            page_number_label.setPos(x, y)

        view.setObjectName(f"{page_type} Page {page_count}")
        if page_type == "Question":
            view.setStyleSheet("border: 2px solid black")  # Add border for question pages

        return view

    def title_page(self, scrollAreaTitlePageWidgetContents):
        scene_intro = QGraphicsScene()
        self.create_page(scene_intro, scrollAreaTitlePageWidgetContents, 0, "Title")

    def add_question_page(self):
        self.questionPageCount += 1
        scene = QGraphicsScene()
        self.create_page(scene, self.scrollAreaWidgetContents, self.questionPageCount, "Question")

    def add_answer_page(self):
        scene_intro = QGraphicsScene()
        self.answerPageCount += 1
        self.scene_answers = QGraphicsScene()
        self.create_page(scene_intro, self.scrollAreaAnswersWidgetContents, 2, "Answer")

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
                view.setStyleSheet("border: 2px solid black")
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
            printer = QPrinter(QPrinter.PrinterMode.PrinterResolution)
            printer.setResolution(96)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            printer.setOutputFileName("output.pdf")

            painter = QPainter()
            painter.begin(printer)

            # Render the title page
            self.scrollAreaTitlePageWidgetContents.layout().itemAt(0).widget().scene().render(painter)

            # Render question pages
            for i in range(self.questionPageCount):
                questionPage = self.scrollAreaWidgetContents.layout().itemAt(i).widget()
                printer.newPage()  # Start a new page before rendering each question page
                questionPage.scene().render(painter)

            # Render answer pages
            for i in range(self.answerPageCount):
                answerPage = self.scrollAreaAnswersWidgetContents.layout().itemAt(i).widget()
                printer.newPage()  # Start a new page before rendering each answer page
                answerPage.scene().render(painter)

            painter.end()

        except Exception as e:
            print(f"An error occurred while saving the PDF: {e}")

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
            qd.graph_quadratic(self)
        elif equation_type == "  3E Graphing Quadratics":
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
