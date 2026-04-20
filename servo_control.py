import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
from datetime import datetime
import threading


class ServoControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление сервоприводом Arduino")
        self.root.geometry("600x500")

        self.serial_connection = None
        self.is_connected = False

        self.create_widgets()
        self.update_ports()

    def create_widgets(self):
        # Секция подключения
        connection_frame = ttk.LabelFrame(self.root, text="Подключение к Arduino", padding=10)
        connection_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(connection_frame, text="COM-порт:").grid(row=0, column=0, sticky="w", padx=5)
        self.port_combo = ttk.Combobox(connection_frame, width=15, state="readonly")
        self.port_combo.grid(row=0, column=1, padx=5)

        self.connect_btn = ttk.Button(connection_frame, text="Подключить", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=2, padx=5)

        ttk.Button(connection_frame, text="Обновить", command=self.update_ports).grid(row=0, column=3, padx=5)

        self.status_label = ttk.Label(connection_frame, text="● Отключено", foreground="red")
        self.status_label.grid(row=0, column=4, padx=10)

        # Секция управления сервоприводом
        control_frame = ttk.LabelFrame(self.root, text="Управление сервоприводом", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        self.angle_var = tk.IntVar(value=90)
        self.angle_label = ttk.Label(control_frame, text="Угол: 90°", font=("Arial", 12, "bold"))
        self.angle_label.pack(pady=5)

        self.slider = ttk.Scale(control_frame, from_=0, to=180, orient="horizontal",
                                variable=self.angle_var, command=self.on_slider_change)
        self.slider.pack(fill="x", padx=20, pady=5)

        # Кнопки быстрого выбора
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(pady=10)

        angles = [0, 45, 90, 180]
        for angle in angles:
            ttk.Button(buttons_frame, text=f"{angle}°", width=8,
                      command=lambda a=angle: self.set_angle(a)).pack(side="left", padx=5)

        # Терминал логов
        log_frame = ttk.LabelFrame(self.root, text="Терминал логов", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled",
                                                   font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)

    def update_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)
            self.log(f"Найдено портов: {len(ports)}")
        else:
            self.log("COM-порты не найдены")

    def toggle_connection(self):
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()

    def connect(self):
        port = self.port_combo.get()
        if not port:
            self.log("Ошибка: выберите COM-порт", "error")
            return

        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            self.is_connected = True
            self.status_label.config(text="● Подключено", foreground="green")
            self.connect_btn.config(text="Отключить")
            self.port_combo.config(state="disabled")
            self.log(f"Подключено к {port}", "success")

            # Запуск потока чтения
            threading.Thread(target=self.read_serial, daemon=True).start()

        except serial.SerialException as e:
            self.log(f"Ошибка подключения: {e}", "error")

    def disconnect(self):
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None

        self.is_connected = False
        self.status_label.config(text="● Отключено", foreground="red")
        self.connect_btn.config(text="Подключить")
        self.port_combo.config(state="readonly")
        self.log("Отключено от Arduino", "info")

    def on_slider_change(self, value):
        angle = int(float(value))
        self.angle_label.config(text=f"Угол: {angle}°")
        self.send_angle(angle)

    def set_angle(self, angle):
        self.angle_var.set(angle)
        self.angle_label.config(text=f"Угол: {angle}°")
        self.send_angle(angle)

    def send_angle(self, angle):
        if not self.is_connected:
            self.log("Ошибка: не подключено к Arduino", "error")
            return

        try:
            command = f"{angle}\n"
            self.serial_connection.write(command.encode())
            self.log(f"→ Отправлено: {angle}°", "send")
        except Exception as e:
            self.log(f"Ошибка отправки: {e}", "error")

    def read_serial(self):
        while self.is_connected and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    response = self.serial_connection.readline().decode().strip()
                    if response:
                        self.log(f"← Получено: {response}", "receive")
            except Exception as e:
                self.log(f"Ошибка чтения: {e}", "error")
                break

    def log(self, message, msg_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")

        colors = {
            "info": "black",
            "success": "green",
            "error": "red",
            "send": "blue",
            "receive": "purple"
        }

        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")

        # Подсветка последней строки
        line_start = self.log_text.index("end-2c linestart")
        line_end = self.log_text.index("end-1c")
        tag_name = f"tag_{msg_type}"
        self.log_text.tag_add(tag_name, line_start, line_end)
        self.log_text.tag_config(tag_name, foreground=colors.get(msg_type, "black"))

        self.log_text.see("end")
        self.log_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServoControlApp(root)
    root.mainloop()
