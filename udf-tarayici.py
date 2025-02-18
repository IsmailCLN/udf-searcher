import os
import re
import zipfile
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget,
    QHBoxLayout,
)


class UDFSearcherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UDF Dosya Arama")
        self.setGeometry(100, 100, 800, 600)

        # Ana widget ve layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Dizin seçimi
        self.directory_label = QLabel("Dizin Seç:")
        layout.addWidget(self.directory_label)
        dir_layout = QHBoxLayout()
        self.directory_input = QLineEdit()
        self.browse_button = QPushButton("Gözat")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.directory_input)
        dir_layout.addWidget(self.browse_button)
        layout.addLayout(dir_layout)

        # Arama ifadesi
        self.search_label = QLabel("Aranacak İfade:")
        layout.addWidget(self.search_label)
        self.search_input = QLineEdit()
        layout.addWidget(self.search_input)

        # Arama başlatma butonu
        self.search_button = QPushButton("Ara")
        self.search_button.clicked.connect(self.start_search)
        layout.addWidget(self.search_button)

        # Sonuç alanı
        self.results_label = QLabel("Sonuçlar:")
        layout.addWidget(self.results_label)
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.open_file)
        layout.addWidget(self.results_list)

        # Copyright ve link
        self.copyright_label = QLabel(
            '<a href="https://ismailcelen.netlify.app/">© İsmail ÇELEN. Tüm hakları saklıdır.</a>'
        )
        copyright_layout = QHBoxLayout()
        copyright_layout.addStretch()
        copyright_layout.addWidget(self.copyright_label)
        copyright_layout.addStretch()
        layout.addLayout(copyright_layout)

        self.setCentralWidget(central_widget)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Dizin Seç")
        if directory:
            self.directory_input.setText(directory)

    def start_search(self):
        directory = self.directory_input.text().strip()
        search_string = self.search_input.text().strip()

        if not directory or not os.path.isdir(directory):
            self.results_list.clear()
            self.results_list.addItem("Geçerli bir dizin seçin.")
            return

        if not search_string:
            self.results_list.clear()
            self.results_list.addItem("Aranacak bir ifade girin.")
            return

        self.results_list.clear()
        self.results_list.addItem("Arama yapılıyor...")
        QApplication.processEvents()
        results = self.search_in_udf_files(directory, search_string)
        results += self.search_in_file_names(directory, search_string)
        self.results_list.clear()
        if results:
            for result in results:
                self.results_list.addItem(result)
        else:
            self.results_list.addItem(
                f"'{search_string}' ifadesi hiçbir dosyada bulunamadı."
            )

    def search_in_file_names(self, directory, search_string):
        found_files = []
        regex = re.compile(rf"\w*{re.escape(search_string)}\w*", re.IGNORECASE)

        for root, _, files in os.walk(directory):
            for file in files:
                if regex.search(file):
                    found_files.append(os.path.join(root, file))
        return found_files

    def search_in_udf_files(self, directory, search_string):
        found_files = []
        regex = re.compile(rf"\w*{re.escape(search_string)}\w*", re.IGNORECASE)

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".udf"):
                    file_path = os.path.join(root, file)
                    try:
                        with zipfile.ZipFile(file_path, "r") as zip_ref:
                            xml_files = [
                                f for f in zip_ref.namelist() if f.endswith(".xml")
                            ]
                            for xml_file in xml_files:
                                with zip_ref.open(xml_file) as xml_content:
                                    try:
                                        content = xml_content.read().decode("utf-8")
                                        if regex.search(content):
                                            found_files.append(file_path)
                                            break
                                    except Exception as e:
                                        print(f"XML okuma hatası: {xml_file} - {e}")
                    except zipfile.BadZipFile:
                        print(f"Geçersiz zip dosyası: {file_path}")
                    except Exception as e:
                        print(f"Hata oluştu: {file_path} - {e}")
        return found_files

    def open_file(self, item):
        file_path = item.text()
        os.startfile(file_path)


if __name__ == "__main__":
    app = QApplication([])
    window = UDFSearcherApp()
    window.show()
    app.exec()
