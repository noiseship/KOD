#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expense Tracker - приложение для отслеживания личных расходов
Автор: Харисов Камиль
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ExpenseTrackerApp:
    """Главный класс приложения Expense Tracker"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Expense Tracker - Личные расходы")
        self.root.geometry("950x650")
        self.root.resizable(True, True)
        
        # Данные
        self.expenses = []
        self.data_file = "expenses.json"
        
        # Категории
        self.categories = ["Еда", "Транспорт", "Развлечения", 
                          "Коммунальные услуги", "Одежда", 
                          "Здоровье", "Образование", "Другое"]
        
        # Загрузка данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== Панель добавления ==========
        add_frame = ttk.LabelFrame(main_frame, text="Добавление расхода", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Строка 1
        row1 = ttk.Frame(add_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Сумма (руб):", width=12).pack(side=tk.LEFT, padx=5)
        self.amount_entry = ttk.Entry(row1, width=20)
        self.amount_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Категория:", width=12).pack(side=tk.LEFT, padx=5)
        self.category_combo = ttk.Combobox(row1, values=self.categories, width=20)
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.set("Еда")
        
        # Строка 2
        row2 = ttk.Frame(add_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Дата (ГГГГ-ММ-ДД):", width=15).pack(side=tk.LEFT, padx=5)
        self.date_entry = ttk.Entry(row2, width=15)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row2, text="Добавить расход", command=self.add_expense).pack(side=tk.LEFT, padx=20)
        
        # ========== Панель фильтрации ==========
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        filter_row = ttk.Frame(filter_frame)
        filter_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_row, text="Категория:").pack(side=tk.LEFT, padx=5)
        self.filter_category = ttk.Combobox(filter_row, values=["Все"] + self.categories, width=15)
        self.filter_category.pack(side=tk.LEFT, padx=5)
        self.filter_category.set("Все")
        
        ttk.Label(filter_row, text="Дата от:").pack(side=tk.LEFT, padx=5)
        self.filter_date_from = ttk.Entry(filter_row, width=10)
        self.filter_date_from.insert(0, "2024-01-01")
        self.filter_date_from.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_row, text="Дата до:").pack(side=tk.LEFT, padx=5)
        self.filter_date_to = ttk.Entry(filter_row, width=10)
        self.filter_date_to.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.filter_date_to.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_row, text="Применить фильтр", command=self.apply_filter).pack(side=tk.LEFT, padx=10)
        ttk.Button(filter_row, text="Сбросить фильтр", command=self.reset_filter).pack(side=tk.LEFT, padx=5)
        
        # ========== Статистика ==========
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_row = ttk.Frame(stats_frame)
        stats_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(stats_row, text="Общая сумма:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.total_label = ttk.Label(stats_row, text="0 руб", font=('Arial', 12, 'bold'), foreground='green')
        self.total_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(stats_row, text="Сумма за период:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=20)
        self.period_total_label = ttk.Label(stats_row, text="0 руб", font=('Arial', 12, 'bold'), foreground='blue')
        self.period_total_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(stats_row, text="Записей:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=20)
        self.count_label = ttk.Label(stats_row, text="0", font=('Arial', 10))
        self.count_label.pack(side=tk.LEFT, padx=5)
        
        # ========== Таблица ==========
        table_frame = ttk.LabelFrame(main_frame, text="Список расходов", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Таблица
        columns = ("ID", "Дата", "Категория", "Сумма (руб)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма (руб)", text="Сумма (руб)")
        
        self.tree.column("ID", width=50)
        self.tree.column("Дата", width=120)
        self.tree.column("Категория", width=150)
        self.tree.column("Сумма (руб)", width=120)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить данные", command=self.save_data).pack(side=tk.LEFT, padx=5)
    
    def validate_input(self, amount, date_str):
        """Валидация входных данных"""
        # Проверка суммы
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return False, "Сумма должна быть положительным числом"
            if amount_float > 10000000:
                return False, "Сумма слишком большая"
        except ValueError:
            return False, "Сумма должна быть числом"
        
        # Проверка даты
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return False, "Неверный формат даты. Используйте ГГГГ-ММ-ДД"
        
        return True, amount_float
    
    def add_expense(self):
        """Добавление нового расхода"""
        amount = self.amount_entry.get().strip()
        category = self.category_combo.get()
        date = self.date_entry.get().strip()
        
        # Валидация
        is_valid, result = self.validate_input(amount, date)
        if not is_valid:
            messagebox.showerror("Ошибка ввода", result)
            return
        
        amount_float = result
        
        # ID
        if self.expenses:
            expense_id = max(e['id'] for e in self.expenses) + 1
        else:
            expense_id = 1
        
        # Добавление
        self.expenses.append({
            'id': expense_id,
            'amount': amount_float,
            'category': category,
            'date': date
        })
        
        # Очистка
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("Еда")
        
        # Сохранение
        self.save_data()
        self.refresh_table()
        
        messagebox.showinfo("Успех", f"Расход {amount_float:.2f} руб добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления")
            return
        
        item = self.tree.item(selected[0])
        expense_id = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить этот расход?"):
            self.expenses = [e for e in self.expenses if e['id'] != expense_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Расход удален")
    
    def apply_filter(self):
        """Применение фильтрации"""
        self.refresh_table()
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.filter_category.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_from.insert(0, "2024-01-01")
        self.filter_date_to.delete(0, tk.END)
        self.filter_date_to.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.refresh_table()
    
    def get_filtered_expenses(self):
        """Получение расходов с учётом фильтрации"""
        filtered = self.expenses.copy()
        
        # Фильтр по категории
        category_filter = self.filter_category.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e['category'] == category_filter]
        
        # Фильтр по дате
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()
        
        if date_from:
            filtered = [e for e in filtered if e['date'] >= date_from]
        if date_to:
            filtered = [e for e in filtered if e['date'] <= date_to]
        
        return filtered
    
    def refresh_table(self):
        """Обновление таблицы и статистики"""
        # Очистка
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение данных
        filtered = self.get_filtered_expenses()
        filtered.sort(key=lambda x: x['date'], reverse=True)
        
        # Заполнение
        for expense in filtered:
            self.tree.insert("", tk.END, values=(
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}"
            ))
        
        # Статистика
        total = sum(e['amount'] for e in self.expenses)
        period_total = sum(e['amount'] for e in filtered)
        count = len(filtered)
        
        self.total_label.config(text=f"{total:.2f} руб")
        self.period_total_label.config(text=f"{period_total:.2f} руб")
        self.count_label.config(text=str(count))
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []
    
    def save_data(self):
        """Сохранение данных в JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Успех", "Данные сохранены!")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


# Запуск
if __name__ == "__main__":
    print("Запуск Expense Tracker...")
    app = ExpenseTrackerApp()
    app.run()