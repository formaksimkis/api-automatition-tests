import subprocess
import sys
import os
from datetime import datetime


def run_tests_with_reports():
    """Запуск тестов с генерацией различных отчетов"""

    # Получить абсолютный путь к файлу
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(current_dir, "tests")
    test_file_path = os.path.join(tests_dir, "test_posts_api.py")

    # Создаем папку для отчетов
    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print("🚀 Запуск API тестов с генерацией отчетов...")
    print("=" * 50)

    # Команды для запуска тестов с разными отчетами
    commands = [
        #Стандартный HTML отчет pytest
        [sys.executable, "-m", "pytest", test_file_path,
         "-v",
         f"--html=reports/pytest_report_{timestamp}.html",
         "--self-contained-html"],

        # XML отчет для CI/CD
        [sys.executable, "-m", "pytest", test_file_path,
         f"--junitxml=reports/test_results_{timestamp}.xml"],

        # Подробный текстовый отчет в консоли
        [sys.executable, "-m", "pytest", test_file_path, "-v"],

        # Запуск функции генерации кастомного отчета
        [sys.executable, test_file_path]
    ]

    for i, cmd in enumerate(commands):
        print(f"\n📋 Запуск команды {i + 1}: {' '.join(cmd)}")
        print("-" * 50)

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Вывод результатов
        if result.returncode == 0:
            print("✅ Тесты завершены успешно")
        else:
            print("❌ Тесты завершены с ошибками")

        if result.stdout:
            print("Вывод:")
            print(result.stdout)

        if result.stderr:
            print("Ошибки:")
            print(result.stderr)

    print("\n" + "=" * 50)
    print("📊 Все отчеты сохранены в папке 'reports/'")
    print(f"🕒 Время запуска: {timestamp}")


if __name__ == "__main__":
    run_tests_with_reports()
