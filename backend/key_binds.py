from PyQt6.QtCore import QObject, Qt, QEvent
from PyQt6.QtWidgets import QMessageBox, QGraphicsScene

class EquationKeyHandler(QObject):
    """
    An event filter to handle key bindings within a QGraphicsScene.
    Specifically listens for the Delete key to remove selected equations.
    """

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def eventFilter(self, obj, event):
        # Ensure the event is within a QGraphicsScene
        if isinstance(obj, QGraphicsScene):
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Delete:
                    self.handle_delete_key(obj)
                    return True
        # For all other events, pass them on
        return super().eventFilter(obj, event)

    def handle_delete_key(self, scene):
        """
        Deletes the currently selected equation(s) in the scene,
        and their corresponding answers in the answer page.
        """
        selected_items = scene.selectedItems()
        if not selected_items:
            # Inform the user that no equation is selected
            QMessageBox.information(self.main_window, "No Selection", "No equation is selected to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self.main_window,
            "Delete Equation",
            f"Are you sure you want to delete the selected {len(selected_items)} equation(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                # Remove answer items if they exist
                if hasattr(item, 'answer_items'):
                    for answer_item in item.answer_items:
                        # Remove the answer item from its scene
                        answer_item.scene().removeItem(answer_item)
                # Remove the equation item from the scene
                scene.removeItem(item)
            QMessageBox.information(self.main_window, "Deleted", "Selected equation(s) and their answers have been deleted.")
        else:
            # User chose not to delete
            pass
