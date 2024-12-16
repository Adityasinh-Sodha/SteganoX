from tkinter import Tk, Label, Button, filedialog, Entry, messagebox, Toplevel, Canvas
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageOps
import numpy as np
import os
import uuid
import pyperclip
import threading
import tempfile

DELIMITER = '1111111111111110'  # Used to identify the end of the hidden message

def resize_image(img, new_size):
    """Resize the image to the specified size."""
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    return img

def calculate_new_size(img, binary_message_length):
    """Calculate the new image size to fit the binary message."""
    width, height = img.size
    channels = len(img.getbands())
    total_pixels = width * height * channels

    # Calculate the required number of pixels
    required_pixels = binary_message_length + len(DELIMITER)
    if required_pixels <= total_pixels:
        return img.size  # Current size is sufficient

    # Increase the size by calculating required width and height
    factor = (required_pixels / total_pixels) ** (1 / 2)
    new_width = max(int(width * factor), width + 1)
    new_height = max(int(height * factor), height + 1)

    return new_width, new_height

def hide_message(image_path, message, password, progress_callback):
    try:
        # Open the image
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)  # Handle rotated images

        # Encrypt the message if password is provided
        if password:
            message = ''.join(chr(ord(char) ^ ord(password[i % len(password)])) for i, char in enumerate(message))

        # Convert the message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message) + DELIMITER
        total_length = len(binary_message)  # Compute total length

        # Resize the image if necessary
        img = resize_image(img, calculate_new_size(img, len(binary_message)))

        arr = np.array(img, dtype=np.uint8)
        binary_message = iter(binary_message)

        total_pixels = arr.shape[0] * arr.shape[1] * arr.shape[2]
        processed_pixels = 0

        # Hide the binary message in the image
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                for k in range(arr.shape[2]):
                    try:
                        arr[i][j][k] = (arr[i][j][k] & ~1) | int(next(binary_message))
                        processed_pixels += 1
                        if progress_callback:
                            progress_callback(processed_pixels, total_length)
                    except StopIteration:
                        output_path = os.path.join(os.getcwd(), f"hidden_message_{uuid.uuid4().hex[:8]}.png")
                        img = Image.fromarray(arr, mode=img.mode)
                        img.save(output_path)
                        return f"Message successfully hidden! Output saved as {output_path}"

        return "Message hidden successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def reveal_message(image_path, password, progress_callback):
    try:
        # Open the image and convert it to a NumPy array
        img = Image.open(image_path)
        arr = np.array(img, dtype=np.uint8)

        binary_message = ""
        total_pixels = arr.shape[0] * arr.shape[1] * arr.shape[2]
        processed_pixels = 0

        # Extract the binary message from the image
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                for k in range(arr.shape[2]):
                    binary_message += str(arr[i][j][k] & 1)
                    processed_pixels += 1
                    if progress_callback:
                        progress_callback(processed_pixels, total_pixels)

                    # Stop if the delimiter is found
                    if binary_message.endswith(DELIMITER):
                        all_bytes = [binary_message[i:i+8] for i in range(0, len(binary_message) - len(DELIMITER), 8)]
                        decoded_message = ''.join(chr(int(byte, 2)) for byte in all_bytes)

                        # Decrypt the message if a password is provided
                        if password:
                            try:
                                decoded_message = ''.join(
                                    chr(ord(char) ^ ord(password[i % len(password)])) for i, char in enumerate(decoded_message)
                                )
                            except Exception:
                                return "Error: Incorrect password provided!"

                        return f"Hidden message: {decoded_message}"

        return "No hidden message found in the image."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def select_image_file():
    try:
        initial_dir = os.path.expanduser("~/Pictures") if os.path.exists(os.path.expanduser("~/Pictures")) else os.getcwd()
        filetypes = [
            ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
            ("PNG Files", "*.png"),
            ("JPEG Files", "*.jpg;*.jpeg"),
            ("Bitmap Files", "*.bmp"),
            ("GIF Files", "*.gif"),
            ("All Files", "*.*"),
        ]
        
        image_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select an Image File",
            filetypes=filetypes
        )
        return image_path
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while selecting the image: {e}")
        return None


