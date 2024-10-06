from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import (
    QGraphicsPixmapItem, QGraphicsScene, QMessageBox, QGraphicsLineItem,
    QDialog, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QPixmap, QIntValidator, QImage
from PyQt6.QtCore import QPointF, QByteArray
from backend import mgen
from matplotlib import pyplot as plt
from io import BytesIO


class BaseTextItem(QGraphicsPixmapItem):
    """
    A base class for text items displayed as pixmaps in a QGraphicsScene.
    It uses Matplotlib to render text (including LaTeX) into a QPixmap.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialise the BaseTextItem with optional arguments.
        """
        super().__init__(*args, **kwargs)

    def set_plain_text(self, text):
        """
        Sets the text to be displayed by rendering it with Matplotlib and converting
        the rendered image into a QPixmap.

        Parameters:
        - text (str): The text string to display, which can include LaTeX syntax.
        """
        try:
            self.text = text
            # Create a Matplotlib figure with no background
            fig = plt.figure(figsize=(1, 1), facecolor='none')

            # Configure Matplotlib's mathtext to use Times New Roman font
            plt.rcParams['mathtext.fontset'] = 'custom'
            plt.rcParams['mathtext.rm'] = 'Times New Roman'
            plt.rcParams['mathtext.it'] = 'Times New Roman:italic'
            plt.rcParams['mathtext.bf'] = 'Times New Roman:bold'

            # Add text to the figure
            text_obj = plt.text(
                0, 0, f'${text}$',  # Render text as LaTeX
                fontname='Times New Roman', size=25,
                ha='left', va='bottom', colour='black'
            )

            # Remove axes for a better look
            plt.axis('off')

            # Draw the canvas to calculate bounding box
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            bbox = text_obj.get_window_extent(renderer)
            width, height = bbox.width / fig.dpi, bbox.height / fig.dpi

            # Resize figure based on text size
            fig.set_size_inches(width, height)
            text_obj.set_position((0, 0))
            fig.canvas.draw()

            # Save the figure to a buffer in SVG format
            buf = BytesIO()
            plt.savefig(
                buf, format='svg', bbox_inches='tight',
                transparent=True, dpi=fig.dpi
            )
            plt.close(fig)
            buf.seek(0)

            # Load the SVG data into a QImage and convert to QPixmap
            image = QImage()
            image.loadFromData(buf.read())
            pixmap = QPixmap.fromImage(image)
            self.setPixmap(pixmap)
        except Exception as e:
            print(f"An error occurred in set_plain_text: {e}")


class EditableTextItem(BaseTextItem):
    """
    A text item that is editable and movable within a QGraphicsScene (The page).
    It displays equations and allows users to interact with them.
    """

    def __init__(self, equation_type, difficulty, answer, *args, **kwargs):
        """
        Initialise the EditableTextItem with specific properties.

        Parameters:
        - equation_type (str): The type of equation (e.g., "Linear Equation").
        - difficulty (str): The difficulty level (e.g., "Easy").
        - answer (str or QPixmap): The answer associated with the equation.
        """
        super().__init__(*args, **kwargs)
        # Enable item to be movable and selectable within the scene
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)

        self.equation_type = equation_type
        self.difficulty = difficulty
        self.drag_offset = QPointF(0, 0)
        self.answer = answer
        # List to hold associated answer items
        self.answer_items = []

    def mouse_press_event(self, event):
        """
        Handles the mouse press event to initiate dragging.

        Parameters:
        - event (QGraphicsSceneMouseEvent): The mouse event.
        """
        try:
            # Calculate the offset between the mouse position and the item's top-left corner
            # This is because the item kept snapping to the top-left corner of the curser
            self.drag_offset = event.pos() - self.boundingRect().topLeft()
            super().mousePressEvent(event)
        except Exception as e:
            print(f"An error occurred in mouse_press_event: {e}")

    def mouse_move_event(self, event):
        """
        Handles the mouse move event to implement snapping to a grid.

        Parameters:
        - event (QGraphicsSceneMouseEvent): The mouse event.
        """
        try:
            if self.isSelected():
                # Calculate the new position with snapping to a 10x10 grid
                new_pos = event.scenePos() - self.drag_offset
                grid_size = 10
                new_x = round(new_pos.x() / grid_size) * grid_size
                new_y = round(new_pos.y() / grid_size) * grid_size
                snapped_pos = QPointF(new_x, new_y)
                self.setPos(snapped_pos)
            else:
                super().mouseMoveEvent(event)
        except Exception as e:
            print(f"An error occurred in mouse_move_event: {e}")

    def mouse_double_click_event(self, event):
        """
        Handles the mouse double-click event to show a dialog with question details.

        Parameters:
        - event (QGraphicsSceneMouseEvent): The mouse event.
        """
        try:
            dialog = QDialog()
            dialog.setWindowTitle("Answer")
            layout = QVBoxLayout()

            # Display the question text
            question_label = QLabel(f"Question: {self.text}")
            layout.addWidget(question_label)

            # Display the answer, which can be text or an image
            if isinstance(self.answer, QPixmap):
                answer_label = QLabel()
                answer_label.setPixmap(self.answer)
                layout.addWidget(answer_label)
            else:
                answer_label = QLabel(f"Answer: {self.answer}")
                layout.addWidget(answer_label)

            # Display the difficulty level
            difficulty_label = QLabel(f"Difficulty: {self.difficulty}")
            layout.addWidget(difficulty_label)

            # OK button to close the dialog
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(dialog.accept)
            layout.addWidget(ok_button)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            print(f"An error occurred in mouse_double_click_event: {e}")

