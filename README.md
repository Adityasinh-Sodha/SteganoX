# SteganoX

SteganoX is a graphical user interface (GUI) application built using Python and Tkinter that allows you to securely hide and reveal secret messages within image files. This tool is designed with simplicity and functionality in mind, making it accessible for beginners and advanced users alike.

---
## Features

### 1. **Hide Messages in Images**
- Embed secret text messages into image files without visibly altering the image.
- Automatically resizes the image if needed to fit the entire message.
- Uses a delimiter to ensure the hidden message can be properly identified and extracted.
- Optional password protection: encrypts your message using a password to enhance security.
- Supports multiple image formats: PNG, JPEG, BMP, and GIF.

### 2. **Reveal Hidden Messages from Images**
- Extract secret messages embedded in images.
- promot user to enter password if a password was used during the hiding process.
- If user enter wrong password the revealed message is being unreadable.
- Displays the revealed message in a separate window for easy reading and copying.

### 3. **User-Friendly GUI**
- Built-in Tkinter GUI for ease of use.
- Simple layout with clear instructions for both hiding and revealing messages.

### 4. **Error Handling**
- Alerts for invalid inputs, incorrect passwords, or unsupported image formats.
- Ensures a smooth user experience by handling exceptions gracefully.

---

## Installation

### Prerequisites
- Python 3.7 or later
- Required Python libraries:
  - `Pillow`
  - `numpy`
  - `pyperclip`

### Steps
1. Clone or download this repository:
   ```bash
   git clone https://github.com/Adityasinh-Sodha/SteganoX.git
   cd SteganoX
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python stegano_gui.py
   ```


---

## Limitations
- This tool is under the development
- Password protection uses a basic XOR encryption method and may not be suitable for highly sensitive data.
- Larger messages may require resizing the image, which can result in a larger output file size.
- sometime the larger messages are not readable
- Write issue if you face any of this situations 

---


## License
This project is licensed under the [MIT License](LICENSE).



## Contributing
Feel free to fork this repository, create a new branch, and submit a pull request with your improvements or bug fixes. Contributions are always welcome!



## Author
Developed by **Adityasinh**.
