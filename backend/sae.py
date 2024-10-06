from PyQt6.QtWidgets import QMessageBox, QFileDialog, QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem, \
    QGraphicsLineItem
import json
from backend import qd
from backend.usertext import TextItem
import base64
from PyQt6.QtGui import QPixmap, QColor, QFont
from PyQt6.QtCore import QBuffer


def save_project_data(main_window, file_name):
    """Saves the project data to the specified file in JSON format."""
    try:
        # Get data from the main window
        data = get_project_data(main_window)
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)
        QMessageBox.information(main_window, "Success", "Project saved successfully.")
    except Exception as e:
        QMessageBox.critical(main_window, "Error Saving", f"An error occurred while saving the project: {e}")


def get_project_data(main_window):
    """Collects all data from the main window for saving."""
    data = {
        "questionPageCount": main_window.questionPageCount,
        "answerPageCount": main_window.answerPageCount,
        "intro": [],
        "questions": [],
        "answers": []
    }

    # Map items to unique IDs
    item_id_counter = 0
    # Maps items to IDs
    item_id_map = {}

    # Collect data from IntroPage
    try:
        intro_layout = main_window.scrollAreaTitlePageWidgetContents.layout()
        if intro_layout is not None and intro_layout.count() > 0:
            intro_page_widget = intro_layout.itemAt(0).widget()
            scene = intro_page_widget.scene()
            page_data = {
                "page_number": intro_page_widget.page_number,
                "items": []
            }
            for item in scene.items():
                item_id_counter += 1
                # Assign unique ID
                item_id_map[item] = item_id_counter
                parent = item.parentItem()
                # Get the parent ID if parent is in item_id_map
                parent_id = item_id_map.get(parent, None)
                item_data = {
                    "id": item_id_counter,
                    "parent_id": parent_id,
                }
                if isinstance(item, QGraphicsTextItem):
                    text = item.toPlainText()
                    position = (item.pos().x(), item.pos().y())
                    font_str = item.font().toString()
                    color_name = item.defaultTextColor().name()
                    item_data.update({
                        "type": "QGraphicsTextItem",
                        "text": text,
                        "position": position,
                        "font": font_str,
                        "color": color_name,
                    })
                    page_data["items"].append(item_data)
                elif isinstance(item, QGraphicsRectItem):
                    rect = item.rect()
                    position = (item.pos().x(), item.pos().y())
                    item_data.update({
                        "type": "QGraphicsRectItem",
                        "rect": (rect.x(), rect.y(), rect.width(), rect.height()),
                        "position": position,
                    })
                    page_data["items"].append(item_data)
                elif isinstance(item, QGraphicsLineItem):
                    line = item.line()
                    position = (item.pos().x(), item.pos().y())
                    item_data.update({
                        "type": "QGraphicsLineItem",
                        "line": (line.x1(), line.y1(), line.x2(), line.y2()),
                        "position": position,
                    })
                    page_data["items"].append(item_data)
                # Handle other item types
            data["intro"].append(page_data)
    except Exception as e:
        QMessageBox.critical(main_window, "Error Collecting Intro Page Data",
                             f"An error occurred while collecting intro page data: {e}")

    # Collect data from answer pages first to assign IDs to answer items
    try:
        answer_layout = main_window.scrollAreaAnswersWidgetContents.layout()
        if answer_layout is not None:
            for i in range(answer_layout.count()):
                answer_page_widget = answer_layout.itemAt(i).widget()
                scene = answer_page_widget.scene()
                page_data = {
                    "page_number": answer_page_widget.page_number,
                    "items": []
                }
                for item in scene.items():
                    item_id_counter += 1
                    item_id_map[item] = item_id_counter
                    if isinstance(item, qd.AnswerTextItem):
                        item_data = {
                            "id": item_id_counter,
                            "type": "AnswerTextItem",
                            "text": item.text,
                            "position": (item.pos().x(), item.pos().y()),
                        }
                        page_data["items"].append(item_data)
                    elif isinstance(item, qd.SeparatorItem):
                        item_data = {
                            "id": item_id_counter,
                            "type": "SeparatorItem",
                            "line": (item.line().x1(), item.line().y1(), item.line().x2(), item.line().y2()),
                            "position": (item.pos().x(), item.pos().y()),
                        }
                        page_data["items"].append(item_data)
                    elif isinstance(item, QGraphicsPixmapItem):
                        # Handle images (e.g. graphs)
                        # Convert the QPixmap to a base64 encoded string
                        buffer = QBuffer()
                        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                        item.pixmap().save(buffer, 'PNG')
                        encoded_pixmap = base64.b64encode(buffer.data().data()).decode('utf-8')
                        item_data = {
                            "id": item_id_counter,
                            "type": "PixmapItem",
                            "pixmap": encoded_pixmap,
                            "position": (item.pos().x(), item.pos().y()),
                        }
                        page_data["items"].append(item_data)
                    elif isinstance(item, TextItem):
                        # Handle TextItem
                        item_data = {
                            "id": item_id_counter,
                            "type": "TextItem",
                            "text": item.toPlainText(),
                            "position": (item.pos().x(), item.pos().y()),
                            "font": item.font().toString(),
                            "color": item.defaultTextColor().name()
                        }
                        page_data["items"].append(item_data)
                    elif isinstance(item, QGraphicsTextItem):
                        # Handle QGraphicsTextItem
                        text = item.toPlainText()
                        position = (item.pos().x(), item.pos().y())
                        font_str = item.font().toString()
                        color_name = item.defaultTextColor().name()
                        item_data = {
                            "id": item_id_counter,
                            "type": "QGraphicsTextItem",
                            "text": text,
                            "position": position,
                            "font": font_str,
                            "color": color_name,
                        }
                        page_data["items"].append(item_data)
                    # Handle other item
                data["answers"].append(page_data)
    except Exception as e:
        QMessageBox.critical(main_window, "Error Collecting Answer Data",
                             f"An error occurred while collecting answer data: {e}")

    # Collect data from question pages
    try:
        question_layout = main_window.scrollAreaQuestionWidgetContents.layout()
        if question_layout is not None:
            for i in range(question_layout.count()):
                question_page_widget = question_layout.itemAt(i).widget()
                scene = question_page_widget.scene()
                page_data = {
                    "page_number": question_page_widget.page_number,
                    "items": []
                }
                for item in scene.items():
                    item_id_counter += 1
                    # Assign unique ID
                    item_id_map[item] = item_id_counter
                    if isinstance(item, qd.EditableTextItem):
                        item_data = {
                            "id": item_id_counter,
                            "type": "EditableTextItem",
                            "equation_type": item.equation_type,
                            "text": item.text,
                            "difficulty": item.difficulty,
                            "position": (item.pos().x(), item.pos().y()),
                            # Save IDs of linked answer items
                            "answer_item_ids": [item_id_map[answer_item] for answer_item in item.answer_items if
                                                answer_item in item_id_map]
                        }
                        if isinstance(item.answer, QPixmap):
                            # Convert the QPixmap to a base64 encoded string
                            buffer = QBuffer()
                            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                            item.answer.save(buffer, 'PNG')
                            encoded_pixmap = base64.b64encode(buffer.data().data()).decode('utf-8')
                            item_data['answer'] = {'type': 'pixmap', 'data': encoded_pixmap}
                        else:
                            item_data['answer'] = item.answer
                        page_data["items"].append(item_data)
                    elif isinstance(item, TextItem):
                        # Handle TextItem
                        item_data = {
                            "id": item_id_counter,
                            "type": "TextItem",
                            "text": item.toPlainText(),
                            "position": (item.pos().x(), item.pos().y()),
                            "font": item.font().toString(),
                            "color": item.defaultTextColor().name()
                        }
                        page_data["items"].append(item_data)
                    elif isinstance(item, QGraphicsTextItem):
                        # Handle QGraphicsTextItem
                        text = item.toPlainText()
                        position = (item.pos().x(), item.pos().y())
                        font_str = item.font().toString()
                        color_name = item.defaultTextColor().name()
                        item_data = {
                            "id": item_id_counter,
                            "type": "QGraphicsTextItem",
                            "text": text,
                            "position": position,
                            "font": font_str,
                            "color": color_name,
                        }
                        page_data["items"].append(item_data)
                    # Handle other item types
                data["questions"].append(page_data)
    except Exception as e:
        QMessageBox.critical(main_window, "Error Collecting Question Data",
                             f"An error occurred while collecting question data: {e}")

    return data


