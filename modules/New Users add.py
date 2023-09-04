import mysql.connector
import time

try:
    # Устанавливаем соединение с базой данных
    conn = mysql.connector.connect(
        host="85.10.205.173",
        user="kubg_diplom",
        password="yyEvOmhV",
        database="kubg_diplom"
    )

    if conn.is_connected():
        print("Соединение установлено")
        c = conn.cursor()

        # Ввод данных с клавиатуры
        username = input("Введите логин: ")
        password = input("Введите пароль: ")

        # Выполнение SQL-запроса для добавления данных
        c.execute("INSERT INTO users (user, pass) VALUES (%s, %s)", (username, password))
        print("Данные добавлены")
        conn.commit()
        print("Данные сохранены")

        c.close()
        conn.close()
        print("Соединение закрыто")
        time.sleep(10)
    else:
        print("Ошибка при установлении соединения")
        conn.close()
        print("Соединение закрыто")
        time.sleep(10)
        exit()

except mysql.connector.Error as e:
    print(f"Ошибка при работе с базой данных: {e}")



