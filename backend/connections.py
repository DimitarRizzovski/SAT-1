from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QPushButton, QLineEdit, QListWidget, QSpinBox
)

def setup_ui_elements(main_window):
    """
    Finds and initialises UI elements for the main_window.
    """
    main_window.scrollAreaTitlePageWidgetContents = main_window.findChild(QWidget, 'scrollAreaTitlePageWidgetContents')
    main_window.scrollAreaQuestionWidgetContents = main_window.findChild(QWidget, 'scrollAreaQuestionWidgetContents')
    main_window.scrollAreaAnswersWidgetContents = main_window.findChild(QWidget, 'scrollAreaAnswersWidgetContents')
    main_window.tabWidget = main_window.findChild(QTabWidget, 'tabWidget')

    main_window.addPage = main_window.findChild(QPushButton, 'addPage')
    main_window.deletePage = main_window.findChild(QPushButton, 'deletePage')
    main_window.searchMathEquations = main_window.findChild(QLineEdit, 'searchMathEquations')
    main_window.mathQuestions = main_window.findChild(QListWidget, 'mathQuestions')

    main_window.boldButton = main_window.findChild(QPushButton, 'boldButton')
    main_window.italicButton = main_window.findChild(QPushButton, 'italicButton')
    main_window.underlineButton = main_window.findChild(QPushButton, 'underlineButton')
    main_window.fontsizeBox = main_window.findChild(QSpinBox, 'fontsizeBox')

    main_window.actionPDF = main_window.findChild(QAction, 'actionPDF')
    main_window.actionSave = main_window.findChild(QAction, 'actionSave')
    main_window.actionSave_As = main_window.findChild(QAction, 'actionSave_As')
    main_window.actionOpen = main_window.findChild(QAction, 'actionOpen_2')
    main_window.actionExit = main_window.findChild(QAction, 'actionExit')

def setup_connections(main_window):
    """
    Connects UI elements to their respective event handlers.
    """
    main_window.tabWidget.currentChanged.connect(main_window.on_tab_changed)
    main_window.actionPDF.triggered.connect(main_window.save_pdf)
    main_window.addPage.clicked.connect(main_window.add_question_page)
    main_window.deletePage.clicked.connect(main_window.delete_page)
    main_window.searchMathEquations.textChanged.connect(main_window.search_equations)
    main_window.mathQuestions.itemDoubleClicked.connect(main_window.add_equation)
    main_window.actionSave.triggered.connect(main_window.save_project)
    main_window.actionSave_As.triggered.connect(main_window.save_project_as)
    main_window.actionOpen.triggered.connect(main_window.open_project)
    main_window.actionExit.triggered.connect(main_window.exit_application)

    main_window.boldButton.clicked.connect(main_window.apply_bold)
    main_window.italicButton.clicked.connect(main_window.apply_italic)
    main_window.underlineButton.clicked.connect(main_window.apply_underline)
    main_window.fontsizeBox.valueChanged.connect(main_window.apply_font_size)
