"""
ИНСТРУКЦИЯ ПО НАСТРОЙКЕ com0com:

1. Скачайте com0com:
   https://sourceforge.net/projects/com0com/files/com0com/3.0.0.0/
   Файл: com0com-3.0.0.0-i386-and-x64-signed.zip

2. Установите com0com:
   - Распакуйте архив
   - Запустите setup.exe от имени администратора
   - Следуйте инструкциям установщика

3. Настройте пару портов:
   - Откройте "Setup Command Prompt" (из меню Пуск → com0com)
   - Выполните команду для просмотра портов:
     list

   - Вы увидите что-то вроде:
     CNCA0 PortName=COM3
     CNCB0 PortName=COM4

   - Если портов нет, создайте пару:
     install PortName=COM3 PortName=COM4

4. Запустите эмулятор:
   - В этом файле укажите один порт (например COM4)
   - В servo_control.py выберите парный порт (COM3)

5. Проверка:
   - Запустите: python check_ports.py
   - Запустите: python arduino_emulator.py
   - Запустите: python servo_control.py
   - В GUI выберите COM3 и нажмите "Подключить"

6. Если не работает или нет портов (файл check_ports):
   - Включите тестовый режим
     bcdedit /set testsigning on
   - Возможно нужно будет отключить Secure Boot в BIOS
   - Перезагрузите компьютер (shutdown /r /t 0)
   - Отключить тестовый режим
     bcdedit /set testsigning off
     shutdown /r /t 0
"""

import serial
import time

# НАСТРОЙТЕ ЗДЕСЬ: укажите один из портов пары com0com
PORT = "COM8"  # Используем COM8 (парный к COM7)
BAUDRATE = 9600

print("=" * 60)
print("ЭМУЛЯТОР ARDUINO ДЛЯ СЕРВОПРИВОДА")
print("=" * 60)
print(f"\nПопытка открыть порт: {PORT}")
print("Если ошибка - проверьте настройку com0com (см. инструкцию в коде)\n")

try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    print(f"✓ Порт {PORT} успешно открыт")
    time.sleep(2)

    ser.write("Arduino ready\n".encode('utf-8'))
    print("✓ Эмулятор готов к работе")
    print("\nТеперь запустите servo_control.py и подключитесь к парному порту")
    print("Ожидание команд...\n")
    print("-" * 60)

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            if data:
                try:
                    angle = int(data)
                    if 0 <= angle <= 180:
                        response = f"Angle set: {angle}\n"
                        ser.write(response.encode())
                        print(f"[{time.strftime('%H:%M:%S')}] Получено: {angle}° → Ответ отправлен")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] ⚠ Неверный угол: {angle}")
                except ValueError:
                    print(f"[{time.strftime('%H:%M:%S')}] ⚠ Неверные данные: {data}")

except serial.SerialException as e:
    print(f"\n✗ ОШИБКА: {e}")
    print("\nВозможные причины:")
    print("  1. Порт не существует - проверьте настройку com0com")
    print("  2. Порт занят другой программой")
    print("  3. com0com не установлен")
    print("\nДля установки com0com см. инструкцию в начале этого файла")
except KeyboardInterrupt:
    print("\n\n" + "=" * 60)
    print("Эмулятор остановлен пользователем")
    print("=" * 60)
finally:
    if 'ser' in locals():
        ser.close()
        print("Порт закрыт")
