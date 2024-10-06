from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QSizePolicy, QGraphicsTextItem
)
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtCore import Qt
from backend.key_binds import EquationKeyHandler


class QuestionPage(QGraphicsView):
    """
    Represents a Question Page within the application, displaying questions
    with their corresponding answers.
    """

    def __init__(self, page_number, main_window, parent=None):
        """
        Initialise the QuestionPage with a specific page number and link to the main window.

        Parameters:
        - page_number (int): The identifier for the page being created.
        - main_window (QMainWindow): Reference to the main application window.
        - parent (QWidget, optional): The parent widget in the widget hierarchy.
                                        Defaults to None if not provided.
        """
        # Create a new QGraphicsScene for this page
        scene = QGraphicsScene()
        super().__init__(scene, parent)

        # Reference to the main application window
        self.main_window = main_window

        # Enable anti-aliasing for smoother rendering of graphics and text
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
        )

        # Selection state of the page
        self.isSelected = False

        # Assign the page number
        self.page_number = page_number

        # Set the fixed size of the page (A4 size in pixels at 96 DPI)
        self.setFixedSize(794, 1150)
        scene.setSceneRect(0, 0, 794, 1123)

        # Disable scroll bars for a cleaner look
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set the border style to indicate unselected state
        self.setStyleSheet("border: 2px solid black")

        # Ensure the widget does not resize automatically
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Assign a unique object name based on the page number
        self.setObjectName(f"Question Page {page_number}")

        # Add the page number label to the page
        self.add_page_number()

        # Initialise and install the EquationKeyHandler as an event filter on the scene
        self.key_handler = EquationKeyHandler(main_window)
        scene.installEventFilter(self.key_handler)

    def add_page_number(self):
        """
        Adds the page number text at the bottom centre of the page.
        """
        # Create a QGraphicsTextItem with the page number
        page_number_text = QGraphicsTextItem(f"Page {self.page_number}")

        # Define the font for the page number
        page_number_font = QFont("Times New Roman", 12)
        page_number_text.setFont(page_number_font)

        # Set the text color to black
        page_number_text.setDefaultTextColor(Qt.GlobalColor.black)

        # Calculate the bounding rectangle of the text for positioning
        text_rect = page_number_text.boundingRect()

        # Position the page number at the bottom centre of the scene
        x_position = (self.scene().width() - text_rect.width()) / 2
        y_position = self.scene().height() - text_rect.height() - 20

        page_number_text.setPos(x_position, y_position)

        # Add the page number text item to the scene
        self.scene().addItem(page_number_text)

    def mouseDoubleClickEvent(self, event):
        """
        Handles double-click events on the page. Determines whether to select the page
        or add a new text item based on the location and current selection state.

        Parameters:
        - event (QMouseEvent): The mouse event triggering the double-click.
        """
        # Map the event position to the scene coordinates
        scene_pos = self.mapToScene(event.position().toPoint())

        # Retrieve items at the clicked position
        items_at_pos = self.scene().items(scene_pos)

        # Retrieve currently selected items in the scene
        selected_items = self.scene().selectedItems()

        # Determine if this page is currently selected
        page_is_selected = self.main_window.selectedPage == self

        # Handle page selection
        if not self.isSelected:
            # Deselect other pages by resetting their border color
            for view in self.parent().findChildren(QGraphicsView):
                if hasattr(view, 'isSelected'):
                    view.isSelected = False
                    view.setStyleSheet("border: 2px solid black")

            # Select the current page by setting its border to blue
            self.isSelected = True
            self.setStyleSheet("border: 2px solid blue")

            # Update the main window's reference to the currently selected page
            self.main_window.selectedPage = self

        # Determine whether to add a new text item
        if not items_at_pos and not selected_items and page_is_selected:
            # No items under cursor, no items selected, and page is selected
            self.add_text_at_position(scene_pos)
            # Accept the event to indicate it has been handled
            event.accept()
        else:
            # Do not add text, pass the event to items or ignore
            event.ignore()
            super().mouseDoubleClickEvent(event)

    def add_text_at_position(self, position):
        """
        Adds a new text item to the scene at the specified position.

        Parameters:
        - position (QPointF): The position within the scene where the text item will be added.
        """
        from backend.usertext import TextItem

        # Create a new TextItem with default text
        text_item = TextItem("New Text")

        # Set the position of the text item within the scene
        text_item.setPos(position)

        # Add the text item to the scene
        self.scene().addItem(text_item)

        # Optionally, set focus and select the text item for immediate editing
        text_item.setFocus()
        text_item.setSelected(True)

        # Enable editing mode for the text item
        text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
