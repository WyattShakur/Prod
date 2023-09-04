import tkinter as tk
import mysql.connector
from tkinter import messagebox
from ttkthemes import ThemedTk
from tkhtmlview import HTMLLabel
from tkinter import ttk
import requests
from datetime import datetime
import os
from tkcalendar import Calendar
import re
import threading
import time
import os
import sys
from datetime import datetime

# Создаем папку для логов, если её нет
log_folder = "logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Получаем текущую дату и время
current_datetime = datetime.now()
log_filename = f"logfile_{current_datetime.strftime('%d_%m_%Y_%H_%M_%S')}.txt"

# Полный путь к лог-файлу
log_filepath = os.path.join(log_folder, log_filename)

# Открываем лог файл для записи
class LogToFile:
    def __init__(self, log_filename):
        self.log_filename = log_filename
        self.original_stdout = sys.stdout

    def __enter__(self):
        self.log_file = open(self.log_filename, "w")
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.original_stdout
        if self.log_file:
            self.log_file.close()

    def write(self, text):
        self.original_stdout.write(text)
        self.log_file.write(text)
        self.log_file.flush()

# Функция для записи в лог-файл
def log(message):
    current_time = datetime.now().strftime("[%H:%M:%S]")
    formatted_message = f"{current_time} {message}"
    with open(log_filepath, "a") as log_file:
        log_file.write(formatted_message + "\n")    
        print = log
        print(formatted_message)
# Используем контекстный менеджер для перенаправления вывода print в файл
with LogToFile(log_filepath):
    print("Это сообщение будет записано в лог файл.")
    log("Еще одно сообщение для лога.")
#--------------------------------------------- Начало Зоны Баз Данных -----------------------------------------------------
# Подключение к базе данных MySQL
conn = mysql.connector.connect(
    host="85.10.205.173",
    user="kubg_diplom",
    password="yyEvOmhV",
    database="kubg_diplom"
)
cursor = conn.cursor()

# Создание таблицы для мониторинга входа
create_table_query = """
CREATE TABLE IF NOT EXISTS login_monitoring (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20),
    ip_address VARCHAR(15),
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
cursor.execute(create_table_query)

# Создание таблицы для IP-адресов пользователей
create_ip_table_query = """
CREATE TABLE IF NOT EXISTS ip_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(15),
    country VARCHAR(50),
    city VARCHAR(50),
    success VARCHAR(15),
    username VARCHAR(20),
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
cursor.execute(create_ip_table_query)

# Создание таблицы для заметок
create_notes_table_query = """
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20),
    note_date DATE,
    note_text TEXT
)
"""
cursor.execute(create_notes_table_query)

# Создание таблицы Grafik Zaniatiy
create_grafik_table_query = """
CREATE TABLE IF NOT EXISTS `Grafik Zaniatiy` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    day_of_week VARCHAR(20),
    class VARCHAR(10),
    lesson_name VARCHAR(100),
    lesson_number INT,
    lesson_type VARCHAR(20),
    username VARCHAR(20)
)
"""
cursor.execute(create_grafik_table_query)
#--------------------------------- Конец Зоны Баз Данных -----------------------------------------------------
def center_window(window):
    # Получение размеров экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Расчет координат верхнего левого угла окна для центрирования
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # Установка новых координат окна
    window.geometry(f"+{x}+{y}")


def validate_login():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Ошибка", "Введите логин и пароль")
    elif len(username) < 3 or len(username) > 20:
        messagebox.showerror("Ошибка", "Длина логина должна быть от 3 до 20 символов")
    elif len(password) < 3 or len(password) > 20:
        messagebox.showerror("Ошибка", "Длина пароля должна быть от 3 до 20 символов")
    else:
        login(username)