# I use most of the same documentation here too since the classes are similar
class ExampleTextItem(QGraphicsSvgItem):
    """
    A text item that uses SVG rendering for displaying equations, including LaTeX.
    It is used for displaying example equations in the question dialog UI.
    """

    def __init__(self, equation_type, difficulty, answer, *args, **kwargs):
        """
        Initialise the ExampleTextItem with specific properties.

        Parameters:
        - equation_type (str): The type of equation.
        - difficulty (str): The difficulty level.
        - answer (str): The answer associated with the equation.
        """
        super().__init__(*args, **kwargs)
        self.text = None
        self.equation_type = equation_type
        self.difficulty = difficulty
        self.answer = answer

    def set_plain_text(self, text):
        """
        Sets the text to be displayed by rendering it with Matplotlib and converting
        the rendered SVG into a QSvgRenderer.

        Parameters:
        - text (str): The text string to display, which can include LaTeX syntax.
        """
        try:
            self.text = text
            # Create a Matplotlib figure with no background
            fig = plt.figure(figsize=(1, 1), facecolour="None")

            # Configure Matplotlib's mathtext to use Times New Roman font
            plt.rcParams['mathtext.fontset'] = 'custom'
            plt.rcParams['mathtext.rm'] = 'Times New Roman'
            plt.rcParams['mathtext.it'] = 'Times New Roman:italic'
            plt.rcParams['mathtext.bf'] = 'Times New Roman:bold'

            # Add main equation text
            text_obj = plt.text(
                0, 0, f'${text}$',  # Render text as LaTeX
                fontname='Times New Roman', size=30,
                ha='left', va='bottom', colour='black'
            )

            # Optionally add the answer below the equation in red
            if self.answer != "None":
                plt.text(
                    0, -0.6, f'Answer: {self.answer}',
                    fontname='Times New Roman', size=20,
                    ha='left', va='bottom', colour='red'
                )

            # Remove axes for a better look
            plt.axis('off')

            # Draw the canvas to calculate bounding box
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            bbox = text_obj.get_window_extent(renderer)
            width, height = bbox.width / fig.dpi, bbox.height / fig.dpi

            # Resize figure based on text size
            fig.set_size_inches(width, height)
            text_obj.set_position((0, 0))
            fig.canvas.draw()

            # Save the figure to a buffer in SVG format
            buf = BytesIO()
            plt.savefig(buf, format='svg', bbox_inches='tight', transparent=True)
            plt.close(fig)
            buf.seek(0)

            # Load the SVG data into QSvgRenderer and set it for the item
            svg_data = buf.getvalue().decode('utf-8')
            renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
            self.setSharedRenderer(renderer)
        except Exception as e:
            print(f"An error occurred in set_plain_text: {e}")