def show_progress_bar(task, image_path=None, message=None, password=None):
    """Display a progress bar while the task runs."""
    progress_window = Toplevel(root)
    progress_window.title(f"{task} Progress")
    progress_window.geometry("400x100")
    Label(progress_window, text=f"{task} in Progress...", font=("Arial", 12)).pack(pady=10)

    progress_canvas = Canvas(progress_window, width=300, height=20, bg="white", highlightthickness=1, relief="solid")
    progress_canvas.pack(pady=10)

    def update_progress(processed, total):
        percentage = int((processed / total) * 100)
        progress_canvas.delete("progress")
        progress_canvas.create_rectangle(0, 0, percentage * 3, 20, fill="blue", tags="progress")
        progress_window.update()

    def perform_task():
        if task == "Hiding Message":
            result = hide_message(image_path, message, password, update_progress)
        elif task == "Revealing Message":
            result = reveal_message(image_path, password, update_progress)
        progress_window.destroy()
        if task == "Revealing Message":
            show_revealed_message(result)
        else:
            messagebox.showinfo(f"{task} Complete", result)

    threading.Thread(target=perform_task).start()

def show_revealed_message(result):
    """Display the revealed message in a new window."""
    if "Hidden message:" in result:
        hidden_message = result.replace("Hidden message: ", "")

        result_window = Toplevel(root)
        result_window.title("Revealed Message")
        result_window.geometry("500x300")

        Label(result_window, text="Revealed Message:", font=("Arial", 14)).pack(pady=10)
        text_box = ScrolledText(result_window, width=60, height=10)
        text_box.pack(pady=10)
        text_box.insert('1.0', hidden_message)
        text_box.config(state='disabled')  # Prevent editing
    else:
        messagebox.showerror("Error", result)


def hide_message_gui():
    """GUI workflow for hiding a message."""
    image_path = select_image_file()
    if not image_path:
        messagebox.showwarning("Warning", "No image selected.")
        return

    try:
        Image.open(image_path).verify()
    except Exception:
        messagebox.showerror("Error", "The selected file is not a valid image.")
        return

    message = entry_message.get()
    password = entry_password.get() or None  # Password is optional
    if not message:
        messagebox.showwarning("Warning", "Please enter a message.")
        return

    show_progress_bar("Hiding Message", image_path=image_path, message=message, password=password)

def reveal_message_gui():
    """GUI workflow for revealing a message."""
    image_path = select_image_file()
    if not image_path:
        messagebox.showwarning("Warning", "No image selected.")
        return

    try:
        Image.open(image_path).verify()
    except Exception:
        messagebox.showerror("Error", "The selected file is not a valid image.")
        return

    # Prompt the user for a password
    password_prompt = Toplevel(root)
    password_prompt.title("Enter Password")
    password_prompt.geometry("450x150")
    Label(password_prompt, text="Enter password, Leave empty if you skip password earlier, Wrong Password might affect the result").pack(pady=10)
    password_entry = Entry(password_prompt, show="*", width=25)
    password_entry.pack(pady=5)

    def submit_password():
        password = password_entry.get() or None
        password_prompt.destroy()
        show_progress_bar("Revealing Message", image_path=image_path, password=password)

    Button(password_prompt, text="Submit", command=submit_password).pack(pady=10)


# Initialize Tkinter
root = Tk()
root.title("Enhanced Image Steganography")
root.geometry("500x400")
root.resizable(False, False)

Label(root, text="Enhanced Image Steganography Tool", font=("Arial", 16)).pack(pady=10)

Label(root, text="Enter your message (for hiding):").pack(pady=5)
entry_message = Entry(root, width=50)
entry_message.pack(pady=10)

Label(root, text="Enter your password (optional):").pack(pady=5)
entry_password = Entry(root, width=50, show="*")
entry_password.pack(pady=10)

Button(root, text="Select Image and Hide Message", command=hide_message_gui).pack(pady=10)
Button(root, text="Select Image and Reveal Message", command=reveal_message_gui).pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
