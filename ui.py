from PySide6.QtWidgets import QDialog,QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit, QFileDialog, QComboBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator, QCursor
import pyqtgraph as pg
import numpy as np
import pandas as pd
import operations
import sys

class FloatInput(QLineEdit):
    value_changed = Signal(float)  # Define the signal

    def __init__(self, default_value=0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_color = self.palette().color(self.foregroundRole())
        self.textChanged.connect(self.on_text_changed)
        self.editingFinished.connect(self.on_editing_finished)
        self.set_default_value(default_value)

    def set_default_value(self, value):
        if self.is_valid(value):
            self.setText(f"{value:.2f}")
            self.setStyleSheet(f"color: {self.original_color.name()};")
        else:
            self.setText("0.00")
            self.setStyleSheet("color: red;")

    def on_text_changed(self):
        self.setStyleSheet("color: red;")

    def on_editing_finished(self):
        self.setStyleSheet(f"color: {self.original_color.name()};")
        try:
            value = float(self.text())
            if self.is_valid(value):
                self.setStyleSheet(f"color: {self.original_color.name()};")
                self.value_changed.emit(value)  # Emit the signal
            else:
                self.setStyleSheet("color: red;")  # Keeps the color red if input is invalid
        except ValueError:
            self.setStyleSheet("color: red;")  # Keeps the color red if input is invalid

    def is_valid(self, value):
        return 0.00 <= value <= 0.99

PAR_names = ['Chambolle weight','Corner window','P_Height','P_distance','Steps']
PAR_defaults = [12,100,8,41,0]
PAR_ranges = [[1,1000],[1,1000],[1,100],[1,500],[0,50]]
PAR_values = PAR_defaults.copy()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Viewer")
        self.tracks = []
        self.ftracks = []
        self.redtracks = []
        self.currentPage = 0
        self.totalPages = 0
        self.selected = 0
        self.WAIT = True

        # Layouts
        mainLayout = QVBoxLayout()
        controlsLayout = QHBoxLayout()
        graphsLayout = QVBoxLayout()

        # Controls        
        self.openButton = QPushButton("Open CSV")
        self.combo_box = QComboBox()
        self.combo_box.addItems(PAR_names)  # Populate combo box with items from PAR_names
        #self.sliderShowLabel = QLabel(PAR_names[0])
        self.Slider = QSlider(Qt.Horizontal)
        self.Slider.setMinimum(PAR_ranges[0][0])
        self.Slider.setMaximum(PAR_ranges[0][1])
        self.Slider.setValue(PAR_defaults[0])
        self.sliderLabel = QLabel(str(PAR_defaults[0]))                
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
        self.combo_box.currentTextChanged.connect(self.on_selection_change)  # Set callback
        self.Slider.valueChanged.connect(self.updateSliderLabel)
        self.openButton.clicked.connect(self.openFile)
        self.prevButton.clicked.connect(self.previousPage)
        self.nextButton.clicked.connect(self.nextPage)
        self.previewButton.clicked.connect(self.previewResults)
        self.saveButton.clicked.connect(self.saveData)
        self.previewButton.clicked.connect(self.showPreviewModal)

        # Adding widgets to layout
        controlsLayout.addWidget(self.openButton)
        controlsLayout.addWidget(self.combo_box)
        controlsLayout.addWidget(self.Slider)
        controlsLayout.addWidget(self.sliderLabel)                
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
        
        self.WAIT = False
        
    def on_selection_change(self,text_selected):
        if self.WAIT is False:
            self.WAIT = True
            for i in range(len(PAR_names)):
                if PAR_names[i] == text_selected:
                    self.selected = i
                    break
            self.Slider.setMinimum(PAR_ranges[self.selected][0])
            self.Slider.setMaximum(PAR_ranges[self.selected][1])
            self.Slider.setValue(PAR_values[self.selected])
            self.sliderLabel.setText(str(PAR_values[self.selected]))
            if self.selected == 0:
                self.ftracks=[]
                self.redtracks=[]
            elif self.selected<2:
                self.redtracks=[]
            self.WAIT = False
            self.plotTracks()

    def openFile(self):
        self.WAIT = True
        filename, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if filename:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.tracks = operations.openFile(filename)
            QApplication.restoreOverrideCursor()
            self.totalPages = len(self.tracks) // 20 + (1 if len(self.tracks) % 20 > 0 else 0)
            self.currentPage = 1
            self.updatePagination()
            self.WAIT = False
            self.plotTracks()

    def updateSliderLabel(self, value):
        if self.WAIT is False:
            PAR_values[self.selected]=float(value)
            self.sliderLabel.setText(str(value))
            if self.selected==0:
                self.ftracks=[]
                self.redtracks=[]
            elif self.selected==1:
                self.redtracks=[]
            self.plotTracks()
        
    def previousPage(self):
        self.ftracks=[]
        self.redtracks=[]
        if self.currentPage > 1:
            self.currentPage -= 1
            self.plotTracks()

    def nextPage(self):
        self.ftracks=[]
        self.redtracks=[]
        if self.currentPage < self.totalPages:
            self.currentPage += 1
            self.plotTracks()
            
    def showPreviewModal(self):    
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview Plots")
        layout = QVBoxLayout()
        
        def showHist(data,block,name,bins='auto'):
            graphWidget = pg.PlotWidget()
            y,x = np.histogram(data, bins=bins)        
            graphWidget.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,150))
            graphWidget.setLabel('left', f'Count')
            graphWidget.setLabel('bottom', name)
            block.addWidget(graphWidget)            

        #Exract the datasets
        datasets = self.getDatasets()
        # Create a 2x2 grid layout for the graphs
        topRow = QHBoxLayout()
        bottomRow = QHBoxLayout()
        #Show the histograms
        showHist(datasets[0],topRow,'Number of active segments per track',range(0, max(datasets[0]) + 1))
        showHist(datasets[1],topRow,'Intensity')
        showHist(datasets[2],bottomRow,'Duration')
        showHist(datasets[3],bottomRow,'Relative Intensity')
        #Set the view
        layout.addLayout(topRow)
        layout.addLayout(bottomRow)
        dialog.setLayout(layout)
        dialog.exec()

    def updatePagination(self):
        self.pageLabel.setText(f"{self.currentPage} of {self.totalPages}")
        self.prevButton.setEnabled(self.currentPage > 1)
        self.nextButton.setEnabled(self.currentPage < self.totalPages)
        self.tracksLabel.setText(f"Tracks: {len(self.tracks)}")
        self.ftracks=[]
        self.redtracks=[]
        #comment
        
    def getDatasets(self):
        stats,baselines=self.getStats()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        datasets=[[],[],[],[]]        
        for i in range(len(stats)):
            datasets[0].append(operations.count_steps(stats[i],baselines[i],PAR_values[2]))
            datasets[1]+=operations.intensity(stats[i])
            datasets[2]+=operations.duration(stats[i],baselines[i],PAR_values[2])
            datasets[3]+=operations.intensity(stats[i],baselines[i],PAR_values[2])
        QApplication.restoreOverrideCursor()
        return datasets

    def getStats(self):
        stats = []        
        baselines=[]
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for time, intensity in self.tracks:
            fintensity = (operations.filter(intensity,PAR_values[0]))
            gauge = operations.corners(fintensity,PAR_values[1])
            pplus = operations.cliffs(gauge,PAR_values[2],PAR_values[3])
            pminus = operations.cliffs(-gauge,PAR_values[2],PAR_values[3])            
            segments = operations.create_steps(time, intensity, pplus[0], pminus[0],  self.Slider.value())
            stats.append(segments)
            baselines.append(operations.baseline(intensity))
        QApplication.restoreOverrideCursor()
        return stats,baselines

    def saveData(self):
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", "Excel Files (*.xlsx)")
        if filename == '':
            return
        
        datasets = self.getDatasets()
        
        df0 = pd.DataFrame(PAR_values,columns=['Parameters'])
        df1 = pd.DataFrame(datasets[0],columns=['Count'])
        df2 = pd.DataFrame(datasets[1],columns=['Intensity'])
        df3 = pd.DataFrame(datasets[2],columns=['Duration'])
        df4 = pd.DataFrame(datasets[3],columns=['Relative intensity'])
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df0.to_excel(writer, sheet_name='Parameters')
            df1.to_excel(writer, sheet_name='Number')
            df2.to_excel(writer, sheet_name='Intensity')
            df3.to_excel(writer, sheet_name='Duration')
            df4.to_excel(writer, sheet_name='Step Intensity')

    def plotTracks(self):
        if self.WAIT is False:
            if len(self.tracks) == 0:
                return
            self.updatePagination()
            start = (self.currentPage - 1) * 20
            end = start + 20
            for i, graphWidget in enumerate(self.graphWidgets):
                graphWidget.clear()
                if start + i < len(self.tracks):
                    time, intensity = self.tracks[start + i]
                    baseline = operations.baseline(intensity)
                    graphWidget.plot(time, intensity)
                    if len(self.ftracks)==i:
                        self.ftracks.append(operations.filter(intensity,PAR_values[0]))
                    if self.selected<4:
                        graphWidget.plot(time, self.ftracks[i],pen='y')
                        graphWidget.plot([time[0],time[-1]], [baseline,baseline],pen='c')
                    if 0<self.selected<4:
                        if len(self.redtracks)==i:
                            self.redtracks.append(operations.corners(self.ftracks[i],PAR_values[1]))
                        graphWidget.plot(time, np.average(self.ftracks[i])+ self.redtracks[i],pen='r')
                        if 1<self.selected<4:
                            peaksplus = operations.cliffs(self.redtracks[i],PAR_values[2],PAR_values[3])
                            peaksminus = operations.cliffs(-self.redtracks[i],PAR_values[2],PAR_values[3])
                            if peaksplus is not None:
                                for j in peaksplus[0]:
                                    value = np.average(self.ftracks[i])+self.redtracks[i][j]
                                    graphWidget.plot([time[j]], [value],symbol='o',pen='r')
                            if peaksminus is not None:
                                for j in peaksminus[0]:
                                    value = np.average(self.ftracks[i])+self.redtracks[i][j]
                                    graphWidget.plot([time[j]], [value],symbol='o',pen='g')
                    if self.selected == 4:
                        if len(self.redtracks)==i:
                            self.redtracks.append(operations.corners(intensity,PAR_values[1]))
                        pplus = operations.cliffs(self.redtracks[i],PAR_values[2],PAR_values[3])
                        pminus = operations.cliffs(-self.redtracks[i],PAR_values[2],PAR_values[3])
                        segments = operations.create_steps(time, intensity, pplus[0], pminus[0],  self.Slider.value())
                        up = True
                        for segment in segments:
                            if baseline-PAR_values[2]<np.average(segment[1])< baseline+PAR_values[2]:
                                color = 'c'
                            else:
                                color = 'g' if up else 'r'
                                up = not up
                            graphWidget.plot(segment[0], np.ones_like(segment[1])*np.average(segment[1]), pen=color)

    def previewResults(self):
        self.combo_box.setCurrentIndex(4)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())