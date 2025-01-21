#import sys
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget, QStatusBar, QMenu, QColorDialog,
    QDialog, QLabel, QListWidget, QPushButton, QTreeWidget, QTreeWidgetItem # zusatz für Egenschaften
)
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog
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

        # Standard-Theme setzen (dunkel standard)
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

        # Farbschema Menü-----------------------------------------------------------------
        theme_menu = QMenu("Theme", self) #Name Theme > ModiWechsel auf deutsch nd so schön
        menu_bar.addMenu(theme_menu)

        light_theme_action = QAction("Hell", self)
        light_theme_action.triggered.connect(self.set_light_theme)
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dunkel", self)
        dark_theme_action.triggered.connect(self.set_dark_theme)
        theme_menu.addAction(dark_theme_action)

        custom_color_action = QAction("Benutzerdefinierter Hintergrund", self)# benutzerdefinierte Farbe
        custom_color_action.triggered.connect(self.select_custom_color)
        theme_menu.addAction(custom_color_action)

        #Screenshot von Modell Menü-------------------------------------------------------
        screenshot_action = QAction("Bildschirmfoto", self)
        screenshot_action.triggered.connect(self.take_screenshot)
        file_menu.addAction(screenshot_action)

        #Ansicht----------------------------------------------------
        # Ansicht Menü---------------------------------------------------------------
        view_menu = menu_bar.addMenu("Ansicht")

        view_x_action = QAction("X-Achse", self)
        view_x_action.triggered.connect(self.set_view_x)
        view_menu.addAction(view_x_action)

        view_y_action = QAction("Y-Achse", self)
        view_y_action.triggered.connect(self.set_view_y)
        view_menu.addAction(view_y_action)

        view_z_action = QAction("Z-Achse", self)
        view_z_action.triggered.connect(self.set_view_z)
        view_menu.addAction(view_z_action)

        # Aktion "Exit" zum Beenden der Anwendung
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

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

                # Modell an VTKRenderWidget übergeben
                self.vtk_widget.model = self.model # sonst wird nach Eigenschaften nix angezeigt

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

    # Hintergrundfarben-------------------------------------------------------------------------
    def set_light_theme(self):
        self.vtk_widget.set_background_color((1.0, 1.0, 1.0))  # Weißer Hintergrund
        self.apply_stylesheet("light") # auch ändern am Fenster
        self.update_status("Set theme: Light")

    def set_dark_theme(self):
        self.vtk_widget.set_background_color((0.1, 0.1, 0.1))  # Dunkler Hintergrund
        self.apply_stylesheet("dark") # auch ändern am Fenster
        self.update_status("Set theme: Dark")

    def select_custom_color(self):        #Öffnet Farbauswahldialog + setzen der gewählten Farbe als Hintergrund

        color = QColorDialog.getColor()  # Zeigt die Farbpalette an
        if color.isValid():  # Überprüft, ob  gültige Farbe gewählt
            # RGB-Werte für VTK (normiert zwischen 0 und 1) für innen
            rgb = (color.redF(), color.greenF(), color.blueF())  # Erhalte RGB als Tupel
            self.vtk_widget.set_background_color(rgb)  # Setzt die Hintergrundfarbe im VTK-Renderer
        
            # Hexadezimalwert für die GUI für den äußeren Rand
            hex_color = color.name()  # Erhalte Hex-Wert (z. B. #RRGGBB)
            self.setStyleSheet(f"QMainWindow {{background-color: {hex_color};}}")  # GUI-Hintergrund ändern

        self.update_status(f"Custom color set: {hex_color}")

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

    #Screenshot----------------------------------------
    def take_screenshot(self):     #Ruft die Screenshot-Funktion des VTKRenderWidgets auf und speichert die Datei.
        
        # Datei-Dialog öffnen, um den Speicherort festzulegen
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save VTK Screenshot", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        if not file_path:
            return

        # Screenshot des VTK-Renderers aufnehmen und speichern
        self.vtk_widget.save_screenshot(file_path) #verbindung zu vtkRenderWidget
        self.status_bar.showMessage(f"VTK Screenshot saved to {file_path}")
    
    #Ansicht------------------------------------------------------------------------------------------------
    def set_view_x(self):
        self.vtk_widget.set_camera_view('x')

    def set_view_y(self):
        self.vtk_widget.set_camera_view('y')

    def set_view_z(self):
        self.vtk_widget.set_camera_view('z')


class VTKRenderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.vtk_widget = QVTKRenderWindowInteractor(self) #erstellen VTK widget
        self.layout.addWidget(self.vtk_widget) #zum layout hinzufügen

        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        self._add_orientation_axes()

        self.vtk_widget.GetRenderWindow().Render()
        self.vtk_widget.Start()

        # Binde Maus-Events an das Hauptfenster
        self.vtk_widget.GetRenderWindow().GetInteractor().AddObserver("LeftButtonPressEvent", self._on_left_click)

        # Rechtsklick ermöglichen für Eigenschaftsfenster (nur bei fdd Files)
        self.vtk_widget.GetRenderWindow().GetInteractor().AddObserver("RightButtonPressEvent", self._show_context_menu)

    def load_model(self, file_name):
        # Debug-Ausgabe, um zu prüfen, ob die Datei geladen wird
        print(f"Lade Modell aus Datei: {file_name}")

        # Modell aus Datei laden
        reader = vtk.vtkOBJReader()
        reader.SetFileName(file_name) #Dateiname setzen
        reader.Update() # laden der Datei

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

    #Screenshot-------------------------------------------------------------------------------------------------------------------
    def save_screenshot(self, file_path: str): #Speichert Screenshot nur von VTK-Renderer
        
        # VTK Screenshot
        render_window = self.vtk_widget.GetRenderWindow()
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(render_window)
        window_to_image.Update()

        # Bild in Datei schreiben
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(file_path)
        writer.SetInputConnection(window_to_image.GetOutputPort())
        writer.Write()

    # absolutes Koordinatensystem in Ecke-------------------------------------------------------------------------------------------
    def _add_orientation_axes(self): #Fügt ein Koordinatensystem in der rechten unteren Ecke hinzu
        axes = vtk.vtkAxesActor()

        axes.SetTotalLength(2.0, 2.0, 2.0)  # Achsenlängen auf das Doppelte setzen versuch achsen besser zu trefen funktioniert nicht
        axes.SetShaftTypeToCylinder()       # Achsen als Zylinder darstellen
        axes.SetCylinderRadius(0.1)        # Radius der Zylinderachsen
        axes.SetConeRadius(0.5)            # Radius der Achsenspitzen

        self.orientation_widget = vtk.vtkOrientationMarkerWidget()
        self.orientation_widget.SetOrientationMarker(axes)
        self.orientation_widget.SetInteractor(self.vtk_widget.GetRenderWindow().GetInteractor())

        # Position in der rechten unteren Ecke fixieren
        self.orientation_widget.SetViewport(0.8, 0.0, 1.0, 0.3)  # Normalisierte Koordinaten (x_min, y_min, x_max, y_max)
        self.orientation_widget.SetEnabled(1)
        self.orientation_widget.InteractiveOff()

    # Ansicht------------------------------------------------------

    def set_camera_view(self, axis):
        camera = self.renderer.GetActiveCamera()
        if axis == 'x':
            camera.SetPosition(10, 0, 0)  # Blick entlang der X-Achse
            camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
            camera.SetViewUp(0, 0, 1)  # Z-Achse zeigt nach oben
        elif axis == 'y':
            camera.SetPosition(0, 10, 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
        elif axis == 'z':
            camera.SetPosition(0, 0, 10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 1, 0)
        
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    # Versuch einer weiteren Achsenausrichtung------------------------------------------------------------------
    def _on_left_click(self, caller, event): #richtet die Kamera basierend auf der Farbe der Koordinatenachsen aus
        click_pos = caller.GetEventPosition()
        print(f"Mausklick: {click_pos}")

        # zugriff aug RenderWindow
        render_window = self.vtk_widget.GetRenderWindow()
        width, height = render_window.GetSize()
        print(f"Fenstergröße: {width}x{height}")

        #für späteres minimieren der Klickpositionen
            # Berechnung des Viewports reduzierung auf unteres Fenster 
        #x_min, y_min = int(0.8 * window_width), 0
        #x_max, y_max = window_width, int(0.2 * window_height)

            # Prüfen, ob der Klick innerhalb des Viewports liegt
        #if not (x_min <= click_pos[0] <= x_max and y_min <= click_pos[1] <= y_max):
            #print("Klick außerhalb des Achsensystems")
            #return

        # Offscreen-Rendering für die Farben
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(render_window)
        window_to_image.ReadFrontBufferOn()
        window_to_image.Update()

        x, y = click_pos
        y = height - y - 1  # Y-Achse invertieren
        image = window_to_image.GetOutput()

        pixel = (
            int(image.GetScalarComponentAsDouble(x, y, 0, 0)),
            int(image.GetScalarComponentAsDouble(x, y, 0, 1)),
            int(image.GetScalarComponentAsDouble(x, y, 0, 2))
        )
        print(f"Klickposition RGB-Werte: {pixel}")

        # Funktion zur Farbprüfung mit Toleranz
        def is_close_to_color(color, target, tolerance=150):
            return all(abs(c - t) <= tolerance for c, t in zip(color, target))

        # Kamera basierend auf der Farbe ausrichten
        camera = self.renderer.GetActiveCamera()
        if is_close_to_color(pixel, (255, 0, 0)):  # X-Achse (Rot)
            print("X-Achse ausgewählt")
            camera.SetPosition(10, 0, 0)  # Blick entlang der X-Achse
            camera.SetFocalPoint(0, 0, 0)  # Fokus auf den Ursprung
            camera.SetViewUp(0, 0, 1)  # Z-Achse zeigt nach oben
        elif is_close_to_color(pixel, (0, 255, 0)):  # Y-Achse (Grün)
            print("Y-Achse ausgewählt")
            camera.SetPosition(0, 10, 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
        elif is_close_to_color(pixel, (0, 0, 255)):  # Z-Achse (Blau)
            print("Z-Achse ausgewählt")
            camera.SetPosition(0, 0, 10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 1, 0)
        else:
            print("Keine gültige Achse ausgewählt")

        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    # Anzeigen der Eigenschaften (nur bei fdd Files)

    def _show_context_menu(self, caller, event):                            #caller,event: funktioniert als Callback caller: was ausgelöst, event: Ereigniss
        # Deaktivieren von Interaktor um zoomen zu unterbinden (nd so schön)
        self.vtk_widget.GetRenderWindow().GetInteractor().Disable()

        menu = QMenu(self)
        show_props_action = menu.addAction("Eigenschaften anzeigen")
        show_props_action.triggered.connect(self._show_properties_dialog)
        menu.exec_(self.mapToGlobal(self.vtk_widget.mapFromGlobal(QCursor.pos())))

        # wieder aktivieren
        self.vtk_widget.GetRenderWindow().GetInteractor().Enable()

    def _show_properties_dialog(self):
        # Sicherstellen, dass ein Modell geladen ist
        if hasattr(self, "model") and hasattr(self.model, "get_mbsObjectList"):# überprüfen gibt es Methode
            dialog = PropertiesDialog(self.model.get_mbsObjectList()) # "Getter" aufrufen
            dialog.exec_()



class PropertiesDialog(QDialog):
    def __init__(self, mbs_objects):
        super().__init__()
        self.setWindowTitle("Eigenschaften") #fenstertitel

        layout = QVBoxLayout() #hauptlayout

        # Liste der Objekte
        self.object_list = QListWidget() # Widget zur Anzeige der Objektliste
        for obj in mbs_objects:
            self.object_list.addItem(obj.getType() + " - " + obj.getSubType())
        layout.addWidget(self.object_list)

        # Eigenschaften-Anzeige als Tree
        self.properties_tree = QTreeWidget()
        self.properties_tree.setHeaderLabels(["Eigenschaft", "Typ", "Wert"]) #kopfzeile setzen
        layout.addWidget(self.properties_tree) #tree zum layout

        # Event bei Auswahl eines Objekts
        self.object_list.currentRowChanged.connect(self._update_properties)

        # Schließen-Button
        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout) # Layout dem Dialog zuweisen
        self.mbs_objects = mbs_objects # Liste der Objekte speichern

    def _update_properties(self, index):
        if index >= 0:
            selected_object = self.mbs_objects[index]
            properties = selected_object.inspect_object() #eigenschaften abrufen

            # Tree aktualisieren
            self.properties_tree.clear()
            root_item = QTreeWidgetItem([properties["type"], "", ""]) #hauptknoten erstellen
            self.properties_tree.addTopLevelItem(root_item) #hauptknoten hinzufügen

            # Parameter als untergeordnete Items hinzufügen
            for key, details in properties["parameters"].items():
                param_item = QTreeWidgetItem(
                    [key, details["type"], str(details["value"])] # Schlüssel, Typ und Wert hinzufügen
                )
                root_item.addChild(param_item)

            self.properties_tree.expandAll()