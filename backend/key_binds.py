from PyQt6.QtCore import QObject, Qt, QEvent
from PyQt6.QtWidgets import QMessageBox, QGraphicsScene

class EquationKeyHandler(QObject):
    """
    An event filter to handle key bindings within a QGraphicsScene
    Listens for the Delete key to remove selected equations
    """

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def eventFilter(self, obj, event):
        if isinstance(obj, QGraphicsScene):
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Delete:
                    self.handle_delete_key(obj)
                    return True
        return super().eventFilter(obj, event)

    def handle_delete_key(self, scene):
        selected_items = scene.selectedItems()
        if not selected_items:
            QMessageBox.information(self.main_window, "No Selection", "No equation is selected to delete.")
            return

        reply = QMessageBox.question(
            self.main_window,
            "Delete Equation",
            f"Are you sure you want to delete the selected {len(selected_items)} equation(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                if hasattr(item, 'answer_items'):
                    for answer_item in item.answer_items:
                        answer_scene = answer_item.scene()
                        if answer_scene is not None:
                            answer_scene.removeItem(answer_item)
                        answer_views = answer_scene.views()
                        if answer_views:
                            answer_page = answer_views[0]
                            if hasattr(answer_page, 'answer_items'):
                                if answer_item in answer_page.answer_items:
                                    answer_page.answer_items.remove(answer_item)
                            self.update_answer_positions(answer_page)
                scene.removeItem(item)
            QMessageBox.information(self.main_window, "Deleted", "Selected equation(s) and their answers have been deleted.")
        else:
            pass

    def update_answer_positions(self, answer_page):
        try:
            y_pos = 10
            for item in answer_page.answer_items:
                item.setPos(0, y_pos)
                y_pos += item.boundingRect().height() + 5
        except Exception as e:
            print(f"An error occurred in update_answer_positions: {e}")
