from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsRectItem,
    QSizePolicy
)
from PyQt6.QtGui import QPainter, QFont, QColor, QCursor
from PyQt6.QtCore import Qt


class IntroPage(QGraphicsView):
    """
    Represents the Intro/Title Page with detailed sections.
    """

    def __init__(self, page_number, parent=None, add_default_items=True):
        scene = QGraphicsScene()
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        self.isSelected = False
        self.page_number = page_number
        self.setFixedSize(794, 1150)
        scene.setSceneRect(0, 0, 794, 1123)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("border: 2px solid black")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setObjectName(f"Title Page {page_number}")

        if add_default_items:
            # Add default sections only if add_default_items is True
            # Add Header Section
            self.add_header_section(scene)

            # Add Table Section
            self.add_table_section(scene)

            # Add Instruction Section
            self.add_instruction_section(scene)

            # Add Final Instruction
            self.add_final_instruction(scene)

    def make_editable_text(self, text, font, pos, parent=None):
        """
        Creates a QGraphicsTextItem that is editable and draggable.
        """
        text_item = QGraphicsTextItem(text, parent)
        text_item.setFont(font)
        text_item.setDefaultTextColor(Qt.GlobalColor.black)
        text_item.setPos(*pos)
        text_item.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditable | Qt.TextInteractionFlag.TextEditorInteraction)
        text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
        text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
        text_item.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        return text_item

    def add_header_section(self, scene):
        """
        Adds the header section to the scene.
        """
        # "NAME:" label at top left
        name_font = QFont("Times New Roman", 16)
        name_label = self.make_editable_text("NAME:", name_font, (50, 50))
        scene.addItem(name_label)

        # Blank line beside "NAME:"
        blank_line = QGraphicsRectItem(75, 25, 200, 1, parent=name_label)
        blank_line.setBrush(QColor(Qt.GlobalColor.black))
        blank_line.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        blank_line.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(blank_line)

        # "UNIT 1" Label
        unit_font = QFont("Times New Roman", 20, QFont.Weight.Bold)
        unit_label = self.make_editable_text("UNIT 1", unit_font, (0, 150))
        unit_label.setPos((scene.width() - unit_label.boundingRect().width()) / 2, 150)
        scene.addItem(unit_label)

        # "MATHEMATICAL METHODS" Header below "UNIT 1"
        main_title_font = QFont("Times New Roman", 28, QFont.Weight.Bold)
        main_title = self.make_editable_text("MATHEMATICAL METHODS", main_title_font, (0, 200))
        main_title.setPos((scene.width() - main_title.boundingRect().width()) / 2, 200)
        scene.addItem(main_title)

        # "SAC 1 Part 1: Volume of a Box" <- From an old test
        subtitle_font = QFont("Times New Roman", 20)
        subtitle = self.make_editable_text("SAC 1 Part 1: Volume of a Box", subtitle_font, (0, 250))
        subtitle.setPos((scene.width() - subtitle.boundingRect().width()) / 2, 250)
        scene.addItem(subtitle)

        # Reading and Writing Time
        time_font = QFont("Times New Roman", 16)
        reading_time = self.make_editable_text("Reading time: 5 minutes", time_font, (0, 300))
        reading_time.setPos((scene.width() - reading_time.boundingRect().width()) / 2, 300)
        writing_time = self.make_editable_text("Writing time: 45 minutes", time_font, (0, 330))
        writing_time.setPos((scene.width() - writing_time.boundingRect().width()) / 2, 330)
        scene.addItem(reading_time)
        scene.addItem(writing_time)

    def add_table_section(self, scene):
        """
        Adds the table section to the scene.
        """
        table_width = 400
        table_height = 80
        table_x = (scene.width() - table_width) / 2
        table_y = 400

        # Draw table border
        table_rect = QGraphicsRectItem(table_x, table_y, table_width, table_height)
        table_rect.setPen(QColor(Qt.GlobalColor.black))
        table_rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        table_rect.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(table_rect)

        # Define column widths (Must add to be 1)
        col1_width = table_width * 0.33
        col2_width = table_width * 0.33
        col3_width = table_width * 0.34

        # Draw vertical lines only
        line1 = QGraphicsRectItem(table_x + col1_width, table_y, 2, table_height, parent=table_rect)
        line1.setBrush(QColor(Qt.GlobalColor.black))
        line1.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        line1.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(line1)

        line2 = QGraphicsRectItem(table_x + col1_width + col2_width, table_y, 2, table_height, parent=table_rect)
        line2.setBrush(QColor(Qt.GlobalColor.black))
        line2.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        line2.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(line2)

        # Draw horizontal line for headers
        header_height = 40
        line3 = QGraphicsRectItem(table_x, table_y + header_height, table_width, 2, parent=table_rect)
        line3.setBrush(QColor(Qt.GlobalColor.black))
        line3.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        line3.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(line3)

        # Add table headers with multiline
        headers = ["Number of\nQuestions", "Number to be\nAnswered", "Number of\nMarks"]
        header_font = QFont("Times New Roman", 14, QFont.Weight.Bold)
        for i, header in enumerate(headers):
            header_item = QGraphicsTextItem(header, parent=table_rect)
            header_item.setFont(header_font)
            header_item.setDefaultTextColor(Qt.GlobalColor.black)
            # Adjust text width for wrapping
            header_item.setTextWidth(col1_width if i < 2 else col3_width)
            # Center align
            header_rect = header_item.boundingRect()
            x = table_x + (col1_width * i) + (col1_width - header_rect.width()) / 2
            y = table_y + (header_height - header_rect.height()) / 2
            header_item.setPos(x, y)
            header_item.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextEditable | Qt.TextInteractionFlag.TextEditorInteraction)
            header_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
            header_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
            scene.addItem(header_item)

        # Add table data row <- Number of marks stuff
        data = ["1", "1", "1"]
        data_font = QFont("Times New Roman", 14)
        for i, datum in enumerate(data):
            data_item = QGraphicsTextItem(datum, parent=table_rect)
            data_item.setFont(data_font)
            data_item.setDefaultTextColor(Qt.GlobalColor.black)
            data_item.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextEditable | Qt.TextInteractionFlag.TextEditorInteraction)
            data_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
            data_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
            # Center align
            data_rect = data_item.boundingRect()
            x = table_x + (col1_width * i) + (col1_width - data_rect.width()) / 2
            y = table_y + header_height + (table_height - header_height - data_rect.height()) / 2
            data_item.setPos(x, y)
            scene.addItem(data_item)

    def add_instruction_section(self, scene):
        """
        Adds the instruction section with bullet points to the scene.
        """
        box_width = 700
        box_height = 450
        box_x = (scene.width() - box_width) / 2
        box_y = 500

        # Draw instruction box
        instruction_box = QGraphicsRectItem(box_x, box_y, box_width, box_height)
        instruction_box.setPen(QColor(Qt.GlobalColor.black))
        instruction_box.setBrush(QColor(Qt.GlobalColor.white))
        instruction_box.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        instruction_box.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(instruction_box)

        # Define subsections and their content
        subsections = {
            "Not allowed items:": [
                "Blank sheets of paper.",
                "Liquid white-out."
            ],
            "Allowed items:": [
                "Pens, pencils, erasers, rulers, and calculators."
            ],
            "Materials Supplied:": [
                "Question and answer book.",
                "Working space is provided throughout the book."
            ],
            "Instructions:": [
                "Fill out the sheet provided for responses.",
                "Use English for all answers.",
                "Non-scaled diagrams are allowed."
            ]
        }

        # Starting position for text within the box
        current_y = box_y + 20
        left_margin = box_x + 20

        for title, bullets in subsections.items():
            # Add subsection title
            title_font = QFont("Times New Roman", 16, QFont.Weight.Bold)
            title_item = self.make_editable_text(title, title_font, (left_margin, current_y), parent=instruction_box)
            scene.addItem(title_item)

            # Add bullet points
            bullet_font = QFont("Times New Roman", 14)
            for bullet in bullets:
                bullet_text = f"• {bullet}"
                bullet_item = self.make_editable_text(bullet_text, bullet_font, (left_margin + 30, current_y + 30),
                                                      parent=instruction_box)
                scene.addItem(bullet_item)
                # Move down for next bullet
                current_y += 35
            # Increased space after each subsection
            current_y += 15

    def add_final_instruction(self, scene):
        """
        Adds the final instruction box at the bottom of the page.
        """
        box_width = 600
        box_height = 70
        box_x = (scene.width() - box_width) / 2
        box_y = 950

        # Draw final instruction box
        final_box = QGraphicsRectItem(box_x, box_y, box_width, box_height)
        final_box.setPen(QColor(Qt.GlobalColor.black))
        final_box.setBrush(QColor(Qt.GlobalColor.white))
        final_box.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        final_box.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(final_box)

        # Add text
        final_font = QFont("Times New Roman", 16, QFont.Weight.Bold)
        final_text = QGraphicsTextItem(
            "Students are NOT permitted to bring mobile phones and/or any other unauthorized electronic devices into the room.",
            parent=final_box
        )
        final_text.setFont(final_font)
        final_text.setDefaultTextColor(Qt.GlobalColor.black)
        final_text.setTextWidth(box_width - 20)  # Padding
        final_text.setPos(box_x + 10, box_y + 10)
        final_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditable | Qt.TextInteractionFlag.TextEditorInteraction)
        final_text.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable, True)
        final_text.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(final_text)

    def mouseDoubleClickEvent(self, event):
        """
        Handles double-click events to select the page.
        """
        for view in self.parent().findChildren(QGraphicsView):
            if hasattr(view, 'isSelected'):
                view.isSelected = False
                view.setStyleSheet("border: 2px solid black")
        self.isSelected = True
        self.setStyleSheet("border: 2px solid blue")
        self.parent().selectedPage = self
        super().mouseDoubleClickEvent(event)
