import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeView, QStatusBar, QMenuBar, QAction, QSplitter, QLabel, QMessageBox, QAbstractItemView, QStyle
)
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont

from drive_auth import DriveAuthenticator

class GoogleDriveTransferApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MirrorDrive")
        self.setGeometry(100, 100, 1200, 800)

        self.source_drive = None
        self.dest_drive = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self._create_menu_bar()

        button_layout = QHBoxLayout()
        self.auth_source_btn = QPushButton("1. Kaynak Hesabı Yetkilendir")
        self.auth_source_btn.clicked.connect(self.authenticate_source)
        
        self.auth_dest_btn = QPushButton("2. Hedef Hesabı Yetkilendir")
        self.auth_dest_btn.clicked.connect(self.authenticate_destination)

        self.transfer_btn = QPushButton("--> Transfer Et < --")
        self.transfer_btn.setEnabled(False)
        self.transfer_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        self.transfer_btn.clicked.connect(self.start_transfer)

        button_layout.addWidget(self.auth_source_btn)
        button_layout.addWidget(self.auth_dest_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.transfer_btn)
        main_layout.addLayout(button_layout)

        splitter = QSplitter(Qt.Horizontal)
        self.source_tree, self.source_quota_label, source_widget = self._create_tree_view("Kaynak Sürücü")
        self.dest_tree, self.dest_quota_label, dest_widget = self._create_tree_view("Hedef Sürücü")
        splitter.addWidget(source_widget)
        splitter.addWidget(dest_widget)
        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Lütfen önce kaynak ve hedef hesapları yetkilendirin.")

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Dosya")
        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        help_menu = menu_bar.addMenu("Yardım")
        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def _create_tree_view(self, label_text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        tree_view = QTreeView()
        tree_view.setHeaderHidden(True)
        tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tree_view.expanded.connect(self.on_item_expanded)
        
        quota_label = QLabel("Kota bilgisi için yetkilendirin.")
        quota_label.setAlignment(Qt.AlignCenter)
        font = quota_label.font()
        font.setPointSize(9)
        quota_label.setFont(font)

        layout.addWidget(label)
        layout.addWidget(tree_view)
        layout.addWidget(quota_label)
        return tree_view, quota_label, widget

    def authenticate_source(self):
        self._authenticate_drive('source')

    def authenticate_destination(self):
        self._authenticate_drive('destination')

    def _authenticate_drive(self, drive_type):
        is_source = drive_type == 'source'
        self.status_bar.showMessage(f"{'Kaynak' if is_source else 'Hedef'} hesap yetkilendiriliyor...")
        try:
            auth = DriveAuthenticator(credentials_file=f'credentials_{drive_type}.json')
            drive_instance = auth.authenticate()
            if is_source:
                self.source_drive = drive_instance
                btn = self.auth_source_btn
                tree = self.source_tree
                self.update_quota_display(self.source_drive, self.source_quota_label)
            else:
                self.dest_drive = drive_instance
                btn = self.auth_dest_btn
                tree = self.dest_tree
                self.update_quota_display(self.dest_drive, self.dest_quota_label)
            
            self.status_bar.showMessage(f"{'Kaynak' if is_source else 'Hedef'} hesap başarıyla yetkilendirildi.")
            btn.setEnabled(False)
            btn.setText(f"✓ {'Kaynak' if is_source else 'Hedef'} Yetkilendirildi")
            self.populate_tree(drive_instance, tree)
            self.check_auth_status()
        except Exception as e:
            error_msg = f"{'Kaynak' if is_source else 'Hedef'} yetkilendirme hatası: {e}"
            self.status_bar.showMessage(error_msg)
            QMessageBox.critical(self, "Hata", error_msg)

    def on_item_expanded(self, index):
        tree_view = self.sender()
        item = tree_view.model().itemFromIndex(index)
        if not item.hasChildren() or (item.hasChildren() and item.child(0).text() != ""):
            return
        item.removeRow(0)
        drive = self.source_drive if tree_view is self.source_tree else self.dest_drive
        if not drive:
            return
        folder_id = item.data(Qt.UserRole)
        self.load_folder_contents(drive, item, folder_id)

    def load_folder_contents(self, drive, parent_item, parent_id):
        self.status_bar.showMessage(f"'{parent_item.text()}' içeriği yükleniyor...")
        QCoreApplication.processEvents()
        try:
            file_list = drive.ListFile({'q': f"'{parent_id}' in parents and trashed=false"}).GetList()
            if not file_list:
                placeholder = QStandardItem("(Klasör boş)")
                placeholder.setEnabled(False)
                parent_item.appendRow(placeholder)
                return
            for file_item in file_list:
                item = QStandardItem(file_item['title'])
                item.setData(file_item['id'], Qt.UserRole)
                item.setData(file_item['mimeType'], Qt.UserRole + 1)
                if file_item['mimeType'] == 'application/vnd.google-apps.folder':
                    item.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
                    item.appendRow(QStandardItem())
                else:
                    item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
                parent_item.appendRow(item)
        except Exception as e:
            self.status_bar.showMessage(f"Klasör içeriği yüklenemedi: {e}")

    def populate_tree(self, drive, tree_view):
        model = QStandardItemModel()
        tree_view.setModel(model)
        root_item = model.invisibleRootItem()
        root_item.setText("Drive")
        self.load_folder_contents(drive, root_item, 'root')
        self.status_bar.showMessage("Ana dizin başarıyla yüklendi.", 5000)

    def check_auth_status(self):
        if self.source_drive and self.dest_drive:
            self.transfer_btn.setEnabled(True)
            self.status_bar.showMessage("Her iki hesap da yetkilendirildi. Transfer için hazır.")

    def start_transfer(self):
        source_indexes = self.source_tree.selectionModel().selectedIndexes()
        dest_index = self.dest_tree.selectionModel().currentIndex()
        if not source_indexes:
            QMessageBox.warning(self, "Hata", "Lütfen kaynaktan en az bir dosya veya klasör seçin.")
            return
        if not dest_index.isValid():
            QMessageBox.warning(self, "Hata", "Lütfen hedeften bir ana klasör seçin.")
            return
        dest_item = self.dest_tree.model().itemFromIndex(dest_index)
        dest_parent_id = dest_item.data(Qt.UserRole)
        dest_parent_mime = dest_item.data(Qt.UserRole + 1)
        if dest_parent_mime != 'application/vnd.google-apps.folder':
            QMessageBox.warning(self, "Hata", "Lütfen hedef olarak bir klasör seçin.")
            return
        try:
            dest_email = self.dest_drive.GetAbout()['user']['emailAddress']
            self.transfer_btn.setEnabled(False)
            QCoreApplication.processEvents()
            for index in source_indexes:
                if index.column() == 0:
                    source_item = self.source_tree.model().itemFromIndex(index)
                    source_id = source_item.data(Qt.UserRole)
                    source_title = source_item.text()
                    self.transfer_item_recursively(source_id, source_title, dest_parent_id, dest_email)
            QMessageBox.information(self, "Başarılı", "Transfer işlemi tamamlandı.")
            self.populate_tree(self.dest_drive, self.dest_tree)
            self.update_quota_display(self.source_drive, self.source_quota_label)
            self.update_quota_display(self.dest_drive, self.dest_quota_label)
        except Exception as e:
            self.status_bar.showMessage(f"Transfer sırasında bir hata oluştu: {e}")
            QMessageBox.critical(self, "Transfer Hatası", f"Bir hata meydana geldi:\n{e}")
        finally:
            self.transfer_btn.setEnabled(True)

    def transfer_item_recursively(self, source_id, source_title, dest_parent_id, dest_email):
        source_file = self.source_drive.CreateFile({'id': source_id})
        source_file.FetchMetadata(fields='mimeType, title')
        source_mime = source_file['mimeType']
        if source_mime == 'application/vnd.google-apps.folder':
            self.status_bar.showMessage(f"Klasör oluşturuluyor: '{source_title}'")
            QCoreApplication.processEvents()
            new_folder = self.dest_drive.CreateFile({
                'title': source_title,
                'parents': [{'id': dest_parent_id}],
                'mimeType': 'application/vnd.google-apps.folder'
            })
            new_folder.Upload()
            children = self.source_drive.ListFile({'q': f"'{source_id}' in parents and trashed=false"}).GetList()
            for child in children:
                self.transfer_item_recursively(child['id'], child['title'], new_folder['id'], dest_email)
        else:
            self.status_bar.showMessage(f"Dosya transfer ediliyor: '{source_title}'")
            QCoreApplication.processEvents()
            source_file_for_perms = self.source_drive.CreateFile({'id': source_id})
            permission = source_file_for_perms.InsertPermission({
                'type': 'user',
                'value': dest_email,
                'role': 'reader'
            })
            self.dest_drive.auth.service.files().copy(
                fileId=source_id, body={'parents': [{'id': dest_parent_id}], 'title': source_title}
            ).execute()
            source_file_for_perms.DeletePermission(permission['id'])

    def update_quota_display(self, drive, label):
        try:
            about = drive.GetAbout()
            used = int(about['quotaBytesUsed'])
            total = int(about['quotaBytesTotal'])
            label.setText(f"Kullanım: {self._format_bytes(used)} / {self._format_bytes(total)}")
        except Exception as e:
            label.setText("Kota bilgisi alınamadı.")
            self.status_bar.showMessage(f"Kota bilgisi hatası: {e}")

    @staticmethod
    def _format_bytes(byte_count):
        if byte_count is None: return "N/A"
        power = 1024
        n = 0
        power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while byte_count >= power and n < len(power_labels) -1 :
            byte_count /= power
            n += 1
        return f"{byte_count:.2f} {power_labels[n]}B"

    def show_about_dialog(self):
        QMessageBox.about(self, "Hakkında",
            """MirrorDrive<br><br>
            İki Google Drive hesabı arasında dosya ve klasör transferi yapar.<br><br>
            Geliştirici: <a href='https://github.com/mrr00tsuz'>mrr00tsuz</a>
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = GoogleDriveTransferApp()
    main_win.show()
    sys.exit(app.exec_())