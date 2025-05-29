# HIT137 - Assignment 3 - Question 1: Image Editor
# Developed using Tkinter for GUI, OpenCV for image processing, and PIL for rendering

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor - HIT137")

        # Variables
        self.image = None
        self.original_image = None
        self.tk_image = None
        self.crop_rect = None
        self.start_x = self.start_y = 0
        self.undo_stack = []
        self.redo_stack = []

        # GUI layout
        self.canvas = tk.Canvas(root, width=600, height=400, bg="lightgray")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        tk.Button(control_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=5)

        self.slider = ttk.Scale(root, from_=0.1, to=2.0, orient="horizontal", command=self.resize_image)
        self.slider.set(1.0)
        self.slider.pack(fill='x', padx=20, pady=10)

        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.image = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
            self.original_image = self.image.copy()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.display_image(self.image)

    def display_image(self, img):
        img_pil = Image.fromarray(img)
        img_resized = img_pil.resize((600, 400))
        self.tk_image = ImageTk.PhotoImage(img_resized)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def start_crop(self, event):
        self.start_x, self.start_y = event.x, event.y

    def draw_crop(self, event):
        self.canvas.delete("crop_rect")
        self.crop_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red", tag="crop_rect"
        )

    def end_crop(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        ratio_x = self.image.shape[1] / 600
        ratio_y = self.image.shape[0] / 400
        x1 = int(x1 * ratio_x)
        x2 = int(x2 * ratio_x)
        y1 = int(y1 * ratio_y)
        y2 = int(y2 * ratio_y)

        cropped = self.image[y1:y2, x1:x2]
        if cropped.size > 0:
            self.push_undo(self.image)
            self.image = cropped
            self.display_image(self.image)

    def resize_image(self, value):
        if self.image is not None:
            scale = float(value)
            new_size = (int(self.image.shape[1] * scale), int(self.image.shape[0] * scale))
            resized = cv2.resize(self.image, new_size)
            self.display_image(resized)

    def save_image(self):
        if self.image is not None:
            path = filedialog.asksaveasfilename(defaultextension=".png")
            if path:
                cv2.imwrite(path, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Success", "Image saved successfully.")

    def push_undo(self, state):
        self.undo_stack.append(state.copy())
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.display_image(self.image)

    def redo(self):
        if self.redo_stack:
            self.push_undo(self.image)
            self.image = self.redo_stack.pop()
            self.display_image(self.image)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
