#import sys
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QStatusBar, QMenu
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from mbsModel import mbsModel
from inputfilereader import readInput  # pfadindifferenzen mit weiter äußerem inputfilereader! -> umbenennung zu inputfilereader__



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visualisierungsfenster") # Titel von Fenster
        self.setGeometry(100, 100, 1024, 768) #Fenstergröße und Pos

        # Menüleiste erstellen
        self.create_menu_bar()

        # Statusleiste hinzufügen
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar) # setzen der Statusleiste
        self.update_status("No model loaded")

        # VTK RenderWindow
        self.vtk_widget = VTKRenderWidget()
        self.setCentralWidget(self.vtk_widget) # setzen als zentrales Widget

        # Modellinstanz
        self.model = mbsModel()

        # Standard-Theme setzen (dunkel standarf)
        self.set_dark_theme()        

    def create_menu_bar(self):
        #erstellen der Menüleiste
        menu_bar = self.menuBar()

        # File Menü-------------------------------------------------------------------
        file_menu = menu_bar.addMenu("File") # erstellen von "File"-Menü

        # Aktion "Load" für das Laden von Modellen
        load_action = QAction("Load Model", self)
        load_action.triggered.connect(self.load_model)
        file_menu.addAction(load_action)

        # Aktion "Import Fdd" für den Import von Fdd-Dateien
        import_action = QAction("Import Fdd", self)
        import_action.triggered.connect(self.import_fdd)
        file_menu.addAction(import_action)

        # JSON Datei laden
        load_json_action = QAction("Load from JSON", self)
        load_json_action.triggered.connect(self.load_JSON)
        file_menu.addAction(load_json_action)

        # Save
        import_action = QAction("Save", self)
        import_action.triggered.connect(self.saveGeometry)
        file_menu.addAction(import_action)

        # Aktion "Exit" zum Beenden der Anwendung
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Farbschema Menü-----------------------------------------------------------------
        theme_menu = QMenu("Theme", self) #Name Theme > ModiWechsel auf deutsch nd so schön
        menu_bar.addMenu(theme_menu)

        light_theme_action = QAction("Hell", self)
        light_theme_action.triggered.connect(self.set_light_theme)
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dunkel", self)
        dark_theme_action.triggered.connect(self.set_dark_theme)
        theme_menu.addAction(dark_theme_action)

    def load_model(self):
        #öffnet DateiDialog um Nodell zu laden
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Model", "", "Model Files (*.vtk *.stl *.obj);;All Files (*)")
        if file_name:
            self.update_status(f"Loaded model: {file_name}")
            self.vtk_widget.load_model(file_name)

    def import_fdd(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Fdd File", "", "Fdd Files (*.fdd);;All Files (*)")
        if file_name:
            try:
                # Lese die Fdd-Datei mit inputfilereader
                mbs_objects = readInput(file_name)
                self.model = mbsModel()
                self.model.load_objects(mbs_objects)  # Neue Methode im mbsModel

                # Visualisiere das Modell im Renderer
                self.vtk_widget.render_model(self.model)
                # Kamera auf das Modell ausrichten
                self.vtk_widget.renderer.ResetCamera() # kamera reseten um nicht zu weit im modell zu sein, funktioniert jedoch nicht
                self.vtk_widget.vtk_widget.GetRenderWindow().Render() #2mal vtk_widget da außerhalb

                self.update_status(f"Loaded Fdd file: {file_name}")
            except Exception as e:
                self.update_status(f"Error loading Fdd file: {e}")
                print(e)

    def load_JSON(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Model from JSON", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            try:
                # JSON-Daten ins Modell laden
                self.model = mbsModel()
                self.model.loadDatabase(file_name)

                # Modell visualisieren
                self.vtk_widget.render_model(self.model)
                self.vtk_widget.renderer.ResetCamera()
                self.vtk_widget.vtk_widget.GetRenderWindow().Render()

                self.update_status(f"Model loaded from: {file_name}")
            except Exception as e:
                self.update_status(f"Error loading model: {e}")
                print(e)

    def saveGeometry(self):
        # Öffnen Dialog zum Speichern der Datei
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Model", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            try:
                # Modell speichern
                self.model.saveDatabase(file_name)
                self.update_status(f"Model saved to: {file_name}")
            except Exception as e:
                self.update_status(f"Error saving model: {e}")
                print(e)

    def update_status(self, message):
        self.status_bar.showMessage(message)

    #hintergrundfarben
    def set_light_theme(self):
        self.vtk_widget.set_background_color((1.0, 1.0, 1.0))  # Weißer Hintergrund
        self.apply_stylesheet("light") # auch ändern am Fenster
        self.update_status("Set theme: Light")

    def set_dark_theme(self):
        self.vtk_widget.set_background_color((0.1, 0.1, 0.1))  # Dunkler Hintergrund
        self.apply_stylesheet("dark") # auch ändern am Fenster
        self.update_status("Set theme: Dark")

    def apply_stylesheet(self, theme):
        if theme == "light":
            # Stylesheet für hell lt. Internet
            stylesheet = """
                QMainWindow {background-color: #ffffff; color: #000000;}
                QMenuBar {background-color: #f0f0f0; color: #000000;}
                QMenu {background-color: #f0f0f0; color: #000000;}
                QStatusBar {background-color: #e0e0e0; color: #000000;}
                QPushButton {background-color: #e0e0e0; color: #000000; border: 1px solid #c0c0c0;}
                QPushButton:hover {background-color: #d6d6d6;}
            """
        if theme == "dark":
            # Stylesheet dunkel
            stylesheet = """
                QMainWindow {background-color: #2e2e2e; color: #ffffff;}
                QMenuBar {background-color: #3c3c3c; color: #ffffff;}
                QMenu {background-color: #3c3c3c; color: #ffffff;}
                QStatusBar {background-color: #2e2e2e; color: #ffffff;}
                QPushButton {background-color: #444444; color: #ffffff; border: 1px solid #5e5e5e;}
                QPushButton:hover {background-color: #555555;}
            """
        # Anwenden des Stylesheets
        self.setStyleSheet(stylesheet)

class VTKRenderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.vtk_widget = QVTKRenderWindowInteractor(self) #erstellen VTK widget
        self.layout.addWidget(self.vtk_widget) #zum layout hinzufügen

        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        self.vtk_widget.GetRenderWindow().Render()
        self.vtk_widget.Start()

    def load_model(self, file_name):
        # Debug-Ausgabe, um zu prüfen, ob die Datei geladen wird
        print(f"Lade Modell aus Datei: {file_name}")

        # Modell aus Datei laden
        reader = vtk.vtkOBJReader()
        reader.SetFileName(file_name) #Dateiname setzen
        reader.Update() # laden der Datei

        # Prüfen, ob Punkte im Modell vorhanden sind funktioniert no nd!!!!!
        output = reader.GetOutput()
        if output.GetNumberOfPoints() == 0:
            print("Fehler: .obj Datei enthält keine Punkte. Datei prüfen!")
            return

        #mappen der Geometry zu einem Aktor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort()) # verbinden von mapper und reader

        actor = vtk.vtkActor()
        actor.SetMapper(mapper) # verbinden actor mit mapper


        self.renderer.RemoveAllViewProps() #entfernen vorheriger Objekte
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()  # Kamera auf das Modell ausrichten## wichtig damit fenster nicht weiß
        # Rendern
        self.vtk_widget.GetRenderWindow().Render()

    def render_model(self, model: mbsModel):
        # Fügt alle Akteure des Modells zum Renderer hinzu
        self.renderer.RemoveAllViewProps()

        model.showModel(self.renderer)## visualisiere neues Modell
         # Kamera neu ausrichten um zoom problem zu beheben
        self.renderer.ResetCamera()

        self.vtk_widget.GetRenderWindow().Render()

    #Hintergrundstil
    def set_background_color(self, color):
        self.renderer.SetBackground(color) # farbe ändern
        self.vtk_widget.GetRenderWindow().Render() #aktualisieren