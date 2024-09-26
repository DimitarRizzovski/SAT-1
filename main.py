import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QScrollArea, QSizePolicy, QVBoxLayout, QTabWidget,
    QDialog, QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsTextItem, QMessageBox,
    QLineEdit, QListWidget, QPushButton, QLabel, QWidget
)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPainter, QPageSize, QAction
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import Qt
import qd
import sae


class SelectableGraphicsView(QGraphicsView):
    """
    A QGraphicsView subclass that detects user input to select a page.
    """

    def __init__(self, scene, page_number, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.isSelected = False
        self.page_number = page_number

    def mouseDoubleClickEvent(self, event):
        """
        Handles double-click events to select the page.
        """
        for view in self.parent().findChildren(SelectableGraphicsView):
            view.isSelected = False
            view.setStyleSheet("border: 2px solid black")
        self.isSelected = True
        self.setStyleSheet("border: 2px solid blue")
        self.parent().selectedPage = self
        super().mouseDoubleClickEvent(event)


class MyGui(QMainWindow):
    """
    The main GUI class
    """

    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)

        # Initialise variables
        self.current_save_file = None
        self.saves_dir = "saves"
        self.questionPageCount = 0
        self.answerPageCount = 0
        self.selectedPage = None

        # Ensure the saves directory exists
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)

        # Set up UI elements and connections
        self.setup_ui_elements()
        self.setup_connections()

        # Initialise pages
        self.create_title_page()
        self.add_question_page()
        self.add_answer_page()

        # Select the first question page by default
        first_question_page = self.scrollAreaQuestionWidgetContents.layout().itemAt(0).widget()
        first_question_page.isSelected = True
        first_question_page.setStyleSheet("border: 2px solid blue")

        # Show the main window maximized
        self.showMaximized()
        self.show()

    def setup_ui_elements(self):
        """
        Finds and initialises UI elements.
        """
        self.scrollAreaTitlePageWidgetContents = self.findChild(QWidget, 'scrollAreaTitlePageWidgetContents')
        self.scrollAreaQuestionWidgetContents = self.findChild(QWidget, 'scrollAreaQuestionWidgetContents')
        self.scrollAreaAnswersWidgetContents = self.findChild(QWidget, 'scrollAreaAnswersWidgetContents')
        self.tabWidget = self.findChild(QTabWidget, 'tabWidget')

        self.addPage = self.findChild(QPushButton, 'addPage')
        self.deletePage = self.findChild(QPushButton, 'deletePage')
        self.searchMathEquations = self.findChild(QLineEdit, 'searchMathEquations')
        self.mathQuestions = self.findChild(QListWidget, 'mathQuestions')

        self.actionPDF = self.findChild(QAction, 'actionPDF')
        self.actionSave = self.findChild(QAction, 'actionSave')
        self.actionSave_As = self.findChild(QAction, 'actionSave_As')
        self.actionOpen = self.findChild(QAction, 'actionOpen_2')
        self.actionExit = self.findChild(QAction, 'actionExit')

    def setup_connections(self):
        """
        Connects UI elements to their respective event handlers.
        """
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.actionPDF.triggered.connect(self.save_pdf)
        self.addPage.clicked.connect(self.add_question_page)
        self.deletePage.clicked.connect(self.delete_page)
        self.searchMathEquations.textChanged.connect(self.search_equations)
        self.mathQuestions.itemDoubleClicked.connect(self.add_equation)
        self.actionSave.triggered.connect(self.save_project)
        self.actionSave_As.triggered.connect(self.save_project_as)
        self.actionOpen.triggered.connect(self.open_project)
        self.actionExit.triggered.connect(self.exit_application)

    # Page Management Methods

    def create_page(self, scene, scroll_area_widget_contents, page_count, page_type):
        """
        Creates a new page and adds it to the specified scroll area.

        Args:
            scene (QGraphicsScene): The scene to be displayed in the page.
            scroll_area_widget_contents (QWidget): The container widget for the pages.
            page_count (int): The current count of pages.
            page_type (str): The type of page ("Title", "Question", "Answer").
        """
        view = SelectableGraphicsView(scene, page_count, self)
        view.setFixedSize(794, 1150)
        scene.setSceneRect(0, 0, 794, 1123)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        if scroll_area_widget_contents.layout() is None:
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_area_widget_contents.setLayout(layout)
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

    def create_title_page(self):
        """
        Creates the title page.
        """
        scene_intro = QGraphicsScene()
        self.create_page(scene_intro, self.scrollAreaTitlePageWidgetContents, 0, "Title")

    def add_question_page(self):
        """
        Adds a new question page.
        """
        self.questionPageCount += 1
        scene = QGraphicsScene()
        self.create_page(scene, self.scrollAreaQuestionWidgetContents, self.questionPageCount, "Question")

    def add_answer_page(self):
        """
        Adds a new answer page.
        """
        self.answerPageCount += 1
        scene = QGraphicsScene()
        self.create_page(scene, self.scrollAreaAnswersWidgetContents, self.answerPageCount, "Answer")

    def delete_page(self):
        """
        Deletes the currently selected page.
        """
        try:
            if self.selectedPage is None:
                return

            layout = self.selectedPage.parent().layout()
            if layout is not None:
                index = layout.indexOf(self.selectedPage)
                if index != -1:
                    widget_to_remove = layout.itemAt(index).widget()
                    layout.removeWidget(widget_to_remove)
                    widget_to_remove.setParent(None)

                    # Update page counts
                    if self.selectedPage in self.scrollAreaQuestionWidgetContents.findChildren(SelectableGraphicsView):
                        self.questionPageCount -= 1
                    elif self.selectedPage in self.scrollAreaAnswersWidgetContents.findChildren(SelectableGraphicsView):
                        self.answerPageCount -= 1

                    self.selectedPage = None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the page: {e}")

    # Event Handlers

    def on_tab_changed(self, index):
        """
        Handles tab change events.

        Args:
            index (int): The index of the selected tab.
        """
        try:
            for view in self.findChildren(SelectableGraphicsView):
                view.isSelected = False
                view.setStyleSheet("border: 2px solid black")
            self.selectedPage = None

            if index == 0:
                selected_page_layout = self.scrollAreaTitlePageWidgetContents.layout()
            elif index == 1:
                selected_page_layout = self.scrollAreaQuestionWidgetContents.layout()
            elif index == 2:
                selected_page_layout = self.scrollAreaAnswersWidgetContents.layout()
            else:
                return

            if selected_page_layout is not None and selected_page_layout.count() > 0:
                selected_page = selected_page_layout.itemAt(0).widget()
                selected_page.isSelected = True
                selected_page.setStyleSheet("border: 2px solid blue")
                self.selectedPage = selected_page
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while changing tabs: {e}")

    def search_equations(self):
        """
        Filters the list of math equations based on the search input.
        """
        search_text = self.searchMathEquations.text().lower()
        for i in range(self.mathQuestions.count()):
            item = self.mathQuestions.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def add_equation(self, item):
        """
        Adds the selected equation to the currently selected page.

        Args:
            item (QListWidgetItem): The selected equation item.
        """
        # Find the currently selected page
        for view in self.findChildren(SelectableGraphicsView):
            if view.isSelected:
                self.selectedPage = view
                break

        equation_type = item.text().strip()
        equation_functions = {
            "3A Expanding and collecting like terms": qd.linear_equation_popup,
            "3B Factorising": qd.factorise_equation_popup,
            "3C Quadratic Equations": qd.quadratic,
            "3D Graphing Quadratics": qd.graph_quadratic,
            "3E Graphing Quadratics": lambda self: QMessageBox.information(self, "Not Done", "Not Done"),
            "3F Completing The Square And Turning Points": lambda self: QMessageBox.information(self, "Not Done",
                                                                                                "Not Done"),
            "3G Solving Quadratic Inequalities": lambda self: QMessageBox.information(self, "Not Done", "Not Done"),
            "3H The General Quadratic Formula": lambda self: QMessageBox.information(self, "Not Done", "Not Done"),
            "3I The Discriminant": lambda self: QMessageBox.information(self, "Not Done", "Not Done"),
            "3J Solving Simultaneous Linear and Quadratic Equations": lambda self: QMessageBox.information(self,
                                                                                                           "Not Done",
                                                                                                           "Not Done"),
            "3K Families of Quadratic Polynomial Functions": lambda self: QMessageBox.information(self, "Not Done",
                                                                                                  "Not Done"),
            "3L Quadratic Models": lambda self: QMessageBox.information(self, "Not Done", "Not Done"),
        }

        func = equation_functions.get(equation_type)
        if func:
            func(self)
        else:
            QMessageBox.warning(self, "Not Implemented", f"The equation type '{equation_type}' is not implemented yet.")

    # File Operations

    def save_pdf(self):
        """
        Saves the current project as a PDF file.
        """
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf);;All Files (*)")
            if not file_name:
                return

            printer = QPrinter(QPrinter.PrinterMode.PrinterResolution)
            printer.setResolution(96)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            printer.setOutputFileName(file_name)

            painter = QPainter()
            if not painter.begin(printer):
                QMessageBox.warning(self, "Error", "Failed to open file for writing.")
                return

            # Render the title page
            title_layout = self.scrollAreaTitlePageWidgetContents.layout()
            if title_layout and title_layout.count() > 0:
                title_page = title_layout.itemAt(0).widget()
                title_page.scene().render(painter)

            # Render question pages
            for i in range(self.questionPageCount):
                if i > 0 or (title_layout and self.questionPageCount > 0):
                    printer.newPage()
                question_page = self.scrollAreaQuestionWidgetContents.layout().itemAt(i).widget()
                question_page.scene().render(painter)

            # Render answer pages
            for i in range(self.answerPageCount):
                printer.newPage()
                answer_page = self.scrollAreaAnswersWidgetContents.layout().itemAt(i).widget()
                answer_page.scene().render(painter)

            painter.end()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the PDF: {e}")

    def save_project(self):
        """
        Saves the current project to a file.
        """
        try:
            if self.current_save_file:
                sae.save_project_data(self, self.current_save_file)
            else:
                self.save_project_as()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the project: {e}")

    def save_project_as(self):
        """
        Opens a dialog to save the project to a new file.
        """
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Project As", "",
                                                       "Math Worksheet Projects (*.mwp);;All Files (*)")
            if file_name:
                self.current_save_file = file_name
                sae.save_project_data(self, file_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the project: {e}")

    def open_project(self):
        """
        Opens an existing project file.
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Project", "",
                                                       "Math Worksheet Projects (*.mwp);;All Files (*)")
            if file_name:
                sae.load_project_data(self, file_name)
                self.current_save_file = file_name
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while opening the project: {e}")

    def exit_application(self):
        """
        This is not fully implemented yet
        """
        sae.exit_application(self)


# Main Function
def main():
    """
    The main function to run the application.
    """
    app = QApplication([])
    window = MyGui()
    app.exec()


if __name__ == '__main__':
    main()