def login(username):
    password = password_entry.get()

    # Проверка соответствия введенных логина и пароля в базе данных
    query = "SELECT * FROM users WHERE user=%s AND pass=%s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        # Получение глобального IP-адреса
        ip_address = get_global_ip_address()
        if ip_address:
            # Запись информации о входе в таблицу login_monitoring
            insert_query = "INSERT INTO login_monitoring (username, ip_address) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, ip_address))
            conn.commit()
            # Запись информации о IP-адресе в таблицу ip_addresses
            country, city = get_ip_location(ip_address)
            success = "Access Approved"
            insert_ip_query = "INSERT INTO ip_addresses (username, ip_address, country, city, success) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_ip_query, (username, ip_address, country, city, success))
            conn.commit()
            messagebox.showinfo("Успех", "Вход выполнен")
            # Создание папки для пользователя
            create_user_folder(username)
            # Закрытие текущего окна
            window.destroy()
            main_window(username)  # Передача имени пользователя в main_window()
        else:
            messagebox.showerror("Ошибка", "Не удалось получить глобальный IP-адрес")
    else:
        # Получение глобального IP-адреса
        ip_address = get_global_ip_address()
        if ip_address:
            # Запись информации о неудачной попытке входа в таблицу login_monitoring
            insert_query = "INSERT INTO login_monitoring (username, ip_address) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, ip_address))
            conn.commit()
            # Запись информации о IP-адресе в таблицу ip_addresses
            country, city = get_ip_location(ip_address)
            success = "Access Denied"
            insert_ip_query = "INSERT INTO ip_addresses (username, ip_address, country, city, success) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_ip_query, (username, ip_address, country, city, success))
            conn.commit()
        messagebox.showerror("Ошибка", "Неверный логин или пароль")


def get_global_ip_address():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        data = response.json()
        ip_address = data.get("ip")
        return ip_address
    except requests.RequestException:
        return None


