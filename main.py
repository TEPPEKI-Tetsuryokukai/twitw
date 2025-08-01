import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog, QMessageBox, QTabWidget, QScrollArea,
    QFrame
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from twikit import Client
import requests
from io import BytesIO
from PIL import Image

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Twikit X GUI - ログイン")
        self.client = Client()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.email_label = QLabel("メールアドレス")
        self.email_input = QLineEdit()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        self.pass_label = QLabel("パスワード")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)

        self.login_btn = QPushButton("ログイン")
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def try_login(self):
        email = self.email_input.text()
        password = self.pass_input.text()
        try:
            self.client.login(email=email, password=password)
            self.main_window = MainWindow(self.client)
            self.main_window.show()
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "ログイン失敗", str(e))


class TweetTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.image_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("ここにツイート内容を入力")
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        self.image_btn = QPushButton("画像を添付")
        self.image_btn.clicked.connect(self.select_image)
        btn_layout.addWidget(self.image_btn)

        self.tweet_btn = QPushButton("ツイート送信")
        self.tweet_btn.clicked.connect(self.post_tweet)
        btn_layout.addWidget(self.tweet_btn)

        layout.addLayout(btn_layout)

        self.image_label = QLabel()
        layout.addWidget(self.image_label)

        self.setLayout(layout)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "画像ファイルを選択", "", "Images (*.png *.jpg *.jpeg *.gif)")
        if path:
            self.image_path = path
            pixmap = QPixmap(path).scaledToWidth(200, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)

    def post_tweet(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "入力エラー", "ツイート内容が空です")
            return
        try:
            if self.image_path:
                media = self.client.upload_media(self.image_path)
                self.client.create_tweet(text=text, media_ids=[media.media_id])
            else:
                self.client.create_tweet(text=text)
            QMessageBox.information(self, "成功", "ツイートを投稿しました！")
            self.text_edit.clear()
            self.image_label.clear()
            self.image_path = None
        except Exception as e:
            QMessageBox.warning(self, "投稿失敗", str(e))


class TimelineTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)

        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)

        self.setLayout(layout)
        self.refresh_timeline()

    def refresh_timeline(self):
        try:
            timeline = self.client.get_home_timeline(count=50)
            for tweet in timeline:
                self.display_tweet(tweet)
        except Exception as e:
            QMessageBox.warning(self, "タイムライン取得失敗", str(e))

    def display_tweet(self, tweet):
        tweet_frame = QFrame()
        tweet_frame.setFrameShape(QFrame.StyledPanel)
        tweet_layout = QVBoxLayout()
        tweet_frame.setLayout(tweet_layout)

        user_label = QLabel(f"@{tweet.user.username}")
        user_label.setStyleSheet("font-weight: bold; color: blue;")
        tweet_layout.addWidget(user_label)

        text_label = QLabel(tweet.full_text)
        text_label.setWordWrap(True)
        tweet_layout.addWidget(text_label)

        if tweet.media:
            for media in tweet.media:
                if media.media_url_https.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    try:
                        response = requests.get(media.media_url_https)
                        img = Image.open(BytesIO(response.content))
                        img.thumbnail((400, 300))
                        data = BytesIO()
                        img.save(data, format='PNG')
                        data.seek(0)
                        qimg = QPixmap()
                        qimg.loadFromData(data.read())
                        img_label = QLabel()
                        img_label.setPixmap(qimg)
                        tweet_layout.addWidget(img_label)
                    except Exception:
                        continue

        self.content_layout.addWidget(tweet_frame)
        self.content_layout.addStretch(0)


class MainWindow(QTabWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Twikit X GUI - メイン")
        self.resize(700, 600)

        self.tweet_tab = TweetTab(self.client)
        self.timeline_tab = TimelineTab(self.client)

        self.addTab(self.tweet_tab, "投稿")
        self.addTab(self.timeline_tab, "タイムライン")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())
