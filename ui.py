from PySide6.QtWidgets import QDialog,QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QCursor
import pyqtgraph as pg
import numpy as np
import pandas as pd
import operations
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Viewer")
        self.tracks = []
        self.currentPage = 0
        self.totalPages = 0

        # Layouts
        mainLayout = QVBoxLayout()
        controlsLayout = QHBoxLayout()
        graphsLayout = QVBoxLayout()

        # Controls
        self.openButton = QPushButton("Open CSV")
        self.windowShowLabel = QLabel("Window:")
        self.windowSlider = QSlider(Qt.Horizontal)
        self.windowSlider.setMinimum(11)
        self.windowSlider.setMaximum(301)
        self.windowSlider.setValue(101)
        self.windowSlider.setTickInterval(2)
        self.windowLabel = QLabel("101")
        self.thresholdLabel = QLabel("Threshold:")
        self.thresholdInput = QLineEdit("0.10")
        self.thresholdInput.setValidator(QDoubleValidator(0.00, 9.99, 2))
        self.memoryShowLabel = QLabel("Memory:")
        self.memorySlider = QSlider(Qt.Horizontal)
        self.memorySlider.setMinimum(1)
        self.memorySlider.setMaximum(999)
        self.memorySlider.setValue(100)
        self.memoryLabel = QLabel("100")
        self.previewButton = QPushButton("Preview")
        self.saveButton = QPushButton("Save")
        self.tracksLabel = QLabel("Tracks: 0")

        # Graphs
        self.graphWidgets = []
        for _ in range(5):
            row = QHBoxLayout()
            for _ in range(4):
                graphWidget = pg.PlotWidget()
                row.addWidget(graphWidget)
                self.graphWidgets.append(graphWidget)
            graphsLayout.addLayout(row)

        # Pagination
        self.prevButton = QPushButton("Previous")
        self.nextButton = QPushButton("Next")
        self.pageLabel = QLabel("0 of 0")
        self.prevButton.setEnabled(False)
        self.nextButton.setEnabled(False)

        # Signals
        self.openButton.clicked.connect(self.openFile)
        self.windowSlider.valueChanged.connect(self.updateWindowLabel)
        self.memorySlider.valueChanged.connect(lambda value: self.memoryLabel.setText(str(value)))
        self.prevButton.clicked.connect(self.previousPage)
        self.nextButton.clicked.connect(self.nextPage)
        self.previewButton.clicked.connect(self.previewResults)
        self.saveButton.clicked.connect(self.saveData)
        
        self.memorySlider.valueChanged.connect(self.plotTracks)
        self.thresholdInput.textChanged.connect(self.plotTracks)
        self.windowSlider.valueChanged.connect(self.plotTracks)
        self.previewButton.clicked.connect(self.showPreviewModal)

        # Adding widgets to layout
        controlsLayout.addWidget(self.openButton)
        controlsLayout.addWidget(self.windowShowLabel)
        controlsLayout.addWidget(self.windowSlider)
        controlsLayout.addWidget(self.windowLabel)
        controlsLayout.addWidget(self.thresholdLabel)
        controlsLayout.addWidget(self.thresholdInput)
        controlsLayout.addWidget(self.memoryShowLabel)
        controlsLayout.addWidget(self.memorySlider)
        controlsLayout.addWidget(self.memoryLabel)
        controlsLayout.addWidget(self.previewButton)
        controlsLayout.addWidget(self.saveButton)
        controlsLayout.addWidget(self.tracksLabel)
        mainLayout.addLayout(controlsLayout)
        mainLayout.addLayout(graphsLayout)
        paginationLayout = QHBoxLayout()
        paginationLayout.addWidget(self.prevButton)
        paginationLayout.addWidget(self.pageLabel)
        paginationLayout.addWidget(self.nextButton)
        mainLayout.addLayout(paginationLayout)

        self.setLayout(mainLayout)

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if filename:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.tracks = operations.openFile(filename)
            QApplication.restoreOverrideCursor()
            self.totalPages = len(self.tracks) // 20 + (1 if len(self.tracks) % 20 > 0 else 0)
            self.currentPage = 1
            self.updatePagination()
            self.plotTracks()

    def updateWindowLabel(self, value):
        if value % 2 == 0:  # Ensure only odd values
            value += 1
            self.windowSlider.setValue(value)
        self.windowLabel.setText(str(value))

    def previousPage(self):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.plotTracks()

    def nextPage(self):
        if self.currentPage < self.totalPages:
            self.currentPage += 1
            self.plotTracks()
            
    def showPreviewModal(self):    
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview Plots")
        layout = QVBoxLayout()


        # Generate the dataset of all segments
        stats = []
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for time, intensity in self.tracks:
            segments = operations.create_steps(time, intensity, self.windowSlider.value(), float(self.thresholdInput.text()), self.memorySlider.value())
            stats.append(segments)
        QApplication.restoreOverrideCursor()

        # Create a 2x2 grid layout for the graphs
        topRow = QHBoxLayout()
        bottomRow = QHBoxLayout()

        # Generate 4 random step-like plots
        
        
        graphWidget = pg.PlotWidget()
        # Generate random data for demonstration
        dataset = [operations.count_steps(x) for x in stats]
        y,x = np.histogram(dataset, bins=range(0, max(dataset) + 1))        
        # Use stepMode=True for a step-like plot
        graphWidget.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,150))
        # Set X and Y labels
        graphWidget.setLabel('left', f'Count')
        graphWidget.setLabel('bottom', f'Number of active segments per track')
        topRow.addWidget(graphWidget)
        
        graphWidget = pg.PlotWidget()
        # Generate random data for demonstration
        dataset = []
        for x in stats:
            dataset += operations.intensity(x) 
        y,x = np.histogram(dataset, bins='auto')        
        # Use stepMode=True for a step-like plot
        graphWidget.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,150))
        # Set X and Y labels
        graphWidget.setLabel('left', f'Count')
        graphWidget.setLabel('bottom', f'Intensity')
        topRow.addWidget(graphWidget)
        
        graphWidget = pg.PlotWidget()
        # Generate random data for demonstration
        dataset = []
        for x in stats:
            dataset += operations.duration(x) 
        y,x = np.histogram(dataset, bins='auto')        
        # Use stepMode=True for a step-like plot
        graphWidget.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,150))
        # Set X and Y labels
        graphWidget.setLabel('left', f'Count')
        graphWidget.setLabel('bottom', f'Duration')
        bottomRow.addWidget(graphWidget)
        
        graphWidget = pg.PlotWidget()
        # Generate random data for demonstration
        dataset = []
        for x in stats:
            dataset += operations.intensity(x,True) 
        y,x = np.histogram(dataset, bins='auto')        
        # Use stepMode=True for a step-like plot
        graphWidget.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,150))
        # Set X and Y labels
        graphWidget.setLabel('left', f'Count')
        graphWidget.setLabel('bottom', f'Relative Intensity')
        bottomRow.addWidget(graphWidget)

        layout.addLayout(topRow)
        layout.addLayout(bottomRow)
        dialog.setLayout(layout)
        dialog.exec_()

    def updatePagination(self):
        self.pageLabel.setText(f"{self.currentPage} of {self.totalPages}")
        self.prevButton.setEnabled(self.currentPage > 1)
        self.nextButton.setEnabled(self.currentPage < self.totalPages)
        self.tracksLabel.setText(f"Tracks: {len(self.tracks)}")

    def saveData(self):
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", "Excel Files (*.xlsx)")
        if filename == '':
            return
        
        stats = []        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for time, intensity in self.tracks:
            segments = operations.create_steps(time, intensity, self.windowSlider.value(), float(self.thresholdInput.text()), self.memorySlider.value())
            stats.append(segments)
        QApplication.restoreOverrideCursor()

        dataset1 = [operations.count_steps(x) for x in stats]
        dataset2 = []
        for x in stats:
            dataset2 += operations.intensity(x) 
        dataset3 = []
        for x in stats:
            dataset3 += operations.duration(x) 
        dataset4 = []
        for x in stats:
            dataset4 += operations.intensity(x,True) 
        
        df1 = pd.DataFrame(dataset1,columns=['Count'])
        df2 = pd.DataFrame(dataset2,columns=['Intensity'])
        df3 = pd.DataFrame(dataset3,columns=['Duration'])
        df4 = pd.DataFrame(dataset4,columns=['Relative intensity'])

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df1.to_excel(writer, sheet_name='Number')
            df2.to_excel(writer, sheet_name='Intensity')
            df3.to_excel(writer, sheet_name='Duration')
            df4.to_excel(writer, sheet_name='Step Intensity')

    def plotTracks(self):
        if len(self.tracks) == 0:
            return
        self.updatePagination()
        start = (self.currentPage - 1) * 20
        end = start + 20
        for i, graphWidget in enumerate(self.graphWidgets):
            graphWidget.clear()
            if start + i < len(self.tracks):
                time, intensity = self.tracks[start + i]
                graphWidget.plot(time, intensity)
                segments = operations.create_steps(time, intensity, self.windowSlider.value(), float(self.thresholdInput.text()), self.memorySlider.value())
                for segment in segments:
                    color = 'g' if not segment[2] else 'r'
                    graphWidget.plot(segment[0], segment[1], pen=color)

    def previewResults(self):
        self.plotTracks()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())