def get_ip_location(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        country = data.get("country")
        city = data.get("city")
        return country, city
    except requests.RequestException:
        return None, None


def button_clicked(button_name, username):
    if button_name == "Заметки":
        open_notes_window(username)
    elif button_name == "Мой график занятий":
        open_grafik_window(username)
    else:
        print(f"Кликнута кнопка {button_name}")


def open_calendar(username):
    # Создание нового окна для календаря
    calendar_window = ThemedTk(theme="equilux")  # Используем ThemedTk для единообразной темы окна
    calendar_window.title("Календарь")

    # Запрет изменения размеров окна пользователем
    calendar_window.resizable(False, False)  # Окно не может изменяться
   
    # Создание виджета календаря
    cal = Calendar(calendar_window, selectmode='day', date_pattern='dd.MM.yyyy')
    cal.pack(pady=20)
    

def open_notes_window(username):
    notes_window = ThemedTk(theme="equilux")
    notes_window.title("Заметки")
    
    def add_note():
        # Функция для добавления заметки
        date = selected_date_label["text"]
        note_text = note_entry.get("1.0", "end-1c")
        
        # Проверка, что заметка не пуста
        if not note_text.strip():
            messagebox.showerror("Ошибка", "Нельзя добавить пустую заметку.")
            return
        
         # Изменение формата даты
        date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        
        insert_note_query = "INSERT INTO notes (username, note_date, note_text) VALUES (%s, %s, %s)"
        cursor.execute(insert_note_query, (username, date, note_text))
        conn.commit()
        update_notes_list()  # Обновить список заметок после добавления
        messagebox.showinfo("Успех", "Заметка сохранена")

    
    def delete_note():
        # Функция для удаления заметки
        selected_note = notes_listbox.curselection()
        if selected_note:
            note_id = notes_list[selected_note[0]][0]
            delete_note_query = "DELETE FROM notes WHERE id = %s"
            cursor.execute(delete_note_query, (note_id,))
            conn.commit()
            update_notes_list()  # Обновить список заметок после удаления
            messagebox.showinfo("Успех", "Заметка удалена")

    def update_notes_list():
        # Функция для обновления списка заметок в окне
        notes_listbox.delete(0, "end")
        select_notes_query = "SELECT id, note_date, note_text FROM notes WHERE username = %s"
        cursor.execute(select_notes_query, (username,))
        global notes_list
        notes_list = cursor.fetchall()
        for note in notes_list:
            date = note[1].strftime("%d.%m.%Y")
            note_text = note[2]
            notes_listbox.insert("end", f"{date}: {note_text}")

    selected_date_label = tk.Label(notes_window, text="", font=("Times New Roman", 12))
    selected_date_label.pack(pady=10)

    warning_date_label = tk.Label(notes_window, text="Не забудьте нажать на число на которое вам нужна заметка", font=("Times New Roman", 12))
    warning_date_label.pack(pady=10)

    cal = Calendar(notes_window, selectmode='day', date_pattern='dd.MM.yyyy')
    cal.pack(pady=10)

    note_label = tk.Label(notes_window, text="Заметка:", font=("Times New Roman", 12))
    note_label.pack(pady=10)

    note_entry = tk.Text(notes_window, height=5, width=30)
    note_entry.pack(pady=10)

    add_button = ttk.Button(notes_window, text="Добавить заметку", command=add_note)
    add_button.pack(pady=5)

    notes_listbox = tk.Listbox(notes_window, width=40, height=10)
    notes_listbox.pack(pady=10)

    delete_button = ttk.Button(notes_window, text="Удалить заметку", command=delete_note)
    delete_button.pack(pady=5)

    update_notes_list()  # При открытии окна обновить список заметок

    def on_date_selected():
        selected_date = cal.get_date()
        selected_date_label.config(text=selected_date)

    cal.bind("<<CalendarSelected>>", lambda event: on_date_selected())

    notes_window.mainloop()
#----------------------------------------------------------------

#----------------------------------------------------------------
def open_grafik_window(username):
    grafik_window = ThemedTk(theme="equilux")
    grafik_window.title("Мой график занятий")

    # Уберем параметр username, так как он передается извне
    def update_lessons_list():
        lessons_listbox.delete(0, "end")
        select_lessons_query = "SELECT id, date, day_of_week, class, lesson_name, lesson_number, lesson_type FROM `Grafik Zaniatiy` WHERE username = %s ORDER BY date, lesson_number"
        cursor.execute(select_lessons_query, (username,))
        
        # Добавляем занятия из базы данных в список в интерфейсе
        for lesson in cursor.fetchall():
            date = lesson[1].strftime("%d.%m.%Y")
            day_of_week = lesson[2]
            class_name = lesson[3]
            lesson_name = lesson[4]
            lesson_number = lesson[5]
            lesson_type = lesson[6]
            lessons_listbox.insert("end", f"{date}, {day_of_week}, Класс: {class_name}, Урок: {lesson_name}, Урок №{lesson_number}, Тип: {lesson_type}")

    def refresh_lessons_list():
        update_lessons_list()
        # Запускаем функцию обновления списка через 10 секунд (или другой интервал, по вашему выбору)
        grafik_window.after(100, refresh_lessons_list)    
    def add_new_lesson(username, date, day_of_week, class_name, lesson_name, lesson_number, lesson_type):
        insert_query = "INSERT INTO `Grafik Zaniatiy` (username, date, day_of_week, class, lesson_name, lesson_number, lesson_type) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (username, date, day_of_week, class_name, lesson_name, lesson_number, lesson_type))
        conn.commit()
        update_lessons_list()

    def on_add_lesson():
        date = selected_date_label["text"]
        day_of_week = day_of_week_label["text"]
        class_name = class_name_entry.get()
        lesson_name = lesson_name_entry.get()
        lesson_number = lesson_number_combobox.get()  # Используйте .get(), чтобы получить выбранное значение
        lesson_type = lesson_type_combobox.get()      # Используйте .get(), чтобы получить выбранное значение

        if not class_name or not lesson_name or not lesson_number or not lesson_type:
            messagebox.showerror("Ошибка", "Заполните все поля для добавления занятия. Обратитесь к системному администратору t.me/andrey_joks")
            return

        add_new_lesson(username, date, day_of_week, class_name, lesson_name, lesson_number, lesson_type)
        update_lessons_list()
        messagebox.showinfo("Успех", "Занятие добавлено успешно.")

    def on_delete_lesson():
        selected_lesson = lessons_listbox.curselection()
        if selected_lesson:
            lesson_id = lessons_list[selected_lesson[0]][0]
            delete_lesson(lesson_id)
            update_lessons_list()
            messagebox.showinfo("Успех", "Занятие удалено успешно.")

    def delete_lesson(lesson_id):
            delete_query = "DELETE FROM `Grafik Zaniatiy` WHERE id = %s"
            cursor.execute(delete_query, (lesson_id,))
            conn.commit()
            update_lessons_list()
    def update():
         lessons_listbox.delete(0, "end")
         update_lessons_list()
         messagebox.showinfo("Успех","Функция работает.")

    def update_lessons_list():
        lessons_listbox.delete(0, "end")
        select_lessons_query = "SELECT id, date, day_of_week, class, lesson_name, lesson_number, lesson_type FROM `Grafik Zaniatiy` WHERE username = %s ORDER BY date, lesson_number"
        cursor.execute(select_lessons_query, (username,))
        global lessons_list
        lessons_list = cursor.fetchall()
        for lesson in lessons_list:
            date = lesson[1].strftime("%d.%m.%Y")
            day_of_week = lesson[2]
            class_name = lesson[3]
            lesson_name = lesson[4]
            lesson_number = lesson[5]
            lesson_type = lesson[6]
            lessons_listbox.insert("end", f"{date}, {day_of_week}, Класс: {class_name}, Урок: {lesson_name}, Урок №{lesson_number}, Тип: {lesson_type}")

    def on_date_selected():
        selected_date = cal.get_date()
        selected_date_label.config(text=selected_date)
        day_of_week = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%A")
        day_of_week_label.config(text=day_of_week)


    grafik_frame = ttk.Frame(grafik_window)
    grafik_frame.pack(pady=20)

    cal = Calendar(grafik_frame, selectmode='day', date_pattern='yyyy-MM-dd')
    cal.grid(row=0, column=0, columnspan=3, padx=10)

    select_date_button = ttk.Button(grafik_frame, text="Выбрать дату", command=on_date_selected)
    select_date_button.grid(row=1, column=0, columnspan=3, pady=5)

    selected_date_label = tk.Label(grafik_frame, text="", font=("Times New Roman", 12))
    selected_date_label.grid(row=2, column=0, columnspan=3)

    day_of_week_label = tk.Label(grafik_frame, text="", font=("Times New Roman", 12))
    day_of_week_label.grid(row=3, column=0, columnspan=3, pady=5)

    warning_date_label = tk.Label(grafik_frame, text="Не забудьте нажать на число на которое вам нужна заметка", font=("Times New Roman", 12))
    warning_date_label.grid(row=11, column=0, columnspan=3, pady=10)


    class_name_label = tk.Label(grafik_frame, text="Класс:", font=("Times New Roman", 12))
    class_name_label.grid(row=4, column=0, padx=5)

    class_name_entry = tk.Entry(grafik_frame)
    class_name_entry.grid(row=4, column=1, padx=5)

    lesson_name_label = tk.Label(grafik_frame, text="Название урока:", font=("Times New Roman", 12))
    lesson_name_label.grid(row=5, column=0, padx=5)

    lesson_name_entry = tk.Entry(grafik_frame)
    lesson_name_entry.grid(row=5, column=1, padx=5)

    lesson_number_label = tk.Label(grafik_frame, text="Номер урока:", font=("Times New Roman", 12))
    lesson_number_label.grid(row=6, column=0, padx=5)

    lesson_number_var = tk.IntVar()
    lesson_number_combobox = ttk.Combobox(grafik_frame, textvariable=lesson_number_var, values=list(range(1, 11)), state="readonly")
    lesson_number_combobox.grid(row=6, column=1, padx=5)

    lesson_type_label = tk.Label(grafik_frame, text="Тип урока:", font=("Times New Roman", 12))
    lesson_type_label.grid(row=7, column=0, padx=5)

    lesson_type_var = tk.StringVar()
    lesson_type_combobox = ttk.Combobox(grafik_frame, textvariable=lesson_type_var, values=["обычный", "проверка", "факультатив", "открытый урок"], state="readonly")
    lesson_type_combobox.grid(row=7, column=1, padx=5)

    add_lesson_button = ttk.Button(grafik_frame, text="Добавить занятие", command=on_add_lesson)
    add_lesson_button.grid(row=8, column=0, columnspan=2, pady=10)

    lessons_listbox = tk.Listbox(grafik_frame, width=60, height=10)
    lessons_listbox.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

    delete_lesson_button = ttk.Button(grafik_frame, text="Удалить занятие", command=on_delete_lesson)
    delete_lesson_button.grid(row=10, column=1, columnspan=2, pady=5)  # Изменил координаты для кнопки "Удалить занятие"

    update_lesson_button = ttk.Button(grafik_frame, text="Обновить", command=update)
    update_lesson_button.grid(row=10, column=0, pady=10)  # Разместил кнопку "Обновить" отдельно

    update_lessons_list()
    refresh_lessons_list()  # Запускаем обновление списка занятий в реальном времени

    grafik_window.mainloop()


def main_window(username):
    # Создание нового окна для приветствия
    welcome_window = ThemedTk(theme="equilux")

    # Задание размеров окна
    welcome_window.geometry("950x500")

    # Запрет изменения размеров окна пользователем
    welcome_window.resizable(False, False)

    # Центрирование окна при открытии
    center_window(welcome_window)

    # Задание названия программы
    welcome_window.title("Ассистент вчителя информатики")

    # Вывод приветственной информации
    welcome_label = tk.Label(welcome_window, text="Ассистент вчителя информатики", font=("Times New Roman", 16))
    welcome_label.pack()

    welcome_username_label = tk.Label(welcome_window, text="Добро пожаловать, " + username, font=("Times New Roman", 12))
    welcome_username_label.pack(anchor=tk.NE)

    # Создание и размещение фрейма для кнопок 1 и 2
    button_frame1 = tk.Frame(welcome_window)
    button_frame1.pack(pady=10)

    # Кнопка с календарем
    calendar_button = ttk.Button(button_frame1, text="Календарь", width=30, command=lambda: open_calendar(username))
    calendar_button.pack(side=tk.LEFT, padx=5)
    # Кнопка для открытия окна с графиком занятий
    #grafik_button = ttk.Button(button_frame1, text="Мой график занятий", width=30, command=lambda: open_grafik_window(username))
    #grafik_button.pack(side=tk.LEFT, padx=5)

       # Остальные кнопки
    button_names = ["Заметки", "Мой график занятий"]
    for name in button_names:
        button = ttk.Button(button_frame1, text=name, width=30, command=lambda n=name: button_clicked(n, username))
        button.pack(side=tk.LEFT, padx=5)

    # Создание и размещение фрейма для кнопок 3, 4, 5, 6
    button_frame2 = tk.Frame(welcome_window)
    button_frame2.pack(pady=10)

    button_names2 = ["Урок(открытие файлов)", "Электронный журнал", "Облако"]
    for name in button_names2:
        button = ttk.Button(button_frame2, text=name, width=30, command=lambda n=name: button_clicked(n, username))
        button.pack(side=tk.LEFT, padx=5)

    # Запуск главного цикла обработки событий нового окна
    welcome_window.mainloop()



def create_user_folder(username):
    parent_folder = "Users"
    folder_path = os.path.join(parent_folder, username)

    try:
        os.makedirs(folder_path)
        print(f"Создана папка для пользователя: {folder_path}")
    except FileExistsError:
        print(f"Папка для пользователя уже существует: {folder_path}")


# Создание окна
window = tk.Tk()

# Задание размеров окна
window.geometry("600x600")  # Ширина: 600 пикселей, Высота: 500 пикселей

# Запрет изменения размеров окна пользователем
window.resizable(False, False)  # Окно не может изменяться

# Задание названия программы
window.title("Моя программа")

# Создание и размещение элементов на окне
username_default_text = "Введите логин"
username_label = tk.Label(window, text="Логин")
username_label.pack()

username_entry = tk.Entry(window)
username_entry.pack()

password_label = tk.Label(window, text="Пароль")
password_default_text = "Введите пароль"
password_label.pack()

password_entry = tk.Entry(window, show="*")
password_entry.pack()

login_button = tk.Button(window, text="Войти", command=validate_login)
login_button.pack()

# Закрытие соединения с базой данных после закрытия окна
def on_closing():
    cursor.close()
    conn.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

# Центрирование окна при открытии
center_window(window)

# Запуск главного цикла обработки событий
window.mainloop()