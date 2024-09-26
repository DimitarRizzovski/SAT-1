from PyQt6.QtWidgets import QMessageBox, QFileDialog, QGraphicsScene
import json
import qd
import base64
from io import BytesIO
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QByteArray, QBuffer




def save_project_data(main_window, file_name):
    """Saves the data to the specified file."""
    try:
        data = get_project_data(main_window)  # Get data from the main window
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        QMessageBox.critical(main_window, "Error Saving", f"An error occurred while saving the project: {e}")


def get_project_data(main_window):
    """Collects all data for saving."""
    data = {
        "questionPageCount": main_window.questionPageCount,
        "answerPageCount": main_window.answerPageCount,
        "questions": [],
        "answers": []
    }

    # Collect data from question pages
    try:
        layout = main_window.scrollAreaQuestionWidgetContents.layout()
        if layout is not None:
            for i in range(layout.count()):
                question_page = layout.itemAt(i).widget()
                scene = question_page.scene()
                page_data = {
                    "items": []
                }
                for item in scene.items():
                    if isinstance(item, qd.EditableTextItem):
                        item_data = {
                            "type": "EditableTextItem",
                            "equation_type": item.equation_type,
                            "text": item.text,
                            "difficulty": item.difficulty,
                            "position": (item.pos().x(), item.pos().y())
                        }
                        if isinstance(item.answer, QPixmap):
                            # Convert the image to text
                            buffer = QBuffer()
                            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                            item.answer.save(buffer, 'PNG')
                            encoded_pixmap = base64.b64encode(buffer.data().data()).decode('utf-8')
                            item_data['answer'] = {'type': 'pixmap', 'data': encoded_pixmap}
                        else:
                            item_data['answer'] = item.answer
                        page_data["items"].append(item_data)
                data["questions"].append(page_data)
    except Exception as e:
        QMessageBox.critical(main_window, "Error Collecting Question Data", f"An error occurred: {e}")
    # Similar logic for answers

    return data





def load_project_data(main_window, file_name):
    """Loads project data from the specified file."""
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)

        # Clear existing data
        main_window.questionPageCount = 0
        main_window.answerPageCount = 0

        # Remove existing pages
        if main_window.scrollAreaQuestionWidgetContents.layout() is not None:
            while main_window.scrollAreaQuestionWidgetContents.layout().count() > 0:
                child = main_window.scrollAreaQuestionWidgetContents.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        if main_window.scrollAreaAnswersWidgetContents.layout() is not None:
            while main_window.scrollAreaAnswersWidgetContents.layout().count() > 0:
                child = main_window.scrollAreaAnswersWidgetContents.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Load questions
        for i, page_data in enumerate(data["questions"]):
            # Create a new scene
            scene = QGraphicsScene()
            page_number = i + 1  # Page numbers start from 1
            main_window.questionPageCount += 1
            # Create a new page with the scene
            main_window.create_page(scene, main_window.scrollAreaQuestionWidgetContents, page_number, "Question")
            # Add items to the scene
            for item_data in page_data["items"]:
                if item_data["type"] == "EditableTextItem":
                    # Decode image data
                    if isinstance(item_data['answer'], dict) and item_data['answer']['type'] == 'pixmap':
                        encoded_pixmap = item_data['answer']['data']
                        pixmap_data = base64.b64decode(encoded_pixmap)
                        pixmap = QPixmap()
                        pixmap.loadFromData(pixmap_data)
                        answer = pixmap
                    else:
                        answer = item_data['answer']
                    item = qd.EditableTextItem(item_data["equation_type"], item_data["difficulty"], answer)
                    item.setPlainText(item_data["text"])
                    item.setPos(*item_data["position"])
                    scene.addItem(item)

        # Load answers
        for i, page_data in enumerate(data.get("answers", [])):
            scene = QGraphicsScene()
            page_number = i + 1
            main_window.answerPageCount += 1
            main_window.create_page(scene, main_window.scrollAreaAnswersWidgetContents, page_number, "Answer")
            # Similar logic for adding answer items

        # Select the top page in the question tab
        if main_window.scrollAreaQuestionWidgetContents.layout() is not None and main_window.scrollAreaQuestionWidgetContents.layout().count() > 0:
            top_page = main_window.scrollAreaQuestionWidgetContents.layout().itemAt(0).widget()
            top_page.isSelected = True
            top_page.setStyleSheet("border: 2px solid blue")
            main_window.selectedPage = top_page

    except Exception as e:
        QMessageBox.critical(main_window, "Error Loading", f"An error occurred while loading the project: {e}")



def save_file(main_window):
    """Opens a file dialog for saving the project and calls save_project_data."""
    file_name, _ = QFileDialog.getSaveFileName(
        main_window,
        "Save Project",
        "",
        "JSON Files (*.json)"
    )
    if file_name:
        save_project_data(main_window, file_name)


def exit_application(main_window):
    """Saves the current project (if a file is open) and exits the application."""
    if main_window.current_save_file:
        try:
            save_project_data(main_window, main_window.current_save_file)
        except Exception as e:
            print(f"Error saving project: {e}")
    main_window.close()
