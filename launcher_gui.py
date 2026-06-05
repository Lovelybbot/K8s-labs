#!/usr/bin/env python3
"""
Лаунчер Kubernetes Lab с графическим интерфейсом (Tkinter)
Запуск: python launcher_gui.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import sys
import os
import platform
import webbrowser

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kubernetes Lab - Управление стендом")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.process = None
        self.running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Kubernetes Lab", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 5))
        
        # Информация о платформе
        platform_text = f"Платформа: {platform.system()} {platform.release()}"
        platform_label = ttk.Label(main_frame, text=platform_text, font=("Arial", 9))
        platform_label.pack(pady=(0, 10))
        
        # ===== КНОПКИ УПРАВЛЕНИЯ =====
        buttons_frame = ttk.LabelFrame(main_frame, text="Управление стендом", padding="10")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Первая строка кнопок
        row1 = ttk.Frame(buttons_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        self.start_btn = ttk.Button(row1, text="▶ Запустить стенд", command=self.start_lab, width=20)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(row1, text="⏹ Остановить клиент", command=self.stop_client, width=20, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.restart_btn = ttk.Button(row1, text="🔄 Перезапустить клиент", command=self.restart_client, width=20)
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        
        # Вторая строка кнопок
        row2 = ttk.Frame(buttons_frame)
        row2.pack(fill=tk.X)
        
        self.clean_btn = ttk.Button(row2, text="🧹 Частичная очистка", command=self.clean_partial, width=20)
        self.clean_btn.pack(side=tk.LEFT, padx=5)
        
        self.clean_all_btn = ttk.Button(row2, text="🗑 Полная очистка", command=self.clean_all, width=20)
        self.clean_all_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== ССЫЛКИ НА СЕРВИСЫ =====
        links_frame = ttk.LabelFrame(main_frame, text="Быстрый доступ к сервисам", padding="10")
        links_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Первая строка ссылок
        links_row1 = ttk.Frame(links_frame)
        links_row1.pack(fill=tk.X, pady=(0, 5))
        
        self.api_btn = ttk.Button(links_row1, text="📱 API (30080)", command=lambda: webbrowser.open("http://localhost:30080/docs"), width=20)
        self.api_btn.pack(side=tk.LEFT, padx=5)
        
        self.prometheus_btn = ttk.Button(links_row1, text="📊 Prometheus (30900)", command=lambda: webbrowser.open("http://localhost:30900"), width=20)
        self.prometheus_btn.pack(side=tk.LEFT, padx=5)
        
        self.grafana_btn = ttk.Button(links_row1, text="📈 Grafana (30300)", command=lambda: webbrowser.open("http://localhost:30300"), width=20)
        self.grafana_btn.pack(side=tk.LEFT, padx=5)
        
        # Вторая строка ссылок
        links_row2 = ttk.Frame(links_frame)
        links_row2.pack(fill=tk.X)
        
        self.swagger_btn = ttk.Button(links_row2, text="📚 Swagger UI", command=lambda: webbrowser.open("http://localhost:30080/docs"), width=20)
        self.swagger_btn.pack(side=tk.LEFT, padx=5)
        
        self.redoc_btn = ttk.Button(links_row2, text="📖 ReDoc", command=lambda: webbrowser.open("http://localhost:30080/redoc"), width=20)
        self.redoc_btn.pack(side=tk.LEFT, padx=5)
        
        self.metrics_btn = ttk.Button(links_row2, text="📊 Metrics", command=lambda: webbrowser.open("http://localhost:30080/metrics"), width=20)
        self.metrics_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== СТАТУС =====
        status_frame = ttk.LabelFrame(main_frame, text="Статус", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(anchor=tk.W)
        
        # ===== ПРОГРЕСС =====
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # ===== ЛОГ =====
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Настройка цветов
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
        
        # Кнопки управления логом
        log_buttons_frame = ttk.Frame(main_frame)
        log_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        clear_btn = ttk.Button(log_buttons_frame, text="🗑 Очистить лог", command=self.clear_log)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(log_buttons_frame, text="💾 Сохранить лог", command=self.save_log)
        save_btn.pack(side=tk.LEFT, padx=5)
        
    def log(self, message, tag=None):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Очистка лога"""
        self.log_text.delete(1.0, tk.END)
        self.log("Лог очищен", "info")
    
    def save_log(self):
        """Сохранение лога в файл"""
        from datetime import datetime
        filename = f"launcher_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(self.log_text.get(1.0, tk.END))
        self.log(f"Лог сохранён в {filename}", "success")
    
    def set_status(self, text, color="black"):
        """Установка статуса"""
        self.status_var.set(text)
        self.root.update_idletasks()
    
    def start_progress(self):
        """Запуск индикатора прогресса"""
        self.progress.start(10)
    
    def stop_progress(self):
        """Остановка индикатора прогресса"""
        self.progress.stop()
    
    def run_command(self, cmd, description):
        """Выполнение команды с выводом в лог"""
        self.log(f"\n{'='*60}", "info")
        self.log(f">>> {description}", "info")
        self.log(f"Команда: {cmd}", "info")
        self.log(f"{'='*60}", "info")
        
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    if "ERROR" in line or "error" in line:
                        self.log(line, "error")
                    elif "OK" in line or "ГОТОВО" in line or "Success" in line:
                        self.log(line, "success")
                    elif "Warning" in line or "Предупреждение" in line:
                        self.log(line, "warning")
                    else:
                        self.log(line, "info")
            
            process.wait()
            
            if process.returncode == 0:
                self.log(f"✅ {description} - УСПЕШНО", "success")
                return True
            else:
                self.log(f"❌ {description} - ОШИБКА (код: {process.returncode})", "error")
                return False
                
        except Exception as e:
            self.log(f"❌ Ошибка выполнения: {e}", "error")
            return False
    
    def start_lab(self):
        """Запуск стенда"""
        if self.running:
            messagebox.showwarning("Предупреждение", "Процесс уже запущен")
            return
        
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.clean_btn.config(state=tk.DISABLED)
        self.clean_all_btn.config(state=tk.DISABLED)
        self.start_progress()
        self.set_status("Запуск стенда...")
        
        def run():
            success = self.run_command("python launcher.py --start", "Запуск Kubernetes Lab")
            
            self.stop_progress()
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.clean_btn.config(state=tk.NORMAL)
            self.clean_all_btn.config(state=tk.NORMAL)
            
            if success:
                self.set_status("Стенд запущен")
                self.log("\n✅ Стенд успешно запущен!", "success")
                self.log("📱 API: http://localhost:30080", "info")
                self.log("📊 Prometheus: http://localhost:30900", "info")
                self.log("📈 Grafana: http://localhost:30300 (admin/admin123)", "info")
                self.log("📚 Swagger: http://localhost:30080/docs", "info")
            else:
                self.set_status("Ошибка запуска")
                self.log("\n❌ Ошибка при запуске стенда", "error")
        
        threading.Thread(target=run, daemon=True).start()
    
    def stop_client(self):
        """Остановка клиента"""
        self.set_status("Остановка клиента...")
        self.start_progress()
        
        def run():
            self.run_command("docker-compose down", "Остановка интеграционного клиента")
            self.stop_progress()
            self.set_status("Клиент остановлен")
            self.log("\n✅ Интеграционный клиент остановлен", "success")
        
        threading.Thread(target=run, daemon=True).start()
    
    def restart_client(self):
        """Перезапуск клиента"""
        self.set_status("Перезапуск клиента...")
        self.start_progress()
        
        def run():
            self.run_command("docker-compose down", "Остановка клиента")
            self.run_command("docker-compose up -d", "Запуск клиента")
            self.stop_progress()
            self.set_status("Клиент перезапущен")
            self.log("\n✅ Интеграционный клиент перезапущен", "success")
        
        threading.Thread(target=run, daemon=True).start()
    
    def clean_partial(self):
        """Частичная очистка"""
        if messagebox.askyesno("Подтверждение", "Частичная очистка удалит приложение и клиент, но оставит мониторинг. Продолжить?"):
            self.set_status("Частичная очистка...")
            self.start_progress()
            
            def run():
                self.run_command("python launcher.py --clean", "Частичная очистка")
                self.stop_progress()
                self.set_status("Частичная очистка завершена")
                self.log("\n✅ Частичная очистка завершена", "success")
                self.log("Мониторинг (Prometheus + Grafana) остался", "info")
            
            threading.Thread(target=run, daemon=True).start()
    
    def clean_all(self):
        """Полная очистка"""
        if messagebox.askyesno("Подтверждение", "Полная очистка удалит ВСЁ (приложение, клиент, мониторинг, образы). Продолжить?"):
            self.set_status("Полная очистка...")
            self.start_progress()
            
            def run():
                self.run_command("python launcher.py --clean-all", "Полная очистка")
                self.stop_progress()
                self.set_status("Полная очистка завершена")
                self.log("\n✅ Полная очистка завершена", "success")
                self.log("Все ресурсы удалены", "info")
            
            threading.Thread(target=run, daemon=True).start()

def main():
    root = tk.Tk()
    app = LauncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()