def create_question_dialog(main_window, equation_type, generate_equation_func):
    """
    Creates and manages a dialog for generating and adding equations to the main window.

    Parameters:
    - main_window (QMainWindow): The main application window.
    - equation_type (str): The type of equation to generate (e.g., "Linear Equation").
    - generate_equation_func (callable): A function that generates equations based on difficulty.
    """
    try:
        # Default difficulty level
        diff = "Easy"
        # Load UI from .ui file
        dialog = loadUi('frontend/questiondialog.ui')
        # Prevent resizing
        dialog.setFixedSize(dialog.size())
        # Set dialog title
        dialog.setWindowTitle(equation_type)

        # Connect the cancel button to close the dialog
        dialog.cancelButton.clicked.connect(dialog.close)

        # Set up the QGraphicsScene for displaying example equations
        scene = QGraphicsScene()
        dialog.questionView.setScene(scene)

        def update_example_equations():
            """
            Updates the example equations displayed in the dialog based on the current difficulty.
            """
            try:
                nonlocal diff
                # Clear existing items
                scene.clear()
                # Initial y-position for placing items
                y_pos = 0

                # Generate and display 4 example equations
                for _ in range(4):
                    try:
                        difficulty, equation_text, answer = generate_equation_func(diff)
                    except Exception as e:
                        print(f"An error occurred in generate_equation_func: {e}")
                        continue

                    if equation_type == "Graphing Quadratics":
                        # Create an ExampleTextItem without an answer
                        equation_item = ExampleTextItem(equation_type, difficulty, "None")
                        equation_item.set_plain_text(equation_text)
                        equation_item.setPos(0, y_pos)
                        scene.addItem(equation_item)
                        y_pos += equation_item.boundingRect().height() + 10

                        # Add the answer as a QGraphicsPixmapItem
                        pixmap_item = QGraphicsPixmapItem(answer)
                        # Maximum width for the pixmap
                        max_width = 200
                        pixmap_item.setScale(max_width / pixmap_item.pixmap().width())
                        scene.addItem(pixmap_item)
                        pixmap_item.setPos(0, y_pos)
                        y_pos += pixmap_item.boundingRect().height() + 20
                    else:
                        # Create an ExampleTextItem with an answer
                        equation_item = ExampleTextItem(equation_type, difficulty, answer)
                        equation_item.set_plain_text(equation_text)
                        equation_item.setPos(0, y_pos)
                        scene.addItem(equation_item)
                        y_pos += equation_item.boundingRect().height() + 20
            except Exception as e:
                print(f"An error occurred in update_example_equations: {e}")

        def set_difficulty(new_diff):
            """
            Sets the difficulty level and updates the example equations accordingly.

            Parameters:
            - new_diff (str): The new difficulty level (e.g., "Medium").
            """
            try:
                nonlocal diff
                diff = new_diff
                update_example_equations()
            except Exception as e:
                print(f"An error occurred in set_difficulty: {e}")

        # Connect difficulty buttons to set the difficulty level
        dialog.easyButton.clicked.connect(lambda: set_difficulty("Easy"))
        dialog.mediumButton.clicked.connect(lambda: set_difficulty("Medium"))
        dialog.hardButton.clicked.connect(lambda: set_difficulty("Hard"))
        # Set default selection
        dialog.easyButton.setChecked(True)
        # Reloads the example equations to make new ones
        update_example_equations()

        # Set up validator to ensure the number of questions is between 0 and 99
        validator = QIntValidator(0, 99)
        dialog.numofqueLine.setValidator(validator)

        def enable_buttons():
            """
            Enables or disables the OK and Add buttons based on the input in numofqueLine. (This is where the user specifies how many equations they want to add)
            """
            try:
                if dialog.numofqueLine.text():
                    dialog.okButton.setEnabled(True)
                    dialog.addButton.setEnabled(True)
                else:
                    dialog.okButton.setEnabled(False)
                    dialog.addButton.setEnabled(False)
            except Exception as e:
                print(f"An error occurred in enable_buttons: {e}")

        # Connect text change in numofqueLine to enable_buttons
        dialog.numofqueLine.textChanged.connect(enable_buttons)
        # Dictionary to track y-positions for answers (Didn't finish this part :()
        y_pos_answers = {}

        def add_equations():
            """
            Adds the specified number of equations to the selected page and its answer page.
            """
            try:
                num_of_equations_text = dialog.numofqueLine.text()
                if not num_of_equations_text.isdigit() or int(num_of_equations_text) <= 0:
                    QMessageBox.warning(dialog, "Invalid Input", "Please enter a valid number of equations.")
                    return

                num_of_equations = int(num_of_equations_text)

                if main_window.selectedPage is None:
                    QMessageBox.warning(dialog, "No Page Selected", "Please select a question page to add equations.")
                    return
                # Initial y-position for questions
                y_pos_question = 10
                page_number = getattr(main_window.selectedPage, 'page_number', None)
                if page_number is None:
                    QMessageBox.warning(dialog, "Invalid Page", "Selected page does not have a valid page number.")
                    return

                # Retrieve or create the corresponding answer page
                answer_page = main_window.get_answer_page(page_number)
                if answer_page is None:
                    reply = QMessageBox.question(
                        dialog, "Answer Page Not Found",
                        f"No answer page found for page number {page_number}. Would you like to create one?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        answer_page = main_window.create_answer_page_with_number(page_number)
                        if answer_page is None:
                            QMessageBox.critical(dialog, "Error", "Failed to create an answer page.")
                            return
                    else:
                        QMessageBox.information(dialog, "Operation Cancelled", "Equations will not be added.")
                        return
                # Initial y-position for answers
                y_pos_answer = 10

                for _ in range(num_of_equations):
                    try:
                        # Generate an equation based on the current difficulty
                        difficulty, equation_text, answer = generate_equation_func(diff)
                    except Exception as e:
                        print(f"An error occurred in generate_equation_func during add_equations: {e}")
                        continue
                    try:
                        # Create an EditableTextItem for the question
                        equation_item = EditableTextItem(equation_type, difficulty, answer)
                        equation_item.set_plain_text(equation_text)

                        if main_window.selectedPage is not None:
                            # Add the equation to the selected page's scene
                            main_window.selectedPage.scene().addItem(equation_item)
                            # X-position (could be modified for layout)
                            x = 0
                            y = y_pos_question
                            equation_item.setPos(x, y)
                            y_pos_question += equation_item.boundingRect().height() + 10
                    except Exception as e:
                        print(f"An error occurred while adding question to page: {e}")
                        continue

                    if answer_page is not None:
                        try:
                            answer_items = []

                            # Create and add the answer text item
                            equation_text_item = AnswerTextItem()
                            equation_text_item.set_plain_text(equation_text)
                            answer_page.scene().addItem(equation_text_item)
                            equation_text_item.setPos(0, y_pos_answer)
                            y_pos_answer += equation_text_item.boundingRect().height() + 5
                            answer_items.append(equation_text_item)

                            # Add the answer, which can be text or an image
                            if isinstance(answer, QPixmap):
                                answer_item = QGraphicsPixmapItem(answer)
                                answer_item.setPos(0, y_pos_answer)
                                answer_page.scene().addItem(answer_item)
                                y_pos_answer += answer_item.boundingRect().height() + 5
                                answer_items.append(answer_item)
                            else:
                                answer_text_item = AnswerTextItem()
                                answer_text_item.set_plain_text(f"Answer: {answer}")
                                answer_page.scene().addItem(answer_text_item)
                                answer_text_item.setPos(0, y_pos_answer)
                                y_pos_answer += answer_text_item.boundingRect().height() + 5
                                answer_items.append(answer_text_item)

                            # Add a separator line between answers
                            separator_item = SeparatorItem()
                            separator_item.setPos(0, y_pos_answer)
                            answer_page.scene().addItem(separator_item)
                            y_pos_answer += separator_item.boundingRect().height() + 10
                            answer_items.append(separator_item)

                            # Link the answer items with the question item
                            equation_item.answer_items = answer_items
                        except Exception as e:
                            print(f"An error occurred while adding answer to page: {e}")
                            continue
            except Exception as e:
                print(f"An error occurred in add_equations: {e}")

        # Connect the OK button to add_equations and close the dialog
        dialog.okButton.clicked.connect(lambda: (add_equations(), dialog.close()))

        # Connect the Add button to add_equations without closing the dialog
        dialog.addButton.clicked.connect(add_equations)

        # Execute the dialog
        dialog.exec()
    except Exception as e:
        print(f"An error occurred in create_question_dialog: {e}")
        QMessageBox.critical(main_window, "Error", f"An error occurred: {e}")


class AnswerTextItem(BaseTextItem):
    """
    A specialised BaseTextItem for displaying answers in the answer page.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialise the AnswerTextItem with optional arguments.
        """
        super().__init__(*args, **kwargs)


class SeparatorItem(QGraphicsLineItem):
    """
    A line item used to separate different answers in the answer page.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialise the SeparatorItem by drawing a horizontal line.
        """
        super().__init__(*args, **kwargs)
        try:
            # Draw a horizontal line from (0,0) to (794,0) units (This is because the page is 794 units long)
            self.setLine(0, 0, 794, 0)
        except Exception as e:
            print(f"An error occurred in SeparatorItem.__init__: {e}")


def linear_equation_popup(main_window):
    """
    Opens a dialog for generating linear equations.

    Parameters:
    - main_window (QMainWindow): The main application window.
    """
    create_question_dialog(
        main_window, "Linear Equation", mgen.generate_linear_equation
    )


def factorise_equation_popup(main_window):
    """
    Opens a dialog for generating factorised equations.

    Parameters:
    - main_window (QMainWindow): The main application window.
    """
    create_question_dialog(
        main_window, "Factorise Equation", mgen.generate_factorise_equation
    )


def quadratic(main_window):
    """
    Opens a dialog for generating quadratic equations.

    Parameters:
    - main_window (QMainWindow): The main application window.
    """
    create_question_dialog(
        main_window, "Quadratic Equation", mgen.construct_quadratic
    )


def graph_quadratic(main_window):
    """
    Opens a dialog for generating graphing quadratic equations.

    Parameters:
    - main_window (QMainWindow): The main application window.
    """
    create_question_dialog(
        main_window, "Graphing Quadratics", mgen.generate_graphing_quadratic
    )


def completing_the_square(main_window):
    """
    Opens a dialog for generating equations involving completing the square.

    Parameters:
    - main_window (QMainWindow): The main application window.
    """
    create_question_dialog(
        main_window, "Completing the Square", mgen.completing_square_and_turning_point
    )


def quadratic_inequality(main_window):
    """
    Opens a dialog for generating quadratic inequalities.

    Parameters:
    - main_window (QMainWindow): The main application window.
    """
    create_question_dialog(
        main_window, "Quadratic Inequality", mgen.solving_quadratic_inequality
    )
