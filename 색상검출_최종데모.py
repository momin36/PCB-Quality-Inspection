import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

# HSV 색상 검출 범위
def get_color_bounds(color):
    if color == 'yellow':
        return (15, 95, 90), (50, 255, 255)
    elif color == 'white':
        return (60, 0, 180), (85, 65, 255)
    elif color == 'black':
        return (100, 0, 0), (115, 108, 140)
    else:
        raise ValueError("Invalid color")

def get_roi(color):
    if color == 'yellow':
        return (120, 680, 300, 300)
    elif color == 'white':
        return (300, 15, 425, 200)
    elif color == 'black':
        return (300, 15, 425, 200)
    else:
        raise ValueError("Invalid roi")

# 이미지 처리 함수
def process_image(image_path, color):
    src = cv2.imread(image_path)

    if src is None:
        messagebox.showerror("Error", f"Unable to read the image at {image_path}.")
        return

    # 이미지 크기 조정
    scale_percent = 50
    width = int(src.shape[1] * scale_percent / 120)
    height = int(src.shape[0] * scale_percent / 120)
    dim = (width, height)
    src_resized = cv2.resize(src, dim, interpolation=cv2.INTER_AREA)

    # ROI 선택
    x, y, w, h = get_roi(color)
    cropped = src_resized[y:y + h, x:x + w]

    # HSV 변환
    cropped_hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
    lower_bound, upper_bound = get_color_bounds(color)

    # 범위에 따라 마스크 생성
    mask = cv2.inRange(cropped_hsv, lower_bound, upper_bound)
    result = cv2.bitwise_and(cropped, cropped, mask=mask)

    # 윤곽선 검출
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = 500
    object_detected = False

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            object_detected = True
            cv2.drawContours(cropped, [contour], -1, (0, 0, 255), 2)

    # 결과 출력
    if object_detected:
        messagebox.showinfo("Result", f"정상: {color} 물체가 인식되었습니다.")
    else:
        messagebox.showinfo("Result", f"불량: {color} 물체가 인식되지 않았습니다.")

    # 결과 표시
    show_image(cropped)

# 이미지를 Tkinter 창에 표시하는 함수
def show_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # BGR에서 RGB로 변환
    image = Image.fromarray(image)  # NumPy 배열을 PIL 이미지로 변환
    image = image.resize((800, 600), Image.ANTIALIAS)  # 크기 조정
    photo = ImageTk.PhotoImage(image)

    # 기존 위젯이 있으면 제거
    if hasattr(app, 'image_label'):
        app.image_label.destroy()

    app.image_label = tk.Label(app.root, image=photo)
    app.image_label.image = photo  # 이미지 참조 유지
    app.image_label.pack(pady=10)

# Tkinter GUI
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing")
        self.root.geometry("1200x800")  # 윈도우 크기 설정
        self.image_path = None

        self.select_image_button = tk.Button(root, text="이미지 선택", command=self.select_image, height=2, width=15)
        self.select_image_button.pack(pady=10)

        self.color_label = tk.Label(root, text="색상을 선택하세요:", font=("Arial", 15))
        self.color_label.pack()

        self.color_buttons_frame = tk.Frame(root)
        self.color_buttons_frame.pack(pady=5)

        self.yellow_button = tk.Button(self.color_buttons_frame, text="Yellow", bg="yellow", command=lambda: self.process_color('yellow'), height=3, width=20,font=("Arial", 15))
        self.yellow_button.grid(row=0, column=0, padx=5)

        self.white_button = tk.Button(self.color_buttons_frame, text="White", bg="white", command=lambda: self.process_color('white'), height=3, width=20,font=("Arial", 15))
        self.white_button.grid(row=0, column=1, padx=5)

        self.black_button = tk.Button(self.color_buttons_frame, text="Black", bg="black", fg="white", command=lambda: self.process_color('black'), height=3, width=20,font=("Arial", 15))
        self.black_button.grid(row=0, column=2, padx=5)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.image_path:
            messagebox.showinfo("Image Selected", f"이미지를 선택했습니다: {self.image_path}")
            self.show_selected_image()

    def show_selected_image(self):
        img = cv2.imread(self.image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR 형식이므로 RGB로 변환
        img = Image.fromarray(img)  # NumPy 배열을 PIL 이미지로 변환
        img = img.resize((800, 600), Image.ANTIALIAS)  # 크기 조정
        photo = ImageTk.PhotoImage(img)

        # 기존 위젯이 있으면 제거
        if hasattr(self, 'image_label'):
            self.image_label.destroy()

        self.image_label = tk.Label(self.root, image=photo)
        self.image_label.image = photo  # 이미지 참조 유지
        self.image_label.pack(pady=10)

    def process_color(self, color):
        if not self.image_path:
            messagebox.showerror("Error", "이미지를 먼저 선택하세요.")
            return
        process_image(self.image_path, color)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
