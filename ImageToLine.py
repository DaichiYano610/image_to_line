import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk

from subwindows import ImageViwerApp

class ImageToLineApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image to line")
        self.root.state('zoomed')
        #背景色
        self.background_color = "#58707B"
        self.root.configure(bg = self.background_color)


        # 画像のソースデータ
        self.img_cv2 = None
        self.img_cv2_line = None
        self.img_cv2_binary = None
        self.img_cv2_opened_line = None
        self.img_cv2_opened_binary = None

        # スクロール可能なフレームを作成
        self.canvas = tk.Canvas(self.root, bg=self.background_color)
        
        # 垂直スクロールバー
        self.v_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")

        # 水平スクロールバー
        self.h_scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # フレームをキャンバスに配置
        self.frame = tk.Frame(self.canvas, bg=self.background_color)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # キャンバスとフレームの配置
        self.canvas.pack(side="left", fill="both", expand=True)

        # スクロール領域をフレームサイズに適応
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))

        # マウスホイールイベントのバインド
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        #表示する画像のサイズ
        self.display_width = 750
        self.display_height = 450

        self.padx = 3
        self.pady = 3

        # 画像表示ラベルを作成
        self.label_original = tk.Label(self.frame, width = self.display_width, height= self.display_height, bg = self.background_color)
        self.label_original.grid(row = 0, column = 0, padx = self.padx, pady = self.pady)
        self.label_original.bind("<Button-1>", self.view_img)

        self.label_line = tk.Label(self.frame, width = self.display_width, height= self.display_height, bg = self.background_color)
        self.label_line.grid(row=2, column=0, padx = self.padx, pady = self.pady)
        self.label_line.bind("<Button-1>", self.view_line_img)

        self.label_binary = tk.Label(self.frame, width = self.display_width, height= self.display_height, bg = self.background_color)
        self.label_binary.grid(row=2, column=1, padx = self.padx, pady = self.pady)
        self.label_binary.bind("<Button-1>", self.view_binary_img)

        self.label_opened_line = tk.Label(self.frame, width = self.display_width, height= self.display_height, bg = self.background_color)
        self.label_opened_line.grid(row=5, column=0, padx = self.padx, pady = self.pady)
        self.label_opened_line.bind("<Button-1>", self.view_opened_line_img)

        self.label_opened_binary = tk.Label(self.frame, width = self.display_width, height= self.display_height, bg = self.background_color)
        self.label_opened_binary.grid(row=5, column=1, padx = self.padx, pady = self.pady)
        self.label_opened_binary.bind("<Button-1>", self.view_opened_binary_img)

        #画像を表示するラベルを追加
        self.label_white = tk.Label(self.frame, width = self.display_width, height= self.display_height, bg = self.background_color)
        self.label_white.grid(row=0, column=1, padx = self.padx, pady = self.pady)

        # ボタンを作成してフレームに配置
        self.button_open = tk.Button(self.frame, text="Open Image", command=self.open_file,
                                     bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.button_open.grid(row=1, column=0, padx=10, pady=10)

        self.button_save_line = tk.Button(self.frame, text="Save Line Image", command=self.save_line_image,
                                          bg="#2196F3", fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.button_save_line.grid(row=3, column=0, padx=10, pady=10)

        self.button_save_binary = tk.Button(self.frame, text="Save Binary Image", command=self.save_binary_image,
                                            bg="#FF5722", fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.button_save_binary.grid(row=3, column=1, padx=10, pady=10)

        self.button_save_opened_line = tk.Button(self.frame, text="Save Opened Line Image", command=self.save_opened_line_image,
                                                bg="#9C27B0", fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.button_save_opened_line.grid(row=6, column=0, padx=10, pady=10)

        self.button_save_opened_binary = tk.Button(self.frame, text="Save Opened Binary Image", command=self.save_opened_binary_image,
                                                  bg="#E91E63", fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.button_save_opened_binary.grid(row=6, column=1, padx=10, pady=10)

        # しきい値を調整するスライダーを追加
        self.threshold_slider = tk.Scale(self.frame, from_=0, to=255, orient=tk.HORIZONTAL, command=self.update_binary_image,
                                         label="Threshold", length = self.display_width * 0.8, bg= self.background_color,foreground = 'white')
        self.threshold_slider.set(230)  # 初期値を設定
        self.threshold_slider.grid(row=4, column=1, columnspan=2, padx=10, pady=10)


        # 初期状態で画像を表示
        init_img = np.ones((self.display_height, self.display_width, 3), dtype=np.uint8) * 50
        self.display_image(self.cv2_to_pil(init_img), self.label_original)
        self.display_image(self.cv2_to_pil(init_img), self.label_line)
        self.display_image(self.cv2_to_pil(init_img), self.label_binary)
        self.display_image(self.cv2_to_pil(init_img), self.label_opened_line)
        self.display_image(self.cv2_to_pil(init_img), self.label_opened_binary)
        self.display_image(self.cv2_to_pil(init_img), self.label_white)



    def display_image(self, img_pil, label):
        """PIL形式の画像を指定したラベルに表示する関数"""
        # PIL画像をTkinterで表示できる形式に変換
        img_tk = ImageTk.PhotoImage(img_pil)
        # 画像をラベルに設定して表示
        label.config(image=img_tk)
        label.image = img_tk  # 参照を保持しないと画像がガベージコレクトされる



    def open_file(self):
        # ファイルダイアログを開いて画像ファイルを選択
        filepath = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )

        if filepath:
            # PILで画像読み込み　※OpenCVで画像を読み込むと日本語を含むディレクトリでエラー
            self.img_cv2 = self.pil_to_cv2(Image.open(filepath))


            if self.img_cv2 is None:
                messagebox.showerror("Error", "Failed to load image. Please try another file.")
                return

            # 画像を線画風に変換
            self.img_cv2_line = self.image_to_line(self.img_cv2)
            # スライダーの初期値で線画画像を2値化
            self.update_binary_image()

            # オープニング処理を適用
            #self.apply_opening()

            width = self.display_width
            height = self.display_height

            # 画像をリサイズしてラベルに合わせる
            img_resized = self.resize_image(self.img_cv2, width, height)
            img_pil = self.cv2_to_pil(img_resized)
            self.display_image(img_pil, self.label_original)
            self.display_image(img_pil, self.label_white)

            # 線画画像をリサイズしてラベルに表示
            img_cv2_line_resized = self.resize_image(self.img_cv2_line, width, height)
            img_pil_line = self.cv2_to_pil(img_cv2_line_resized)
            self.display_image(img_pil_line, self.label_line)

            # 2値化画像をリサイズしてラベルに表示
            img_cv2_binary_resized = self.resize_image(self.img_cv2_binary, width, height)
            img_pil_binary = self.cv2_to_pil(img_cv2_binary_resized)
            self.display_image(img_pil_binary, self.label_binary)

            # オープニング処理後の線画画像をリサイズしてラベルに表示
            img_cv2_opened_line_resized = self.resize_image(self.img_cv2_opened_line, width, height)
            img_pil_opened_line = self.cv2_to_pil(img_cv2_opened_line_resized)
            self.display_image(img_pil_opened_line, self.label_opened_line)

            # オープニング処理後の2値化画像をリサイズしてラベルに表示
            img_cv2_opened_binary_resized = self.resize_image(self.img_cv2_opened_binary, width, height)
            img_pil_opened_binary = self.cv2_to_pil(img_cv2_opened_binary_resized)
            self.display_image(img_pil_opened_binary, self.label_opened_binary)

    def apply_opening(self):
        """オープニング処理を線画画像と2値化画像に適用する関数"""
        if self.img_cv2_line is not None:
            kernel = np.ones((5, 5), np.uint8)
            opened_img_line = cv2.morphologyEx(self.img_cv2_line, cv2.MORPH_OPEN, kernel)
            self.img_cv2_opened_line = opened_img_line

            # オープニング処理後の線画画像をリサイズしてラベルに表示
            img_cv2_opened_line_resized = self.resize_image(self.img_cv2_opened_line, self.display_width, self.display_height)
            img_pil_opened_line = self.cv2_to_pil(img_cv2_opened_line_resized)
            self.display_image(img_pil_opened_line, self.label_opened_line)

        if self.img_cv2_binary is not None:
            kernel = np.ones((5, 5), np.uint8)
            opened_img_binary = cv2.morphologyEx(self.img_cv2_binary, cv2.MORPH_OPEN, kernel)
            self.img_cv2_opened_binary = opened_img_binary

            # オープニング処理後の2値化画像をリサイズしてラベルに表示
            img_cv2_opened_binary_resized = self.resize_image(self.img_cv2_opened_binary, self.display_width, self.display_height)
            img_pil_opened_binary = self.cv2_to_pil(img_cv2_opened_binary_resized)
            self.display_image(img_pil_opened_binary, self.label_opened_binary)

    def resize_image(self, img_cv, target_width, target_height):
        """画像を指定した領域に合わせてリサイズする関数"""
        height, width = img_cv.shape[:2]

        # 画像のアスペクト比を維持しながらリサイズ
        aspect_ratio = width / height
        if width > height:
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * aspect_ratio)

        resized_img = cv2.resize(img_cv, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized_img

    def cv2_to_pil(self, img_cv):
        """OpenCVからPIL形式に画像を変換する関数"""
        # BGRからRGBに変換
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        # OpenCVの画像をPIL形式に変換
        img_pil = Image.fromarray(img_rgb)
        return img_pil
    
    def pil_to_cv2(self,image_pil):
        ''' PIL型 -> OpenCV型 '''
        new_image = np.array(image_pil, dtype=np.uint8)
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
        return new_image


    def image_to_line(self, img_cv):
        """画像を線画風に変換する関数"""
        gray_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        neiborhood24 = np.ones((5, 5), dtype=np.uint8)
        dilated = cv2.dilate(gray_img, neiborhood24, iterations=1)

        diff_img = cv2.absdiff(dilated, gray_img)
        flip_img = 255 - diff_img

        return flip_img

    def update_binary_image(self, value=None):
        """2値化画像を更新する関数"""
        if self.img_cv2_line is None:
            return

        # スライダーの値で2値化する
        threshold_value = self.threshold_slider.get()
        _, binary_img = cv2.threshold(self.img_cv2_line, threshold_value, 255, cv2.THRESH_BINARY)
        self.img_cv2_binary = binary_img

        # 2値化画像をリサイズしてラベルに表示
        img_cv2_binary_resized = self.resize_image(self.img_cv2_binary, self.display_width, self.display_height)
        img_pil_binary = self.cv2_to_pil(img_cv2_binary_resized)
        self.display_image(img_pil_binary, self.label_binary)

        # 2値化画像のオープニング処理後の画像を更新
        self.apply_opening()

    def save_line_image(self):
        """線画画像を保存する関数"""
        if self.img_cv2_line is None:
            messagebox.showerror("Error", "No line image to save.")
            return
        
        save_path = self.get_save_path()

        if save_path:
            # 線画画像を保存
            cv2.imwrite(save_path, self.img_cv2_line)
            messagebox.showinfo("Saved", f"Line image saved to {save_path}")

    def save_binary_image(self):
        """2値化画像を保存する関数"""
        if self.img_cv2_binary is None:
            messagebox.showerror("Error", "No binary image to save.")
            return
        
        save_path = self.get_save_path()

        if save_path:
            # 2値化画像を保存
            cv2.imwrite(save_path, self.img_cv2_binary)
            messagebox.showinfo("Saved", f"Binary image saved to {save_path}")

    def save_opened_line_image(self):
        """オープニング画像を保存する関数"""
        if self.img_cv2_opened_line is None:
            messagebox.showerror("Error", "No opened line image to save.")
            return
        
        save_path = self.get_save_path()

        if save_path:
            # オープニング処理後の線画画像を保存
            cv2.imwrite(save_path, self.img_cv2_opened_line)
            messagebox.showinfo("Saved", f"Opened line image saved to {save_path}")

    def save_opened_binary_image(self):
        """オープニング画像を保存する関数"""
        if self.img_cv2_opened_binary is None:
            messagebox.showerror("Error", "No opened binary image to save.")
            return
        
        save_path = self.get_save_path()

        if save_path:
            # オープニング処理後の2値化画像を保存
            cv2.imwrite(save_path, self.img_cv2_opened_binary)
            messagebox.showinfo("Saved", f"Opened binary image saved to {save_path}")


    def get_save_path(self) -> str|None:
        # 保存するファイル名と場所を指定するダイアログを開く
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        return save_path


    def on_mouse_wheel(self, event):
        """マウスホイールでスクロールする関数"""
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def view_img(self,event):
        #line_imgを表示する関数
        if self.img_cv2 is None:
            messagebox.showerror("Error", "No opened image.")
            return

        subwindow = tk.Toplevel(self.root)
        viwer = ImageViwerApp(subwindow ,self.img_cv2)
        viwer.root.mainloop()

    def view_line_img(self,event):
        #img_cv2_lineを表示する関数
        if self.img_cv2_line is None:
            messagebox.showerror("Error", "No opened image.")
            return
        
        subwindow = tk.Toplevel(self.root)
        viwer = ImageViwerApp(subwindow ,self.img_cv2_line)
        viwer.root.mainloop()

    def view_binary_img(self,event):
        #img_cv2_binaryを表示する関数
        if self.img_cv2_binary is None:
            messagebox.showerror("Error", "No opened image.")
            return
        
        subwindow = tk.Toplevel(self.root)
        viwer = ImageViwerApp(subwindow ,self.img_cv2_binary)
        viwer.root.mainloop()

    def view_opened_line_img(self,event):
        #img_cv2_opened_lineを表示する関数
        if self.img_cv2_opened_line is None:
            messagebox.showerror("Error", "No opened image.")
            return
        
        subwindow = tk.Toplevel(self.root)
        viwer = ImageViwerApp(subwindow ,self.img_cv2_opened_line)
        viwer.root.mainloop()

    def view_opened_binary_img(self,event):
        #img_cv2_opened_binaryを表示する関数
        if self.img_cv2_opened_binary is None:
            messagebox.showerror("Error", "No opened image.")
            return
        
        subwindow = tk.Toplevel(self.root)
        viwer = ImageViwerApp(subwindow ,self.img_cv2_opened_binary)
        viwer.root.mainloop()
        


# メインウィンドウを作成してアプリケーションクラスを実行
if __name__ == "__main__":
    app = ImageToLineApp()
    app.root.mainloop()
