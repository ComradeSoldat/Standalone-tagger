import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
from tkinterdnd2 import DND_FILES, TkinterDnD

class TagAutocompleteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tag Autocomplete")
        self.root.geometry("800x600")

        # База данных тегов: {название: {type, count, aliases}}
        self.tags_db = {}

        # Выбранные теги
        self.selected_tags = []

        self.setup_ui()
        self.load_default_tags()

    def setup_ui(self):
        # Верхняя панель для управления файлами
        top_frame = tk.Frame(self.root, bg="#2b2b2b", pady=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top_frame, text="Загрузка CSV файлов:", 
                bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        load_btn = tk.Button(top_frame, text="Загрузить CSV", 
                            command=self.load_csv_file, 
                            bg="#4a4a4a", fg="white",
                            activebackground="#5a5a5a")
        load_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(top_frame, text="Очистить промпт", 
                             command=self.clear_prompt,
                             bg="#4a4a4a", fg="white",
                             activebackground="#5a5a5a")
        clear_btn.pack(side=tk.RIGHT, padx=5)

        info_label = tk.Label(top_frame, 
                             text="Можно перетаскивать CSV файлы в окно",
                             bg="#2b2b2b", fg="#888", font=("Arial", 9))
        info_label.pack(side=tk.RIGHT, padx=10)

        # Фрейм для поиска
        search_frame = tk.Frame(self.root, bg="#2b2b2b", pady=10)
        search_frame.pack(fill=tk.X, padx=10)

        tk.Label(search_frame, text="Поиск тега:", 
                bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=("Arial", 12), bg="#3a3a3a", fg="white",
                                     insertbackground="white")
        self.search_entry.pack(fill=tk.X, pady=5)
        self.search_entry.bind('<Return>', self.on_enter_key)
        self.search_entry.bind('<Down>', self.focus_listbox)

        # Фрейм для результатов поиска
        results_frame = tk.Frame(self.root, bg="#2b2b2b")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tk.Label(results_frame, text="Результаты (двойной клик для выбора):", 
                bg="#2b2b2b", fg="white", font=("Arial", 10)).pack(anchor=tk.W)

        # Listbox с прокруткой
        listbox_frame = tk.Frame(results_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_listbox = tk.Listbox(listbox_frame, 
                                          yscrollcommand=scrollbar.set,
                                          font=("Arial", 10),
                                          bg="#3a3a3a", fg="white",
                                          selectbackground="#5a5a5a",
                                          height=10)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_listbox.yview)

        self.results_listbox.bind('<Double-Button-1>', self.on_tag_select)
        self.results_listbox.bind('<Return>', self.on_tag_select)

        # Фрейм для промпта
        prompt_frame = tk.Frame(self.root, bg="#2b2b2b", pady=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        tk.Label(prompt_frame, text="Промпт (выбранные теги):", 
                bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        # Text widget с прокруткой
        text_frame = tk.Frame(prompt_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.prompt_text = tk.Text(text_frame, height=6, 
                                   font=("Arial", 11),
                                   bg="#3a3a3a", fg="white",
                                   insertbackground="white",
                                   yscrollcommand=text_scrollbar.set,
                                   wrap=tk.WORD)
        self.prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.prompt_text.yview)

        # Кнопка копирования
        copy_btn = tk.Button(prompt_frame, text="Копировать в буфер обмена",
                            command=self.copy_to_clipboard,
                            bg="#4a7c4a", fg="white",
                            activebackground="#5a8c5a",
                            font=("Arial", 10, "bold"),
                            pady=5)
        copy_btn.pack(fill=tk.X, pady=5)

        # Информация о количестве тегов
        self.info_label = tk.Label(self.root, text="Загружено тегов: 0",
                                   bg="#2b2b2b", fg="#888", font=("Arial", 9))
        self.info_label.pack(pady=5)

        # Настройка drag and drop
        try:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        except:
            pass

    def load_default_tags(self):
        """Загрузка тегов по умолчанию из встроенного набора"""
        default_tags = [
            ("1girl", "0", "1000000", "1girls,sole_female"),
            ("1boy", "0", "800000", "1boys,sole_male"),
            ("solo", "0", "900000", ""),
            ("long_hair", "0", "700000", "longhair"),
            ("short_hair", "0", "600000", "shorthair"),
            ("blonde_hair", "0", "500000", "blonde"),
            ("brown_hair", "0", "450000", "brown"),
            ("black_hair", "0", "400000", "black"),
            ("blue_eyes", "0", "350000", ""),
            ("red_eyes", "0", "300000", ""),
            ("smile", "0", "800000", "smiling"),
            ("open_mouth", "0", "600000", ""),
            ("looking_at_viewer", "0", "750000", "looking_at_you"),
            ("masterpiece", "5", "500000", ""),
            ("best_quality", "5", "450000", "best quality,high quality"),
            ("highres", "5", "400000", "high_res,high_resolution"),
            ("portrait", "0", "300000", ""),
            ("landscape", "0", "250000", ""),
            ("anime", "5", "600000", "anime_style"),
            ("realistic", "5", "400000", "photorealistic"),
        ]

        for tag_data in default_tags:
            self.add_tag_to_db(tag_data)

        self.update_info_label()

    def add_tag_to_db(self, tag_data):
        """Добавление тега в базу данных"""
        if len(tag_data) >= 2:
            name = tag_data[0].strip()
            tag_type = tag_data[1] if len(tag_data) > 1 else "0"
            count = tag_data[2] if len(tag_data) > 2 else "0"
            aliases = tag_data[3] if len(tag_data) > 3 else ""

            if name:
                self.tags_db[name.lower()] = {
                    'display': name,
                    'type': tag_type,
                    'count': count,
                    'aliases': aliases.lower() if aliases else ""
                }

    def detect_encoding(self, filepath):
        """Определение кодировки файла"""
        # Список кодировок для проверки
        encodings = ['utf-8', 'utf-8-sig', 'windows-1251', 'cp1251', 'latin-1', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue

        # Если ничего не подошло, используем latin-1 (он всегда работает)
        return 'latin-1'

    def load_csv_file(self):
        """Загрузка CSV файла через диалог"""
        filename = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.process_csv_file(filename)

    def on_drop(self, event):
        """Обработка перетаскивания файлов"""
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            file_path = file_path.strip('{}')
            if file_path.lower().endswith('.csv'):
                self.process_csv_file(file_path)

    def process_csv_file(self, filepath):
        """Обработка CSV файла с автоопределением кодировки"""
        try:
            count_before = len(self.tags_db)

            # Определяем кодировку файла
            encoding = self.detect_encoding(filepath)

            with open(filepath, 'r', encoding=encoding) as f:
                csv_reader = csv.reader(f)
                loaded_rows = 0
                for row in csv_reader:
                    if row and row[0]:
                        self.add_tag_to_db(row)
                        loaded_rows += 1

            count_after = len(self.tags_db)
            new_tags = count_after - count_before

            self.update_info_label()
            messagebox.showinfo("Успех", 
                              f"Загружено: {os.path.basename(filepath)}\n"
                              f"Кодировка: {encoding}\n"
                              f"Обработано строк: {loaded_rows}\n"
                              f"Добавлено новых тегов: {new_tags}\n"
                              f"Всего тегов: {count_after}")
        except Exception as e:
            messagebox.showerror("Ошибка", 
                               f"Не удалось загрузить файл:\n{str(e)}\n\n"
                               f"Попробуйте пересохранить CSV в UTF-8")

    def update_info_label(self):
        """Обновление информации о количестве тегов"""
        self.info_label.config(text=f"Загружено тегов: {len(self.tags_db)}")

    def on_search_change(self, *args):
        """Обработка изменения текста в поле поиска"""
        search_text = self.search_var.get().lower().strip()

        self.results_listbox.delete(0, tk.END)

        if not search_text:
            return

        # Поиск совпадений
        matches = []
        for tag_key, tag_data in self.tags_db.items():
            # Поиск по имени тега
            if search_text in tag_key:
                matches.append((tag_data['display'], int(tag_data.get('count', 0))))
            # Поиск по алиасам
            elif tag_data.get('aliases') and search_text in tag_data['aliases']:
                matches.append((tag_data['display'], int(tag_data.get('count', 0))))

        # Сортировка по популярности (count)
        matches.sort(key=lambda x: x[1], reverse=True)

        # Ограничение результатов
        for tag, count in matches[:100]:
            self.results_listbox.insert(tk.END, tag)

    def on_tag_select(self, event=None):
        """Обработка выбора тега"""
        selection = self.results_listbox.curselection()
        if selection:
            tag = self.results_listbox.get(selection[0])
            self.add_tag_to_prompt(tag)
            self.search_var.set("")
            self.search_entry.focus()

    def add_tag_to_prompt(self, tag):
        """Добавление тега в промпт"""
        if tag not in self.selected_tags:
            self.selected_tags.append(tag)
            self.update_prompt_display()

    def update_prompt_display(self):
        """Обновление отображения промпта"""
        self.prompt_text.delete('1.0', tk.END)
        prompt = ", ".join(self.selected_tags)
        self.prompt_text.insert('1.0', prompt)

    def clear_prompt(self):
        """Очистка промпта"""
        self.selected_tags = []
        self.update_prompt_display()

    def copy_to_clipboard(self):
        """Копирование промпта в буфер обмена"""
        prompt = ", ".join(self.selected_tags)
        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)
        messagebox.showinfo("Успех", "Промпт скопирован в буфер обмена!")

    def on_enter_key(self, event):
        """Обработка нажатия Enter в поле поиска"""
        if self.results_listbox.size() > 0:
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(0)
            self.results_listbox.activate(0)
            self.on_tag_select()

    def focus_listbox(self, event):
        """Фокус на списке результатов"""
        if self.results_listbox.size() > 0:
            self.results_listbox.focus()
            self.results_listbox.selection_clear(0, tk.END)
            self.results_listbox.selection_set(0)
            self.results_listbox.activate(0)

if __name__ == "__main__":
    # Попытка использовать TkinterDnD для drag-and-drop
    try:
        root = TkinterDnD.Tk()
    except:
        root = tk.Tk()
        print("TkinterDnD не установлен. Функция перетаскивания файлов недоступна.")
        print("Установите: pip install tkinterdnd2")

    root.configure(bg="#2b2b2b")
    app = TagAutocompleteApp(root)
    root.mainloop()
