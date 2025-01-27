        super().__init__()
        self.setWindowTitle("Audio GUI")
        self.graphType = "A(t)"

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout_bottom = QHBoxLayout()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_audio)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        graph_menu = menu_bar.addMenu("Graph")
        at_action = QAction("A(t)", self)
        af_action = QAction("A(f)", self)
        at_action.triggered.connect(self.at_action_graph)
        af_action.triggered.connect(self.af_action_graph)
        graph_menu.addAction(at_action)
        graph_menu.addAction(af_action)

        self.graph = PlotWidget()
        main_layout.addWidget(self.graph)

        controls_layout = QHBoxLayout()
        TbRf_layout = QVBoxLayout()
        controlsEqRv_layout = QHBoxLayout()
        controlsThGn_layout = QHBoxLayout()
        main_controls_layout = QVBoxLayout()

        Th_layout = QVBoxLayout()
        Gn_layout = QVBoxLayout()
        Dl_layout = QVBoxLayout()

        self.empty_space0 = self.create_dial("", controlsEqRv_layout)
        self.empty_space0.hide()

        self.treble_slider = self.create_slider("Treble", controlsEqRv_layout)
        self.treble_slider.setValue(100)
        self.treble_slider.setRange(50, 150)

        self.empty_space1 = self.create_dial("", controlsEqRv_layout)
        self.empty_space1.hide()

        self.mid_slider = self.create_slider("Mid", controlsEqRv_layout)
        self.mid_slider.setValue(100)
        self.mid_slider.setRange(50, 150)

        self.empty_space2 = self.create_dial("", controlsEqRv_layout)
        self.empty_space2.hide()

        self.bass_slider = self.create_slider("Bass", controlsEqRv_layout)
        self.bass_slider.setValue(100)
        self.bass_slider.setRange(50, 150)

        self.empty_space3 = self.create_dial("", controlsEqRv_layout)
        self.empty_space3.hide()

        reverb_layout = QVBoxLayout()
        self.decay_dial = self.create_dial("Decay", reverb_layout, 1)
        self.decay_dial.setRange(0, 100)
        self.wetness_dial = self.create_dial("Wetness", reverb_layout)
        self.wetness_dial.setRange(0, 100)
        Dl_layout.addWidget(QLabel("Delay [ms]"))
        self.delay_input = QSpinBox()
        self.delay_input.setRange(0, 5000)
        self.delay_input.setValue(0)
        Dl_layout.addWidget(self.delay_input)
        reverb_layout.addLayout(Dl_layout)

        controlsEqRv_layout.addLayout(reverb_layout)
        controls_layout.addLayout(controlsEqRv_layout)

        threshold_layout = QHBoxLayout()
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(-50, 50)
        self.threshold_input.setValue(0)
        Th_layout.addWidget(QLabel("Threshold [dB]"))
        Th_layout.addWidget(self.threshold_input)
        threshold_layout.addLayout(Th_layout)
        self.level_dial = self.create_dial("Level", threshold_layout)
        controlsThGn_layout.addLayout(threshold_layout)

        self.gain_input = QSpinBox()
        self.gain_input.setRange(-50, 50)
        self.gain_input.setValue(0)
        Gn_layout.addWidget(QLabel("Gain [dB]"))
        Gn_layout.addWidget(self.gain_input)
        controlsThGn_layout.addLayout(Gn_layout)

        main_controls_layout.addLayout(controls_layout)
        main_controls_layout.addLayout(controlsThGn_layout)
        main_layout_bottom.addLayout(main_controls_layout)

        self.file_table = QTableWidget(1, 4)
        self.file_table.setHorizontalHeaderLabels(["File name", "File size [B]", "Time [s]", "Max Amplitude [dB]"])
        self.file_table.horizontalHeader().setStyleSheet("color: black")
        TbRf_layout.addWidget(self.file_table)
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_action)
        TbRf_layout.addWidget(self.refresh_button)
        main_layout_bottom.addLayout(TbRf_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        main_layout.addLayout(main_layout_bottom)

        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }

            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QSlider, QDial, QSpinBox {
                background-color: #444444;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }

            QSlider::handle:horizontal {
                background: #4CAF50;
                border-radius: 5px;
                width: 10px;
            }

            QDial {
                border: 2px solid #4CAF50;
            }

            QTableWidget {
                background-color: #333333;
                color: white;
            }

            QTableWidget::item {
                padding: 5px;
            }

            QTableWidget::horizontalHeader {
                background-color: black;
                color: white;
                font-weight: bold;
            }
        """)
