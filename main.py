import sys
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QTableView, QVBoxLayout

from src.app.data_view import PandasModel
from src.data_processor.import_data import ImportSettings, ReadOrder

base_dir = Path(__file__).resolve().parent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Prototype 01")
        self.setMinimumSize(QSize(800, 500))

        # Khởi tạo các công cụ xử lý
        self.setting_importer = ImportSettings()
        self.order_importer = ReadOrder()

        self.init_ui()
        self.init_signals()

        self.model = None

    def init_ui(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Tệp")

        # 1. Action nạp Settings
        self.import_config_act = QAction(
            QIcon(str(base_dir / "src/static/file-cog.svg")),
            "1. Mở tệp cấu hình",
            self
        )
        file_menu.addAction(self.import_config_act)

        # 2. Action nạp Đơn hàng
        self.import_order_act = QAction(
            QIcon(str(base_dir / "src/static/file-icon.svg")),
            "2. Mở tệp đơn hàng",
            self
        )
        file_menu.addAction(self.import_order_act)
        self.import_order_act.setEnabled(False)

        self.table_view = QTableView()

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_signals(self):
        # Kết nối chính xác tên hàm
        self.import_config_act.triggered.connect(self.open_setting)
        self.import_order_act.triggered.connect(self.open_order)

    def open_setting(self):
        # Lưu ý: Setting thường chỉ cần 1 file, dùng getOpenFileName (không có 's')
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file cấu hình",
            "",
            "Tệp Excel (*.xlsx)"
        )

        if file_path:
            result = self.setting_importer.get_settings(file_path)
            if result:
                QMessageBox.information(
                    self,
                    "Thông báo",
                    "Nạp cấu hình thành công! Bạn có thể chọn đơn hàng."
                )
                # KÍCH HOẠT nút mở đơn hàng
                self.import_order_act.setEnabled(True)
                self.import_config_act.setText("✓ Đã nạp cấu hình")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể đọc dữ liệu cấu hình.")

    def open_order(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Chọn các file đơn hàng", "", "Excel (*.xlsx);;CSV (*.csv)"
        )

        if file_paths:
            raw_df = self.order_importer.read_files(file_paths)

            final_df = self.order_importer.process_data(raw_df, self.setting_importer)

            if final_df is not None:
                self.model = PandasModel(final_df)
                self.table_view.setModel(self.model)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())