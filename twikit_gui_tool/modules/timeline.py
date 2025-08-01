from tkinter import Canvas, Frame, Scrollbar, Label, PhotoImage, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

class TimelineTab:
    def __init__(self, master, client):
        self.master = master
        self.client = client

        self.canvas = Canvas(master)
        self.scrollbar = Scrollbar(master, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_timeline()

    def refresh_timeline(self):
        try:
            timeline = self.client.get_home_timeline(count=50)
            for tweet in timeline:
                self.display_tweet(tweet)
        except Exception as e:
            messagebox.showerror("タイムライン取得失敗", str(e))

    def display_tweet(self, tweet):
        tweet_frame = Frame(self.scrollable_frame, bd=1, relief="solid", padx=5, pady=5)
        tweet_frame.pack(fill="x", padx=5, pady=5)

        user_label = Label(tweet_frame, text=f"@{tweet.user.username}", font=("Arial", 10, "bold"), fg="blue")
        user_label.pack(anchor="w")

        text_label = Label(tweet_frame, text=tweet.full_text, wraplength=500, justify="left")
        text_label.pack(anchor="w")

        if tweet.media:
            for media in tweet.media:
                if media.media_url_https.endswith(('.jpg', '.png', '.jpeg')):
                    try:
                        img_data = requests.get(media.media_url_https).content
                        img = Image.open(BytesIO(img_data))
                        img.thumbnail((400, 300))
                        photo = ImageTk.PhotoImage(img)
                        img_label = Label(tweet_frame, image=photo)
                        img_label.image = photo
                        img_label.pack(anchor="w")
                    except:
                        continue
