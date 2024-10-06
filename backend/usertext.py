from PyQt6.QtWidgets import QGraphicsTextItem
from PyQt6.QtGui import QFont, QPen, QPainterPath
from PyQt6.QtCore import Qt

class TextItem(QGraphicsTextItem):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsTextItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        # Initially, set no text interaction; will enable on double-click
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.setAcceptHoverEvents(True)
        self.setDefaultTextColor(Qt.GlobalColor.black)
        self.setFont(QFont("Arial", 16))

    def paint(self, painter, option, widget):
        # First, call the base class paint method
        super().paint(painter, option, widget)
        # If the item is selected, draw a thicker border
        if self.isSelected():
            rect = self.boundingRect()
            pen = QPen(Qt.GlobalColor.blue, 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)

    def shape(self):
        # Increase the clickable/draggable area
        path = QPainterPath()
        rect = self.boundingRect()
        margin = 10  # Increase the area by 10 pixels on all sides (Too small otherwise)
        rect = rect.adjusted(-margin, -margin, margin, margin)
        path.addRect(rect)
        return path

    def mouseDoubleClickEvent(self, event):
        # On double-click, enable text editing
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        # When losing focus, disable text editing
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        super().focusOutEvent(event)
        # Check if the text is empty; if so, delete the item
        if not self.toPlainText().strip():
            scene = self.scene()
            if scene:
                scene.removeItem(self)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        # If the user presses Enter or Return, end editing
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clearFocus()
