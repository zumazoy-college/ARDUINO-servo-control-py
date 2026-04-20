import serial.tools.list_ports

print("Доступные COM-порты:\n")
ports = serial.tools.list_ports.comports()

if not ports:
    print("Порты не найдены!")
else:
    for port in ports:
        print(f"  Порт: {port.device}")
        print(f"  Описание: {port.description}")
        print(f"  HWID: {port.hwid}")
        print("-" * 50)