def load_project_data(main_window, file_name):
    """Loads project data from the specified JSON formatted file."""
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)

        # Clear existing data
        main_window.questionPageCount = 0
        main_window.answerPageCount = 0

        # Remove existing intro page
        if main_window.scrollAreaTitlePageWidgetContents.layout() is not None:
            while main_window.scrollAreaTitlePageWidgetContents.layout().count() > 0:
                child = main_window.scrollAreaTitlePageWidgetContents.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Remove existing question pages
        if main_window.scrollAreaQuestionWidgetContents.layout() is not None:
            while main_window.scrollAreaQuestionWidgetContents.layout().count() > 0:
                child = main_window.scrollAreaQuestionWidgetContents.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Remove existing answer pages
        if main_window.scrollAreaAnswersWidgetContents.layout() is not None:
            while main_window.scrollAreaAnswersWidgetContents.layout().count() > 0:
                child = main_window.scrollAreaAnswersWidgetContents.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Set questionPageCount and answerPageCount
        main_window.questionPageCount = data.get("questionPageCount", 0)
        main_window.answerPageCount = data.get("answerPageCount", 0)

        # Map IDs to items
        id_item_map = {}

        # Load Intro Page
        try:
            intro_data = data.get("intro", [])
            if intro_data:
                page_data = intro_data[0]
                page_number = page_data.get("page_number", 0)
                # Create a new IntroPage
                main_window.create_page("Title", page_number=page_number)
                intro_page_widget = main_window.scrollAreaTitlePageWidgetContents.layout().itemAt(0).widget()
                scene = intro_page_widget.scene()
                # First pass: create items without setting parentItem
                for item_data in page_data.get("items", []):
                    item_id = item_data.get("id")
                    item_type = item_data.get("type")
                    if item_type == "QGraphicsTextItem":
                        text = item_data.get("text")
                        position = item_data.get("position", (0, 0))
                        font_str = item_data.get("font")
                        color_name = item_data.get("color")

                        item = QGraphicsTextItem(text)
                        item.setPos(*position)

                        # Restore font
                        if font_str:
                            font = QFont()
                            font.fromString(font_str)
                            item.setFont(font)

                        # Restore color
                        if color_name:
                            color = QColor(color_name)
                            item.setDefaultTextColor(color)

                        scene.addItem(item)
                        id_item_map[item_id] = item
                    elif item_type == "QGraphicsRectItem":
                        rect_params = item_data.get("rect", (0, 0, 0, 0))
                        position = item_data.get("position", (0, 0))

                        rect_item = QGraphicsRectItem(*rect_params)
                        rect_item.setPos(*position)
                        scene.addItem(rect_item)
                        id_item_map[item_id] = rect_item
                    elif item_type == "QGraphicsLineItem":
                        line_params = item_data.get("line", (0, 0, 0, 0))
                        position = item_data.get("position", (0, 0))

                        line_item = QGraphicsLineItem(*line_params)
                        line_item.setPos(*position)
                        scene.addItem(line_item)
                        id_item_map[item_id] = line_item
                    # Handle other item types
                # Second pass: set parent relationships
                for item_data in page_data.get("items", []):
                    item_id = item_data.get("id")
                    parent_id = item_data.get("parent_id")
                    if parent_id is not None:
                        item = id_item_map.get(item_id)
                        parent_item = id_item_map.get(parent_id)
                        if item is not None and parent_item is not None:
                            item.setParentItem(parent_item)
        except Exception as e:
            QMessageBox.critical(main_window, "Error Loading Intro Page Data",
                                 f"An error occurred while loading intro page data: {e}")

        # Load answer pages first to recreate answer items
        answer_scenes = []
        for page_data in data.get("answers", []):
            page_number = page_data.get("page_number")
            main_window.create_page("Answer", page_number=page_number)
            # Get the page widget by page_number
            answer_page_widget = None
            answer_layout = main_window.scrollAreaAnswersWidgetContents.layout()
            for i in range(answer_layout.count()):
                page = answer_layout.itemAt(i).widget()
                if page.page_number == page_number:
                    answer_page_widget = page
                    break
            if answer_page_widget is None:
                QMessageBox.warning(main_window, "Warning", f"Could not find answer page {page_number}")
                continue
            scene = answer_page_widget.scene()
            # Keep track of scenes
            answer_scenes.append(scene)
            # First pass: create items
            for item_data in page_data.get("items", []):
                item_id = item_data.get("id")
                item_type = item_data.get("type")
                if item_type == "AnswerTextItem":
                    text = item_data.get("text")
                    position = item_data.get("position", (0, 0))

                    # Create the AnswerTextItem
                    item = qd.AnswerTextItem()
                    item.set_plain_text(text)
                    item.setPos(*position)
                    scene.addItem(item)
                    # Map ID to item
                    id_item_map[item_id] = item
                elif item_type == "SeparatorItem":
                    position = item_data.get("position", (0, 0))
                    line = item_data.get("line", (0, 0, 0, 0))

                    # Create the SeparatorItem
                    item = qd.SeparatorItem()
                    item.setLine(*line)
                    item.setPos(*position)
                    scene.addItem(item)
                    # Map ID to item
                    id_item_map[item_id] = item
                elif item_type == "PixmapItem":
                    pixmap_data = item_data.get("pixmap")
                    position = item_data.get("position", (0, 0))

                    # Decode the pixmap
                    pixmap_bytes = base64.b64decode(pixmap_data)
                    pixmap = QPixmap()
                    pixmap.loadFromData(pixmap_bytes)

                    # Create the QGraphicsPixmapItem
                    item = QGraphicsPixmapItem(pixmap)
                    item.setPos(*position)
                    scene.addItem(item)
                    # Map ID to item
                    id_item_map[item_id] = item
                elif item_type == "TextItem":
                    text = item_data.get("text")
                    position = item_data.get("position", (0, 0))
                    font_str = item_data.get("font")
                    color_name = item_data.get("color")

                    # Create the TextItem
                    item = TextItem(text)
                    item.setPos(*position)

                    # Restore font
                    if font_str:
                        font = QFont()
                        font.fromString(font_str)
                        item.setFont(font)

                    # Restore color
                    if color_name:
                        color = QColor(color_name)
                        item.setDefaultTextColor(color)

                    scene.addItem(item)
                    # Map ID to item
                    id_item_map[item_id] = item
                elif item_type == "QGraphicsTextItem":
                    text = item_data.get("text")
                    position = item_data.get("position", (0, 0))
                    font_str = item_data.get("font")
                    color_name = item_data.get("color")

                    item = QGraphicsTextItem(text)
                    item.setPos(*position)

                    # Restore font
                    if font_str:
                        font = QFont()
                        font.fromString(font_str)
                        item.setFont(font)

                    # Restore color
                    if color_name:
                        color = QColor(color_name)
                        item.setDefaultTextColor(color)

                    scene.addItem(item)
                    id_item_map[item_id] = item

        # Load question pages
        for page_data in data.get("questions", []):
            page_number = page_data.get("page_number")
            main_window.create_page("Question", page_number=page_number)
            # Get the page widget by page_number
            question_page_widget = None
            question_layout = main_window.scrollAreaQuestionWidgetContents.layout()
            for i in range(question_layout.count()):
                page = question_layout.itemAt(i).widget()
                if page.page_number == page_number:
                    question_page_widget = page
                    break
            if question_page_widget is None:
                QMessageBox.warning(main_window, "Warning", f"Could not find question page {page_number}")
                continue
            scene = question_page_widget.scene()

            for item_data in page_data.get("items", []):
                item_id = item_data.get("id")
                item_type = item_data.get("type")
                if item_type == "EditableTextItem":
                    equation_type = item_data.get("equation_type")
                    difficulty = item_data.get("difficulty")
                    text = item_data.get("text")
                    position = item_data.get("position", (0, 0))
                    answer_data = item_data.get("answer")
                    answer_item_ids = item_data.get("answer_item_ids", [])

                    if isinstance(answer_data, dict) and answer_data.get("type") == "pixmap":
                        encoded_pixmap = answer_data.get("data")
                        pixmap_bytes = base64.b64decode(encoded_pixmap)
                        pixmap = QPixmap()
                        pixmap.loadFromData(pixmap_bytes)
                        answer = pixmap
                    else:
                        answer = answer_data

                    # Create the EditableTextItem
                    item = qd.EditableTextItem(equation_type, difficulty, answer)
                    item.set_plain_text(text)
                    item.setPos(*position)
                    scene.addItem(item)
                    # Map ID to item
                    id_item_map[item_id] = item

                    # Link the answer items
                    item.answer_items = [id_item_map[aid] for aid in answer_item_ids if aid in id_item_map]
                elif item_type == "TextItem":
                    text = item_data.get("text")
                    position = item_data.get("position", (0, 0))
                    font_str = item_data.get("font")
                    color_name = item_data.get("color")

                    # Create the TextItem
                    item = TextItem(text)
                    item.setPos(*position)

                    # Restore font
                    if font_str:
                        font = QFont()
                        font.fromString(font_str)
                        item.setFont(font)

                    # Restore color
                    if color_name:
                        color = QColor(color_name)
                        item.setDefaultTextColor(color)

                    scene.addItem(item)
                    # Map ID to item
                    id_item_map[item_id] = item
                elif item_type == "QGraphicsTextItem":
                    text = item_data.get("text")
                    position = item_data.get("position", (0, 0))
                    font_str = item_data.get("font")
                    color_name = item_data.get("color")

                    item = QGraphicsTextItem(text)
                    item.setPos(*position)

                    # Restore font
                    if font_str:
                        font = QFont()
                        font.fromString(font_str)
                        item.setFont(font)

                    # Restore color
                    if color_name:
                        color = QColor(color_name)
                        item.setDefaultTextColor(color)

                    scene.addItem(item)
                    id_item_map[item_id] = item

        # Select the first question page by default
        if main_window.scrollAreaQuestionWidgetContents.layout() and main_window.scrollAreaQuestionWidgetContents.layout().count() > 0:
            first_question_page = main_window.scrollAreaQuestionWidgetContents.layout().itemAt(0).widget()
            first_question_page.isSelected = True
            first_question_page.setStyleSheet("border: 2px solid blue")
            main_window.selectedPage = first_question_page

    except Exception as e:
        QMessageBox.critical(main_window, "Error Loading", f"An error occurred while loading the project: {e}")


def save_file(main_window):
    """Opens a file dialog for saving the project and calls save_project_data."""
    file_name, _ = QFileDialog.getSaveFileName(
        main_window,
        "Save Project",
        "",
        "Math Worksheet Projects (*.mwp);;All Files (*)"
    )
    if file_name:
        save_project_data(main_window, file_name)


def exit_application(main_window):
    """Saves the current project (if a file is open) and exits the application."""
    if main_window.current_save_file:
        try:
            save_project_data(main_window, main_window.current_save_file)
        except Exception as e:
            QMessageBox.critical(main_window, "Error Saving", f"An error occurred while saving the project: {e}")
    main_window.close()
