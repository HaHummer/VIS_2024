import vtk

class MouseEventTester:
    def __init__(self):
        self.render_window = vtk.vtkRenderWindow()
        self.renderer = vtk.vtkRenderer()
        self.render_window.AddRenderer(self.renderer)

        # Einfaches Objekt für die Szene
        sphere = vtk.vtkSphereSource()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)

        self.render_window_interactor = vtk.vtkRenderWindowInteractor()
        self.render_window_interactor.SetRenderWindow(self.render_window)

        # Maus-Event-Callback hinzufügen
        self.render_window_interactor.AddObserver("LeftButtonPressEvent", self.on_left_click)

    def on_left_click(self, caller, event):
        # Klickposition abrufen
        click_pos = caller.GetEventPosition()
        print(f"Mausklick: {click_pos}")

        # Fenstergröße prüfen
        width, height = self.render_window.GetSize()
        print(f"Fenstergröße: {width}x{height}")

        # Beispiel: Pixel aus dem Bild lesen
        window_to_image = vtk.vtkWindowToImageFilter()
        window_to_image.SetInput(self.render_window)
        window_to_image.ReadFrontBufferOn()
        window_to_image.Update()

        x, y = click_pos
        y = height - y - 1  # Y-Koordinate anpassen
        image = window_to_image.GetOutput()

        rgb = (
            int(image.GetScalarComponentAsDouble(x, y, 0, 0)),
            int(image.GetScalarComponentAsDouble(x, y, 0, 1)),
            int(image.GetScalarComponentAsDouble(x, y, 0, 2))
        )
        print(f"Klickposition RGB-Werte: {rgb}")

    def start(self):
        self.renderer.SetBackground(0.1, 0.1, 0.1)
        self.render_window.Render()
        self.render_window_interactor.Start()

        
if __name__ == "__main__":
    tester = MouseEventTester()
    tester.start()