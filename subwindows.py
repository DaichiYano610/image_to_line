import tkinter as tk
from PIL import Image, ImageTk
import cv2

class ImageViwerApp:
    def __init__(self, subwindow ,cv2_image):
        self.root = subwindow
        self.root.title("line_img")

        # ウィンドウを最大化する
        self.root.state("zoomed")

        # cv2の画像データを保存
        self.original_image = cv2_image

        # Canvasウィジェットを作成する
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ウィンドウのサイズ変更イベントにハンドラをバインドする
        self.root.bind("<Configure>", self.resize_image)

    def resize_image(self, event):
        # ウィンドウの新しいサイズを取得する
        new_width = event.width
        new_height = event.height

        # アスペクト比を維持しながらcv2で画像をリサイズする
        height, width = self.original_image.shape[:2]
        aspect_ratio = width / height

        if new_width / aspect_ratio <= new_height:
            resized_width = new_width
            resized_height = int(new_width / aspect_ratio)
        else:
            resized_width = int(new_height * aspect_ratio)
            resized_height = new_height

        # リサイズを実行
        resized_image = cv2.resize(self.original_image, (resized_width, resized_height), interpolation=cv2.INTER_AREA)

        # リサイズされたcv2画像をPIL形式に変換し、Tkinterで使用する形式に変換
        self.photo_image = self.cv2_to_pil(resized_image)

        # 古い画像を削除
        self.canvas.delete("all")

        # キャンバスに描画する
        self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)

    def cv2_to_pil(self, img_cv):
        """OpenCVからPIL形式に画像を変換する関数"""
        # BGRからRGBに変換
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        # OpenCVの画像をPIL形式に変換
        img_pil = Image.fromarray(img_rgb)
        # PILからTkinter用のImageTk.PhotoImageに変換
        img_tk = ImageTk.PhotoImage(img_pil)
        return img_tk

if __name__ == "__main__":
    # 例としてcv2で画像を読み込む
    cv2_image = cv2.imread("victria_night.jpg")

    app = ImageViwerApp(cv2_image)
    app.root.mainloop()
