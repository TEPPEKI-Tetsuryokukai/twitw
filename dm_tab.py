from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QLineEdit,
    QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt

class DMTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.selected_user_id = None

        self.init_ui()
        self.load_dms()

    def init_ui(self):
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("相手のユーザー名またはIDを入力")
        self.search_btn = QPushButton("ユーザー選択")
        self.search_btn.clicked.connect(self.select_user)
        search_layout.addWidget(self.user_input)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        self.dm_list = QListWidget()
        layout.addWidget(QLabel("DM履歴"))
        layout.addWidget(self.dm_list)

        send_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(70)
        self.send_btn = QPushButton("送信")
        self.send_btn.clicked.connect(self.send_dm)
        send_layout.addWidget(self.message_input)
        send_layout.addWidget(self.send_btn)

        layout.addLayout(send_layout)

        self.setLayout(layout)

    def select_user(self):
        username_or_id = self.user_input.text().strip()
        if not username_or_id:
            QMessageBox.warning(self, "入力エラー", "ユーザー名またはIDを入力してください")
            return
        try:
            if username_or_id.isdigit():
                user = self.client.get_user(user_id=int(username_or_id))
            else:
                user = self.client.get_user(username=username_or_id)
            self.selected_user_id = user.id
            QMessageBox.information(self, "ユーザー選択完了", f"相手: @{user.username}")
            self.load_dms()
        except Exception as e:
            QMessageBox.warning(self, "ユーザー取得失敗", str(e))

    def load_dms(self):
        self.dm_list.clear()
        if not self.selected_user_id:
            return
        try:
            # 最新50件のDMを取得
            dms = self.client.get_direct_messages(count=50)
            for dm in reversed(dms):
                if dm.message_create['target']['recipient_id'] == str(self.selected_user_id) or \
                   dm.message_create['sender_id'] == str(self.selected_user_id):
                    sender = "あなた" if dm.message_create['sender_id'] != str(self.selected_user_id) else f"@{self.client.get_me().username}"
                    text = dm.message_create['message_data']['text']
                    self.dm_list.addItem(f"{sender}: {text}")
        except Exception as e:
            QMessageBox.warning(self, "DM取得失敗", str(e))

    def send_dm(self):
        if not self.selected_user_id:
            QMessageBox.warning(self, "エラー", "まずユーザーを選択してください")
            return
        text = self.message_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "エラー", "メッセージが空です")
            return
        try:
            self.client.send_direct_message(self.selected_user_id, text)
            QMessageBox.information(self, "送信成功", "DMを送信しました")
            self.message_input.clear()
            self.load_dms()
        except Exception as e:
            QMessageBox.warning(self, "送信失敗", str(e))
