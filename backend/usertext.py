from PyQt6.QtWidgets import QGraphicsTextItem
from PyQt6.QtGui import QFont, QPen, QPainterPath, QTextCharFormat
from PyQt6.QtCore import Qt, pyqtSignal, QObject

class TextItem(QGraphicsTextItem, QObject):
    itemSelected = pyqtSignal(QGraphicsTextItem)  # Signal to notify when this TextItem is selected
    itemDeselected = pyqtSignal()  # Signal to notify when this TextItem is deselected
    selectionChanged = pyqtSignal(bool)
    editingStarted = pyqtSignal()
    editingFinished = pyqtSignal()
    fontSizeChanged = pyqtSignal(int)

    def __init__(self, text="", parent=None):
        QGraphicsTextItem.__init__(self, text, parent)
        QObject.__init__(self)
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
        self._hasSelection = False

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.isSelected():
            rect = self.boundingRect()
            pen = QPen(Qt.GlobalColor.blue, 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)

    def shape(self):
        # Increase the clickable/draggable area
        path = QPainterPath()
        rect = self.boundingRect()
        margin = 10  # Increase the area by 10 pixels on all sides
        rect = rect.adjusted(-margin, -margin, margin, margin)
        path.addRect(rect)
        return path

    def mouseDoubleClickEvent(self, event):
        # On double-click, enable text editing
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFocus()
        self.editingStarted.emit()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        # When losing focus, disable text editing
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        super().focusOutEvent(event)
        self.editingFinished.emit()
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
        self.checkSelection()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isSelected():
            self.itemSelected.emit(self)
        else:
            self.itemDeselected.emit()
        self.checkSelection()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.checkSelection()

    def checkSelection(self):
        cursor = self.textCursor()
        has_selection = cursor.hasSelection()
        if has_selection != self._hasSelection:
            self._hasSelection = has_selection
            self.selectionChanged.emit(has_selection)
            if has_selection:
                # Emit the current font size
                current_font_size = cursor.charFormat().fontPointSize()
                if current_font_size == 0:  # Default font size if not set
                    current_font_size = self.font().pointSize()
                self.fontSizeChanged.emit(int(current_font_size))

    def applyBold(self):
        try:
            # Apply or remove bold formatting to the selected text
            cursor = self.textCursor()
            if not cursor or not cursor.hasSelection():
                return
            fmt = QTextCharFormat()
            current_weight = cursor.charFormat().fontWeight()
            if current_weight == QFont.Weight.Bold:
                fmt.setFontWeight(QFont.Weight.Normal)
            else:
                fmt.setFontWeight(QFont.Weight.Bold)
            cursor.mergeCharFormat(fmt)
        except Exception as e:
            print(f"Error in applyBold: {e}")

    def applyItalic(self):
        try:
            # Apply or remove italic formatting to the selected text
            cursor = self.textCursor()
            if not cursor or not cursor.hasSelection():
                return
            fmt = QTextCharFormat()
            fmt.setFontItalic(not cursor.charFormat().fontItalic())
            cursor.mergeCharFormat(fmt)
        except Exception as e:
            print(f"Error in applyItalic: {e}")

    def applyUnderline(self):
        try:
            # Apply or remove underline formatting to the selected text
            cursor = self.textCursor()
            if not cursor or not cursor.hasSelection():
                return
            fmt = QTextCharFormat()
            fmt.setFontUnderline(not cursor.charFormat().fontUnderline())
            cursor.mergeCharFormat(fmt)
        except Exception as e:
            print(f"Error in applyUnderline: {e}")

    def setFontSize(self, size):
        try:
            cursor = self.textCursor()
            if not cursor or not cursor.hasSelection():
                return
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            cursor.mergeCharFormat(fmt)
        except Exception as e:
            print(f"Error in setFontSize: {e}")
