#!/usr/bin/env python3
"""
Генератор трафика API с графическим интерфейсом (Tkinter)
Запуск: python traffic_gui.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests
import time
import random
from datetime import datetime

API_URL = "http://localhost:30080"
running = False
stop_flag = False

class TrafficGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор трафика API")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Переменные
        self.post_count = tk.IntVar(value=50)
        self.get_count = tk.IntVar(value=50)
        self.delay = tk.DoubleVar(value=0.05)
        self.threads = tk.IntVar(value=1)
        self.method = tk.StringVar(value="mixed")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== РЕЖИМЫ =====
        mode_frame = ttk.LabelFrame(main_frame, text="Режим генерации", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="POST запросы", variable=self.method, value="post").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mode_frame, text="GET запросы", variable=self.method, value="get").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(mode_frame, text="POST + GET (смешанный)", variable=self.method, value="mixed").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(mode_frame, text="Бесконечный (до остановки)", variable=self.method, value="infinite").grid(row=0, column=3, padx=5)
        
        # ===== НАСТРОЙКИ =====
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # POST запросы
        ttk.Label(settings_frame, text="POST запросов:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(settings_frame, from_=0, to=10000, textvariable=self.post_count, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # GET запросы
        ttk.Label(settings_frame, text="GET запросов:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(settings_frame, from_=0, to=10000, textvariable=self.get_count, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # Задержка
        ttk.Label(settings_frame, text="Задержка (сек):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(settings_frame, from_=0, to=1, increment=0.01, textvariable=self.delay, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Потоки
        ttk.Label(settings_frame, text="Потоков:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.threads, width=10).grid(row=1, column=3, padx=5, pady=5)
        
        # ===== КНОПКИ =====
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(buttons_frame, text="▶ Старт", command=self.start_generation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="⏹ Стоп", command=self.stop_generation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="🗑 Очистить лог", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📊 Проверить API", command=self.check_api).pack(side=tk.LEFT, padx=5)
        
        # ===== СТАТУС =====
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(0, 5))
        
        # ===== ЛОГ =====
        log_frame = ttk.LabelFrame(main_frame, text="Лог запросов", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Настройка цветов для лога
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("info", foreground="blue")
        
    def log(self, message, tag=None):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted, tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Очистка лога"""
        self.log_text.delete(1.0, tk.END)
        self.log("Лог очищен", "info")
    
    def check_api(self):
        """Проверка доступности API"""
        try:
            response = requests.get(f"{API_URL}/api/v1/health", timeout=3)
            if response.status_code == 200:
                self.log("✅ API доступен", "success")
                self.status_var.set("API доступен")
            else:
                self.log(f"⚠️ API ответил с кодом {response.status_code}", "error")
        except Exception as e:
            self.log(f"❌ API недоступен: {e}", "error")
            self.status_var.set("API недоступен")
    
    def generate_post(self, count, thread_id):
        """Генерация POST запросов"""
        for i in range(1, count + 1):
            if stop_flag:
                return
            
            try:
                data = {"test": i, "thread": thread_id, "random": random.randint(1, 1000)}
                response = requests.post(f"{API_URL}/api/v1/data", json=data, timeout=2)
                
                if response.status_code == 200:
                    self.log(f"[Поток {thread_id}] ✓ POST {i}/{count} - статус: {response.status_code}", "success")
                else:
                    self.log(f"[Поток {thread_id}] ✗ POST {i}/{count} - статус: {response.status_code}", "error")
                
                time.sleep(self.delay.get())
                
            except Exception as e:
                self.log(f"[Поток {thread_id}] ✗ POST {i}/{count} - ошибка: {e}", "error")
    
    def generate_get(self, count, thread_id):
        """Генерация GET запросов"""
        for i in range(1, count + 1):
            if stop_flag:
                return
            
            try:
                random_id = random.randint(1, 100)
                response = requests.get(f"{API_URL}/api/v1/data/{random_id}", timeout=2)
                
                if response.status_code == 200:
                    self.log(f"[Поток {thread_id}] ✓ GET {i}/{count} (ID={random_id}) - статус: {response.status_code}", "success")
                else:
                    self.log(f"[Поток {thread_id}] ✗ GET {i}/{count} (ID={random_id}) - статус: {response.status_code}", "error")
                
                time.sleep(self.delay.get())
                
            except Exception as e:
                self.log(f"[Поток {thread_id}] ✗ GET {i}/{count} - ошибка: {e}", "error")
    
    def generate_infinite(self, thread_id):
        """Бесконечная генерация"""
        count = 0
        while not stop_flag:
            try:
                # Чередуем POST и GET
                if count % 2 == 0:
                    data = {"test": count, "thread": thread_id}
                    response = requests.post(f"{API_URL}/api/v1/data", json=data, timeout=2)
                    method = "POST"
                else:
                    random_id = random.randint(1, 100)
                    response = requests.get(f"{API_URL}/api/v1/data/{random_id}", timeout=2)
                    method = "GET"
                
                count += 1
                
                if response.status_code == 200:
                    self.log(f"[Поток {thread_id}] ✓ {method} #{count} - статус: {response.status_code}", "success")
                else:
                    self.log(f"[Поток {thread_id}] ✗ {method} #{count} - статус: {response.status_code}", "error")
                
                time.sleep(self.delay.get())
                
            except Exception as e:
                self.log(f"[Поток {thread_id}] ✗ Ошибка: {e}", "error")
                time.sleep(1)
    
    def start_generation(self):
        """Запуск генерации в отдельном потоке"""
        global running, stop_flag
        
        if not self.check_api_quick():
            messagebox.showerror("Ошибка", "API недоступен. Проверьте, запущен ли стенд.")
            return
        
        stop_flag = False
        running = True
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Генерация...")
        
        method = self.method.get()
        threads_count = self.threads.get()
        
        self.log(f"\n{'='*50}", "info")
        self.log(f"Запуск генерации: метод={method}, потоков={threads_count}", "info")
        
        if method == "infinite":
            self.log("Режим: БЕСКОНЕЧНАЯ ГЕНЕРАЦИЯ (нажмите Стоп для остановки)", "info")
            for i in range(threads_count):
                t = threading.Thread(target=self.generate_infinite, args=(i+1,))
                t.daemon = True
                t.start()
        else:
            post_count = self.post_count.get() if method in ["post", "mixed"] else 0
            get_count = self.get_count.get() if method in ["get", "mixed"] else 0
            
            self.log(f"POST запросов: {post_count}, GET запросов: {get_count}", "info")
            self.log(f"Задержка: {self.delay.get()} сек", "info")
            
            threads_list = []
            
            # Запуск потоков для POST
            if post_count > 0:
                per_thread = max(1, post_count // threads_count)
                for i in range(threads_count):
                    t = threading.Thread(target=self.generate_post, args=(per_thread, i+1))
                    t.start()
                    threads_list.append(t)
            
            # Запуск потоков для GET
            if get_count > 0:
                per_thread = max(1, get_count // threads_count)
                for i in range(threads_count):
                    t = threading.Thread(target=self.generate_get, args=(per_thread, i+1))
                    t.start()
                    threads_list.append(t)
            
            # Ожидание завершения
            def wait_completion():
                for t in threads_list:
                    t.join()
                self.root.after(0, self.generation_complete)
            
            threading.Thread(target=wait_completion, daemon=True).start()
    
    def generation_complete(self):
        """Завершение генерации"""
        global running
        running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Генерация завершена")
        self.log("✅ Генерация завершена", "success")
    
    def stop_generation(self):
        """Остановка генерации"""
        global stop_flag, running
        stop_flag = True
        running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Остановлено")
        self.log("⏹ Генерация остановлена", "info")
    
    def check_api_quick(self):
        """Быстрая проверка API"""
        try:
            requests.get(f"{API_URL}/api/v1/health", timeout=2)
            return True
        except:
            return False

def main():
    root = tk.Tk()
    app = TrafficGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()