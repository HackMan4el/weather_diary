"""
weather_diary.py — GUI application for Weather Diary.
Requires Python 3.10+ with tkinter (standard library).

Run: python weather_diary.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from logic import (
    load_records, save_records,
    validate_date, validate_temperature,
    filter_records,
)


class WeatherDiaryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Weather Diary — Дневник Погоды")
        self.root.resizable(False, False)

        self.records: list[dict] = load_records()

        self._build_input_frame()
        self._build_filter_frame()
        self._build_table_frame()
        self._build_status_bar()

        self.refresh_table(self.records)

    def _build_input_frame(self) -> None:
        frame = ttk.LabelFrame(self.root, text="Новая запись", padding=10)
        frame.grid(row=0, column=0, padx=10, pady=8, sticky="ew")

        ttk.Label(frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.entry_date = ttk.Entry(frame, width=14)
        self.entry_date.grid(row=0, column=1, padx=(4, 16))
        self.entry_date.insert(0, datetime.today().strftime("%d.%m.%Y"))

        ttk.Label(frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.entry_temp = ttk.Entry(frame, width=8)
        self.entry_temp.grid(row=0, column=3, padx=(4, 16))

        ttk.Label(frame, text="Осадки:").grid(row=0, column=4, sticky="w")
        self.precip_var = tk.StringVar(value="Нет")
        cb = ttk.Combobox(
            frame, textvariable=self.precip_var,
            values=["Нет", "Да"], width=6, state="readonly",
        )
        cb.grid(row=0, column=5, padx=(4, 16))

        ttk.Label(frame, text="Описание:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.entry_desc = ttk.Entry(frame, width=60)
        self.entry_desc.grid(row=1, column=1, columnspan=4, padx=(4, 16), pady=(6, 0), sticky="ew")

        ttk.Button(frame, text="+ Добавить запись", command=self.add_record).grid(
            row=1, column=5, padx=(4, 0), pady=(6, 0)
        )

    def _build_filter_frame(self) -> None:
        frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        frame.grid(row=1, column=0, padx=10, pady=4, sticky="ew")

        ttk.Label(frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.filter_date = ttk.Entry(frame, width=14)
        self.filter_date.grid(row=0, column=1, padx=(4, 16))

        ttk.Label(frame, text="Температура выше (°C):").grid(row=0, column=2, sticky="w")
        self.filter_temp = ttk.Entry(frame, width=8)
        self.filter_temp.grid(row=0, column=3, padx=(4, 16))

        ttk.Button(frame, text="Применить фильтр", command=self.apply_filter).grid(
            row=0, column=4, padx=(0, 6)
        )
        ttk.Button(frame, text="Сбросить", command=self.reset_filter).grid(
            row=0, column=5
        )

    def _build_table_frame(self) -> None:
        frame = ttk.Frame(self.root, padding=(10, 4, 10, 4))
        frame.grid(row=2, column=0, sticky="nsew")

        columns = ("date", "temp", "precip", "description")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)

        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("precip", text="Осадки")
        self.tree.heading("description", text="Описание")

        self.tree.column("date", width=110, anchor="center")
        self.tree.column("temp", width=140, anchor="center")
        self.tree.column("precip", width=80, anchor="center")
        self.tree.column("description", width=440)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        ttk.Button(frame, text="Удалить выбранную запись", command=self.delete_record).grid(
            row=1, column=0, pady=(6, 0), sticky="w"
        )

    def _build_status_bar(self) -> None:
        self.status_var = tk.StringVar(value="Готово.")
        ttk.Label(self.root, textvariable=self.status_var, foreground="gray").grid(
            row=3, column=0, padx=12, pady=(0, 6), sticky="w"
        )

    def add_record(self) -> None:
        date = self.entry_date.get().strip()
        temp = self.entry_temp.get().strip()
        desc = self.entry_desc.get().strip()
        precip = self.precip_var.get()

        errors = []
        if not validate_date(date):
            errors.append("Дата должна быть в формате ДД.ММ.ГГГГ (например, 03.05.2025).")
        if not validate_temperature(temp):
            errors.append("Температура должна быть числом (например, -5 или 23.5).")
        if not desc:
            errors.append("Описание не может быть пустым.")

        if errors:
            messagebox.showerror("Ошибка ввода", "\n".join(errors))
            return

        record = {
            "date": date,
            "temperature": float(temp),
            "precipitation": precip,
            "description": desc,
        }
        self.records.append(record)
        save_records(self.records)
        self.refresh_table(self.records)

        self.entry_temp.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.precip_var.set("Нет")
        self.status_var.set(f"Запись за {date} добавлена. Всего записей: {len(self.records)}.")

    def delete_record(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите запись для удаления.")
            return

        values = self.tree.item(selected[0])["values"]
        date_val, temp_val, precip_val, desc_val = values

        for i, rec in enumerate(self.records):
            if (
                rec["date"] == str(date_val)
                and rec["temperature"] == float(temp_val)
                and rec["precipitation"] == str(precip_val)
                and rec["description"] == str(desc_val)
            ):
                self.records.pop(i)
                break

        save_records(self.records)
        self.refresh_table(self.records)
        self.status_var.set(f"Запись удалена. Всего записей: {len(self.records)}.")

    def apply_filter(self) -> None:
        date_f = self.filter_date.get().strip()
        temp_f = self.filter_temp.get().strip()

        if date_f and not validate_date(date_f):
            messagebox.showerror("Ошибка фильтра", "Введите дату в формате ДД.ММ.ГГГГ.")
            return
        if temp_f and not validate_temperature(temp_f):
            messagebox.showerror("Ошибка фильтра", "Порог температуры должен быть числом.")
            return

        filtered = filter_records(self.records, date_f, temp_f)
        self.refresh_table(filtered)
        self.status_var.set(f"Найдено записей по фильтру: {len(filtered)}.")

    def reset_filter(self) -> None:
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.refresh_table(self.records)
        self.status_var.set(f"Фильтр сброшен. Показаны все записи: {len(self.records)}.")

    def refresh_table(self, records: list[dict]) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in records:
            self.tree.insert(
                "", "end",
                values=(rec["date"], rec["temperature"], rec["precipitation"], rec["description"]),
            )


def main() -> None:
    root = tk.Tk()
    WeatherDiaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
