import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPageSize, QAction
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFileDialog, QGraphicsView, QMessageBox, QListWidgetItem, QWidget
)
from PyQt6.uic import loadUi
from backend import sae, qd
from backend.connections import setup_ui_elements, setup_connections
from pages import intro_page, question_page, answer_page
from backend.usertext import TextItem


class MyGui(QMainWindow):
    """
    Main GUI class for the programme

    This class sets up the main window, initialises UI components, manages pages
    (title, question, and answer), and handles user interactions such as adding
    equations, saving projects, and exporting to a PDF file.
    """

    def __init__(self):
        """
        Initialise the main GUI window.

        Loads the UI layout from a .ui file, sets up initial directories,
        initialises counters for question and answer pages, and configures
        the initial selection and display state.
        """
        super().__init__()
        loadUi('frontend/main.ui', self)  # Load the UI design from a .ui file
        self.current_save_file = None  # Path to the current save file
        self.saves_dir = "saves"  # Directory to store save files
        self.questionPageCount = 0  # Counter for question pages
        self.answerPageCount = 0  # Counter for answer pages
        self.selectedPage = None  # Currently selected page
        self.selectedTextItem = None  # Keep track of the selected TextItem

        # Create the saves directory if it doesn't exist
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)

        # Set up UI elements and their connections
        setup_ui_elements(self)
        setup_connections(self)

        self.setup_text_formatting_controls()

        # Create initial pages
        self.create_title_page()
        self.add_question_page()
        self.add_answer_page()

        # Select and highlight the first question page by default
        first_question_page = self.scrollAreaQuestionWidgetContents.layout().itemAt(0).widget()
        first_question_page.isSelected = True
        first_question_page.setStyleSheet("border: 2px solid blue")
        self.selectedPage = first_question_page

        # Display the window maximised
        self.showMaximized()
        self.show()

    def setup_text_formatting_controls(self):
        """Initialise the text formatting buttons and fontsizeBox to be disabled initially."""
        self.boldButton.setEnabled(False)
        self.italicButton.setEnabled(False)
        self.underlineButton.setEnabled(False)
        self.fontsizeBox.setEnabled(False)  # Disable fontsizeBox initially

    def on_text_item_selected(self, text_item):
        """Handle the event when a TextItem is selected."""
        self.selectedTextItem = text_item
        # Enable the formatting buttons
        self.boldButton.setEnabled(True)
        self.italicButton.setEnabled(True)
        self.underlineButton.setEnabled(True)
        # Connect signals for selection changes within the TextItem
        text_item.selectionChanged.connect(self.on_text_selection_changed)
        # Check if text is selected within the TextItem
        self.on_text_selection_changed()

    def on_text_item_deselected(self):
        """Handle the event when a TextItem is deselected."""
        if self.selectedTextItem:
            try:
                self.selectedTextItem.selectionChanged.disconnect(self.on_text_selection_changed)
            except Exception:
                pass
        self.selectedTextItem = None
        # Disable the formatting buttons and fontsizeBox
        self.boldButton.setEnabled(False)
        self.italicButton.setEnabled(False)
        self.underlineButton.setEnabled(False)
        self.fontsizeBox.setEnabled(False)

    def on_text_selection_changed(self):
        """Enable or disable the fontsizeBox based on text selection."""
        if self.selectedTextItem:
            cursor = self.selectedTextItem.textCursor()
            if cursor.hasSelection():
                self.fontsizeBox.setEnabled(True)
                current_font_size = cursor.charFormat().fontPointSize()
                if current_font_size == 0:  # Default font size if not set
                    current_font_size = self.selectedTextItem.font().pointSize()
                self.fontsizeBox.blockSignals(True)
                self.fontsizeBox.setValue(int(current_font_size))
                self.fontsizeBox.blockSignals(False)
            else:
                self.fontsizeBox.setEnabled(False)
        else:
            self.fontsizeBox.setEnabled(False)

    def apply_bold(self):
        """Apply bold formatting to the selected text in the selected TextItem."""
        if self.selectedTextItem:
            self.selectedTextItem.applyBold()
        else:
            QMessageBox.warning(self, "No Text Selected", "Please select a text item to apply bold formatting.")

    def apply_italic(self):
        """Apply italic formatting to the selected text in the selected TextItem."""
        if self.selectedTextItem:
            self.selectedTextItem.applyItalic()
        else:
            QMessageBox.warning(self, "No Text Selected", "Please select a text item to apply italic formatting.")

    def apply_underline(self):
        """Apply underline formatting to the selected text in the selected TextItem."""
        if self.selectedTextItem:
            self.selectedTextItem.applyUnderline()
        else:
            QMessageBox.warning(self, "No Text Selected", "Please select a text item to apply underline formatting.")

    def apply_font_size(self, size):
        """Apply the selected font size to the selected text."""
        if self.selectedTextItem:
            self.selectedTextItem.setFontSize(size)
        else:
            QMessageBox.warning(self, "No Text Selected", "Please select text to change the font size.")

    def create_page(self, page_type, page_number=None, add_default_items=True):
        """
        Create a new page of the specified type.

        Args:
            page_type (str): The type of page to create ('Title', 'Question', 'Answer').
            page_number (int, optional): Specific page number to assign. If None, increments counters.

        Returns:
            QWidget: The created page widget.

        Raises:
            ValueError: If an unknown page type is provided.
        """
        if page_type == "Title":
            if page_number is None:
                page_number = 0
            page = intro_page.IntroPage(page_number, self, add_default_items=add_default_items)
            scroll_area_widget_contents = self.scrollAreaTitlePageWidgetContents
        elif page_type == "Question":
            if page_number is None:
                self.questionPageCount += 1
                page_number = self.questionPageCount
            else:
                self.questionPageCount = max(self.questionPageCount, page_number)
            page = question_page.QuestionPage(page_number, self)
            page.equation_items = []
            scroll_area_widget_contents = self.scrollAreaQuestionWidgetContents
        elif page_type == "Answer":
            if page_number is None:
                self.answerPageCount += 1
                page_number = self.answerPageCount
            else:
                self.answerPageCount = max(self.answerPageCount, page_number)
            page = answer_page.AnswerPage(page_number, self)
            scroll_area_widget_contents = self.scrollAreaAnswersWidgetContents
        else:
            raise ValueError(f"Unknown page type: {page_type}")

        # Initialise layout if not already set
        if scroll_area_widget_contents.layout() is None:
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_area_widget_contents.setLayout(layout)

        # Add the created page to the appropriate scroll area
        scroll_area_widget_contents.layout().addWidget(page)

        # Connect TextItem signals if the page has a scene
        if hasattr(page, 'scene'):
            scene = page.scene()
            if scene:
                # Connect the scene's selectionChanged signal
                scene.selectionChanged.connect(self.on_scene_selection_changed)

        return page

    def on_scene_selection_changed(self):
        """
        Handle changes in the selection within the scene.

        Enables or disables formatting controls based on the selected item.
        """
        if self.selectedPage:
            scene = self.selectedPage.scene()
            if scene:
                selected_items = scene.selectedItems()
                if selected_items:
                    for item in selected_items:
                        if isinstance(item, TextItem):
                            self.on_text_item_selected(item)
                            return
                    # If no TextItem is selected
                    self.on_text_item_deselected()
                else:
                    self.on_text_item_deselected()

    def create_title_page(self):
        """Create the title page."""
        self.create_page("Title")

    def add_question_page(self):
        """Add a new question page."""
        self.create_page("Question")

    def add_answer_page(self):
        """Add a new answer page."""
        self.create_page("Answer")

    def create_answer_page_with_number(self, page_number):
        """
        Create an answer page with a specific page number.

        Args:
            page_number (int): The page number for the new answer page.

        Returns:
            AnswerPage: The created answer page widget.
        """
        page = self.create_page("Answer", page_number)
        return page

    def get_answer_page(self, page_number):
        """
        Retrieve an answer page by its page number.

        Args:
            page_number (int): The page number of the answer page to retrieve.

        Returns:
            AnswerPage or None: The matching answer page if found, else None.
        """
        answer_layout = self.scrollAreaAnswersWidgetContents.layout()
        if answer_layout is not None:
            for i in range(answer_layout.count()):
                page = answer_layout.itemAt(i).widget()
                if page.page_number == page_number:
                    return page
        return None

    def delete_page(self):
        """
        Delete the currently selected page.

        Prompts the user for confirmation before deletion and handles any errors.
        """
        try:
            if self.selectedPage is None:
                QMessageBox.warning(self, "No Selection", "Please select a page to delete.")
                return
            if self.questionPageCount == 1 and isinstance(self.selectedPage, question_page.QuestionPage):
                QMessageBox.warning(self, "First Page", "You cannot delete the first question page.")
                return

            # Determine which layout contains the selectedPage
            page = self.selectedPage
            parent_layout = None
            page_type = None

            # Check if the selectedPage is in Title Page layout
            title_layout = self.scrollAreaTitlePageWidgetContents.layout()
            if title_layout is not None:
                for i in range(title_layout.count()):
                    if title_layout.itemAt(i).widget() == page:
                        parent_layout = title_layout
                        page_type = "Title"
                        break

            # Check if the selectedPage is in Question Page layout
            if parent_layout is None:
                question_layout = self.scrollAreaQuestionWidgetContents.layout()
                if question_layout is not None:
                    for i in range(question_layout.count()):
                        if question_layout.itemAt(i).widget() == page:
                            parent_layout = question_layout
                            page_type = "Question"
                            break

            # Check if the selectedPage is in Answer Page layout
            if parent_layout is None:
                answer_layout = self.scrollAreaAnswersWidgetContents.layout()
                if answer_layout is not None:
                    for i in range(answer_layout.count()):
                        if answer_layout.itemAt(i).widget() == page:
                            parent_layout = answer_layout
                            page_type = "Answer"
                            break

            if parent_layout is None:
                QMessageBox.warning(self, "Error", "Could not find the selected page in any layout.")
                return

            # Confirm deletion with the user
            reply = QMessageBox.question(
                self, 'Confirm Deletion',
                f"Are you sure you want to delete the selected {page_type} page?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Remove the page from the layout
                index_to_remove = None
                for i in range(parent_layout.count()):
                    if parent_layout.itemAt(i).widget() == page:
                        index_to_remove = i
                        break
                if index_to_remove is not None:
                    item = parent_layout.takeAt(index_to_remove)
                    if item:
                        widget = item.widget()
                        if widget:
                            widget.deleteLater()
                    # Update page counts if necessary
                    if page_type == "Question":
                        self.questionPageCount -= 1
                    elif page_type == "Answer":
                        self.answerPageCount -= 1
                    elif page_type == "Title":
                        pass  # Title page count is always 1

                    # Update selectedPage
                    self.selectedPage = None

                    QMessageBox.information(self, "Deleted", "Selected page has been deleted.")
                else:
                    QMessageBox.warning(self, "Error", "Could not remove the page from the layout.")
            else:
                # User cancelled deletion
                pass

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the page: {e}")

    def delete_items(self):
        """
        Delete selected items from the currently selected page.

        Prompts the user for confirmation before deletion and handles any errors.
        """
        try:
            if self.selectedPage is None:
                QMessageBox.warning(self, "No Selection", "Please select a page to delete items from.")
                return

            scene = self.selectedPage.scene()
            if scene is None:
                QMessageBox.warning(self, "No Scene", "Selected page has no scene.")
                return

            selected_items = scene.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select one or more items to delete.")
                return

            # Confirm deletion with the user
            reply = QMessageBox.question(
                self, 'Confirm Deletion',
                f"Are you sure you want to delete the selected {len(selected_items)} item(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                for item in selected_items:
                    scene.removeItem(item)
                QMessageBox.information(self, "Deleted", "Selected items have been deleted.")
            else:
                # User cancelled deletion
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting items: {e}")

    def on_tab_changed(self, index):
        """
        Handle the event when the user changes tabs.

        Args:
            index (int): The index of the newly selected tab.
        """
        try:
            # Deselect all QGraphicsView widgets and reset the border
            for view in self.findChildren(QGraphicsView):
                if hasattr(view, 'isSelected'):
                    view.isSelected = False
                    view.setStyleSheet("border: 2px solid black")

            # Determine which layout corresponds to the selected tab
            if index == 0:
                selected_page_layout = self.scrollAreaTitlePageWidgetContents.layout()
            elif index == 1:
                selected_page_layout = self.scrollAreaQuestionWidgetContents.layout()
            elif index == 2:
                selected_page_layout = self.scrollAreaAnswersWidgetContents.layout()
            else:
                QMessageBox.warning(self, "Invalid Tab", f"Tab index {index} is not recognised.")
                return

            # Select and highlight the first page in the selected tab
            if selected_page_layout is not None and selected_page_layout.count() > 0:
                first_page = selected_page_layout.itemAt(0).widget()
                if first_page:
                    first_page.isSelected = True
                    first_page.setStyleSheet("border: 2px solid blue")
                    self.selectedPage = first_page
            else:
                QMessageBox.information(self, "No Pages", "There are no pages in this tab to select.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while changing tabs: {e}")

    def search_equations(self):
        """
        Search for equations based on the text input.

        Hides items that do not match the search query and shows those that do.
        """
        search_text = self.searchMathEquations.text().lower()
        for i in range(self.mathQuestions.count()):
            item = self.mathQuestions.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def add_equation(self, item: QListWidgetItem):
        """
        Add an equation to the selected page based on the selected item.

        Args:
            item (QListWidgetItem): The item representing the equation type.

        Displays warnings if no page is selected or if the equation type is not implemented.
        """
        selected_page = self.selectedPage
        if selected_page is None:
            QMessageBox.warning(self, "No Page Selected", "Please select a page to add the equation.")
            return

        equation_type = item.text().strip()
        equation_functions = {
            "3A Expanding and collecting like terms": qd.linear_equation_popup,
            "3B Factorising": qd.factorise_equation_popup,
            "3C Quadratic Equations": qd.quadratic,
            "3D Graphing Quadratics": qd.graph_quadratic,
            "3E Completing the square and turning points": qd.completing_the_square,
            "3F Solving Quadratic Inequalities": qd.quadratic_inequality
        }

        # Retrieve the function corresponding to the equation type
        func = equation_functions.get(equation_type)
        if func:
            if callable(func):
                func(self)  # Execute the function to add the equation
        else:
            QMessageBox.warning(self, "Not Implemented", f"The equation type '{equation_type}' is not implemented yet.")

    def save_pdf(self):
        """
        Export the current project as a PDF file.

        Prompts the user to select a save location and handles the rendering
        of each page into the PDF. Notifies the user upon success or failure.
        """
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf);;All Files (*)")
            if not file_name:
                return  # User cancelled the save dialog

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))  # Set paper size to A4
            printer.setOutputFileName(file_name)
            painter = QPainter()

            if not painter.begin(printer):
                QMessageBox.warning(self, "Error", "Failed to open file for writing.")
                return

            # Render the title page if it exists
            title_layout = self.scrollAreaTitlePageWidgetContents.layout()
            if title_layout and title_layout.count() > 0:
                title_page = title_layout.itemAt(0).widget()
                title_page.render(painter)

            # Render each question page
            question_layout = self.scrollAreaQuestionWidgetContents.layout()
            for i in range(question_layout.count()):
                if i > 0 or (title_layout and question_layout.count() > 0):
                    printer.newPage()  # Start a new page in the PDF
                question_page_widget = question_layout.itemAt(i).widget()
                question_page_widget.render(painter)

            # Render each answer page
            answer_layout = self.scrollAreaAnswersWidgetContents.layout()
            for i in range(answer_layout.count()):
                printer.newPage()
                answer_page_widget = answer_layout.itemAt(i).widget()
                answer_page_widget.render(painter)

            painter.end()
            QMessageBox.information(self, "Success", "PDF saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the PDF: {e}")

    def save_project(self):
        """
        Save the current project.

        If a save file already exists, it saves to that file. Otherwise, it
        prompts the user to choose a save location.
        """
        try:
            if self.current_save_file:
                sae.save_project_data(self, self.current_save_file)
                QMessageBox.information(self, "Success", "Project saved successfully.")
            else:
                self.save_project_as()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the project: {e}")

    def save_project_as(self):
        """
        Save the current project with a new file name.

        Prompts the user to choose a location and file name for the project
        and updates the current save file path accordingly.
        """
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Project As", "",
                "Math Worksheet Projects (*.mwp);;All Files (*)"
            )
            if file_name:
                self.current_save_file = file_name
                sae.save_project_data(self, file_name)
                QMessageBox.information(self, "Success", "Project saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the project: {e}")

    def open_project(self):
        """
        Open an existing project file.

        Prompts the user to select a project file and loads its data into the application.
        Updates the current save file path upon successful loading.
        """
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open Project", "",
                "Math Worksheet Projects (*.mwp);;All Files (*)"
            )
            if file_name:
                sae.load_project_data(self, file_name)
                self.current_save_file = file_name
                QMessageBox.information(self, "Success", "Project loaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while opening the project: {e}")

    def exit_application(self):
        """
        Exit the application safely.

        Calls the backend method to handle any necessary cleanup before exiting.
        """
        try:
            sae.exit_application(self)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while exiting the application: {e}")


def main():
    """
    The main entry point of the application.

    Initialises the QApplication, creates the main window, and starts the event loop.
    """
    app = QApplication([])
    window = MyGui()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
