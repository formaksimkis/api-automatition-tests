import pytest
import json
import os
from datetime import datetime


class TestPostsAPI:
    """Тесты для API постов"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Фикстура для настройки перед каждым тестом и очистки после"""
        # Создаем папку для отчетов если ее нет
        os.makedirs("reports", exist_ok=True)
        yield

    @classmethod
    def get_test_count(cls):
        """Возвращает количество тестов в классе"""
        test_methods = [method for method in dir(cls)
                        if method.startswith('test_')
                        and callable(getattr(cls, method))]
        return len(test_methods)

    def test_get_all_posts(self, api_client):
        """Тест получения всех постов"""
        response = api_client.get("/posts")

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверка структуры JSON-ответа
        posts = response.json()
        assert isinstance(posts, list), "Ответ должен быть списком"
        assert len(posts) > 0, "Список постов не должен быть пустым"

        # Проверка структуры первого поста
        first_post = posts[0]
        expected_fields = ["userId", "id", "title", "body"]
        for field in expected_fields:
            assert field in first_post, f"Отсутствует поле {field}"

    def test_get_single_post(self, api_client):
        """Тест получения конкретного поста"""
        response = api_client.get("/posts/1")

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверка структуры JSON-ответа
        post = response.json()
        expected_fields = ["userId", "id", "title", "body"]
        for field in expected_fields:
            assert field in post, f"Отсутствует поле {field}"

        # Проверка конкретных значений
        assert post["id"] == 1, f"Ожидался id=1, получен {post['id']}"
        assert isinstance(post["title"], str), "Title должен быть строкой"
        assert isinstance(post["body"], str), "Body должен быть строкой"

    def test_create_post(self, api_client, sample_post_data):
        """Тест создания нового поста"""
        response = api_client.post("/posts", sample_post_data)

        # Проверка статус-кода
        assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"

        # Проверка структуры JSON-ответа
        created_post = response.json()

        # Проверка, что вернулись данные с ID
        assert "id" in created_post, "В ответе должен быть id созданного поста"

        # Проверка, что данные соответствуют отправленным
        assert created_post["title"] == sample_post_data["title"]
        assert created_post["body"] == sample_post_data["body"]
        assert created_post["userId"] == sample_post_data["userId"]

    def test_update_post(self, api_client):
        """Тест обновления поста"""
        update_data = {
            "id": 1,
            "title": "Updated Title",
            "body": "Updated body content",
            "userId": 1
        }

        response = api_client.put("/posts/1", update_data)

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверка обновленных данных
        updated_post = response.json()
        assert updated_post["title"] == "Updated Title"
        assert updated_post["body"] == "Updated body content"

    def test_delete_post(self, api_client):
        """Тест удаления поста"""
        response = api_client.delete("/posts/1")

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    def test_nonexistent_resource(self, api_client):
        """Тест обработки ошибок для несуществующего ресурса"""
        response = api_client.get("/posts/99999")

        # Проверка статус-кода для несуществующего ресурса
        assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"

    def test_invalid_post_creation(self, api_client):
        """Тест создания поста с невалидными данными"""
        invalid_data = {
            "title": "",  # Пустой title
            "body": "Test body"
        }

        response = api_client.post("/posts", invalid_data)

        # API может обрабатывать это по-разному, проверяем что ответ есть
        assert response.status_code in [200, 201, 400], f"Неожиданный статус код: {response.status_code}"

    def test_partial_update_post(self, api_client, patch_data_all):
        """Тест частичного обновления поста с помощью PATCH"""
        # Сначала получаем исходные данные поста
        original_response = api_client.get("/posts/1")
        original_post = original_response.json()

        # Выполняем PATCH запрос
        response = api_client.patch("/posts/1", patch_data_all)

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверка обновленных данных
        updated_post = response.json()
        assert updated_post["title"] == patch_data_all["title"]
        assert updated_post["body"] == patch_data_all["body"]
        assert updated_post["userId"] == patch_data_all["userId"]

        # Проверяем, что остальные поля остались без изменений
        assert updated_post["id"] == original_post["id"], "Поле id не должно было измениться"

    def test_partial_update_with_multiple_fields(self, api_client, patch_data_multiple_fields):
        """Тест частичного обновления нескольких полей"""
        # Сначала получаем исходные данные поста
        original_response = api_client.get("/posts/1")
        original_post = original_response.json()

        # Выполняем PATCH запрос
        response = api_client.patch("/posts/1", patch_data_multiple_fields)

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверка обновленных данных
        updated_post = response.json()
        assert updated_post["title"] == patch_data_multiple_fields["title"]
        assert updated_post["body"] == patch_data_multiple_fields["body"]

        # Проверяем, что неизмененные поля остались без изменений
        assert updated_post["userId"] == original_post["userId"], "Поле userId не должно было измениться"
        assert updated_post["id"] == original_post["id"], "Поле id не должно было измениться"

    def test_partial_update_single_field(self, api_client):
        """Тест частичного обновления только одного поля"""
        # Сначала получаем исходные данные поста
        original_response = api_client.get("/posts/1")
        original_post = original_response.json()

        single_field_data = {
            "title": "Updated Only Title"
        }

        # Выполняем PATCH запрос
        response = api_client.patch("/posts/1", single_field_data)

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверка обновленных данных
        updated_post = response.json()
        assert updated_post["title"] == "Updated Only Title"

        # Проверяем, что неизмененные поля остались без изменений
        assert updated_post["body"] == original_post["body"], "Поле body не должно было измениться"
        assert updated_post["userId"] == original_post["userId"], "Поле userId не должно было измениться"
        assert updated_post["id"] == original_post["id"], "Поле id не должно было измениться"

    def test_partial_update_empty_data(self, api_client, patch_data_empty):
        """Тест частичного обновления с пустыми данными"""
        # Сначала получаем исходные данные поста
        original_response = api_client.get("/posts/1")
        original_post = original_response.json()

        # Выполняем PATCH запрос с пустыми данными
        response = api_client.patch("/posts/1", patch_data_empty)

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверяем, что все поля остались без изменений
        unchanged_post = response.json()
        assert unchanged_post["title"] == original_post["title"], "Поле title не должно было измениться"
        assert unchanged_post["body"] == original_post["body"], "Поле body не должно было измениться"
        assert unchanged_post["userId"] == original_post["userId"], "Поле userId не должно было измениться"
        assert unchanged_post["id"] == original_post["id"], "Поле id не должно было измениться"

    def test_partial_update_nonexistent_post(self, api_client, patch_data_all):
        """Тест частичного обновления несуществующего поста"""
        # Для несуществующего поста мы не можем получить исходные данные
        # поэтому просто проверяем поведение API

        response = api_client.patch("/posts/99999", patch_data_all)

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверяем, что в ответе есть отправленные нами данные
        updated_data = response.json()
        assert "title" in updated_data, "В ответе должно быть поле title"
        assert updated_data["title"] == patch_data_all["title"], "Title должен соответствовать отправленным данным"

    def test_filter_posts_by_user_id(self, api_client):
        """Тест фильтрации постов по userId"""
        response = api_client.get("/posts?userId=1")

        # Проверка статус-кода
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

        # Проверка структуры ответа
        posts = response.json()
        assert isinstance(posts, list), "Ответ должен быть списком"

        # Проверяем что все посты принадлежат userId=1
        for post in posts:
            assert post["userId"] == 1, f"Все посты должны иметь userId=1, найден userId={post['userId']}"


def generate_custom_html_report():
    """Генерация кастомного HTML отчета"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    display_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_filename = f"reports/api_test_report_{timestamp}.html"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; padding: 20px; background: #2c3e50; color: white; border-radius: 8px; margin-bottom: 20px; }}
            .summary {{ background: #ecf0f1; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .test-case {{ border: 1px solid #bdc3c7; margin: 10px 0; padding: 15px; border-radius: 8px; }}
            .passed {{ border-left: 5px solid #27ae60; background: #d5f4e6; }}
            .failed {{ border-left: 5px solid #e74c3c; background: #fadbd8; }}
            .test-name {{ font-weight: bold; font-size: 16px; margin-bottom: 10px; }}
            .test-description {{ color: #7f8c8d; margin-bottom: 10px; }}
            .test-details {{ background: white; padding: 10px; border-radius: 4px; }}
            .timestamp {{ text-align: right; color: #7f8c8d; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 API Test Report</h1>
                <p>JSONPlaceholder API Automated Tests</p>
            </div>

            <div class="summary">
                <h2>📈 Summary</h2>
                <p><strong>Project:</strong> JSONPlaceholder API Tests</p>
                <p><strong>Base URL:</strong> https://jsonplaceholder.typicode.com</p>
                <p><strong>Test Date:</strong> {display_timestamp}</p>
                <p><strong>Total Tests:</strong> {TestPostsAPI.get_test_count()}</p>
                <p><strong>Test Scope:</strong> CRUD operations for /posts endpoint</p>
            </div>

            <div class="test-results">
                <h2>🧪 Test Results</h2>

                <div class="test-case passed">
                    <div class="test-name">✅ test_get_all_posts</div>
                    <div class="test-description">Тест получения всех постов</div>
                    <div class="test-details">
                        <p><strong>Endpoint:</strong> GET /posts</p>
                        <p><strong>Checks:</strong> Status code 200, JSON structure, required fields</p>
                        <p><strong>Result:</strong> PASSED</p>
                    </div>
                </div>

                <div class="test-case passed">
                    <div class="test-name">✅ test_get_single_post</div>
                    <div class="test-description">Тест получения конкретного поста</div>
                    <div class="test-details">
                        <p><strong>Endpoint:</strong> GET /posts/1</p>
                        <p><strong>Checks:</strong> Status code 200, data validation, field types</p>
                        <p><strong>Result:</strong> PASSED</p>
                    </div>
                </div>

                <div class="test-case passed">
                    <div class="test-name">✅ test_create_post</div>
                    <div class="test-description">Тест создания нового поста</div>
                    <div class="test-details">
                        <p><strong>Endpoint:</strong> POST /posts</p>
                        <p><strong>Checks:</strong> Status code 201, data consistency, ID generation</p>
                        <p><strong>Result:</strong> PASSED</p>
                    </div>
                </div>

                <div class="test-case passed">
                    <div class="test-name">✅ test_update_post</div>
                    <div class="test-description">Тест обновления поста</div>
                    <div class="test-details">
                        <p><strong>Endpoint:</strong> PUT /posts/1</p>
                        <p><strong>Checks:</strong> Status code 200, data update verification</p>
                        <p><strong>Result:</strong> PASSED</p>
                    </div>
                </div>

                <div class="test-case passed">
                    <div class="test-name">✅ test_delete_post</div>
                    <div class="test-description">Тест удаления поста</div>
                    <div class="test-details">
                        <p><strong>Endpoint:</strong> DELETE /posts/1</p>
                        <p><strong>Checks:</strong> Status code 200</p>
                        <p><strong>Result:</strong> PASSED</p>
                    </div>
                </div>

                <div class="test-case passed">
                    <div class="test-name">✅ test_nonexistent_resource</div>
                    <div class="test-description">Тест обработки ошибок для несуществующего ресурса</div>
                    <div class="test-details">
                        <p><strong>Endpoint:</strong> GET /posts/99999</p>
                        <p><strong>Checks:</strong> Status code 404</p>
                        <p><strong>Result:</strong> PASSED</p>
                    </div>
                </div>

                <div class="test-case passed">
                    <div class="test-name">✅ test_invalid_post_creation</div>
                    <div class="test-description">Тест создания поста с невалидными данными</div>
                    <div class="test-details">
                        <p><strong>Endpoint:</strong> POST /posts</p>
                        <p><strong>Checks:</strong> Error handling with invalid data</p>
                        <p><strong>Result:</strong> PASSED</p>
                    </div>
                </div>
            </div>

            <div class="test-case passed">
                <div class="test-name">✅ test_partial_update_post</div>
                <div class="test-description">Тест частичного обновления поста</div>
                <div class="test-details">
                    <p><strong>Endpoint:</strong> PATCH /posts/1</p>
                    <p><strong>Checks:</strong> Status code 200, partial field updates, other fields unchanged</p>
                    <p><strong>Result:</strong> PASSED</p>
                </div>
            </div>

            <div class="test-case passed">
                <div class="test-name">✅ test_partial_update_with_multiple_fields</div>
                <div class="test-description">Тест частичного обновления нескольких полей</div>
                <div class="test-details">
                    <p><strong>Endpoint:</strong> PATCH /posts/1</p>
                    <p><strong>Checks:</strong> Status code 200, few field updates, other fields unchanged</p>
                    <p><strong>Result:</strong> PASSED</p>
                </div>
            </div>

            <div class="test-case passed">
                <div class="test-name">✅ test_partial_update_single_field</div>
                <div class="test-description">Тест частичного обновления одного поля</div>
                <div class="test-details">
                    <p><strong>Endpoint:</strong> PATCH /posts/1</p>
                    <p><strong>Checks:</strong> Status code 200, single field update, other fields unchanged</p>
                    <p><strong>Result:</strong> PASSED</p>
                </div>
            </div>

            <div class="test-case passed">
                <div class="test-name">✅ test_partial_update_empty_data</div>
                <div class="test-description">Тест частичного обновления с пустыми данными</div>
                <div class="test-details">
                    <p><strong>Endpoint:</strong> PATCH /posts/1</p>
                    <p><strong>Checks:</strong> Status code 200, structure preservation with empty payload</p>
                    <p><strong>Result:</strong> PASSED</p>
                </div>
            </div>

            <div class="test-case passed">
                <div class="test-name">✅ test_partial_update_nonexistent_post</div>
                <div class="test-description">Тест частичного обновления несуществующего поста</div>
                <div class="test-details">
                    <p><strong>Endpoint:</strong> PATCH /posts/99999</p>
                    <p><strong>Checks:</strong> Status code 200, behavior with non-existent resources</p>
                    <p><strong>Result:</strong> PASSED</p>
                </div>
            </div>
            
            <div class="test-case passed">
                <div class="test-name">✅ test_filter_posts_by_user_id</div>
                <div class="test-description">Тест фильтрации постов по userId</div>
                <div class="test-details">
                    <p><strong>Endpoint:</strong> GET /posts?userId=1</p>
                    <p><strong>HTTP Method:</strong> GET with query parameters</p>
                    <p><strong>Checks:</strong></p>
                    <p><strong>Result:</strong> PASSED ✅</p>
                </div>
            </div>

            <div class="summary">
                <h2>📋 Conclusions</h2>
                <p><strong>Overall Status:</strong> ✅ ALL TESTS PASSED</p>
                <p><strong>API Status:</strong> ✅ Working correctly</p>
                <p><strong>Test Coverage:</strong> ✅ Comprehensive CRUD operations coverage</p>
                <p><strong>Error Handling:</strong> ✅ Proper error responses verified</p>
                <p><strong>Recommendations:</strong> Continue monitoring API performance and add more edge case tests</p>
            </div>

            <div class="timestamp">
                Report generated on: {display_timestamp}
            </div>
        </div>
    </body>
    </html>
    """

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML отчет сохранен: {report_filename}")
    return report_filename


if __name__ == "__main__":
    # Запуск тестов с генерацией стандартного HTML отчета pytest
    pytest_args = [
        __file__,
        "-v",
        "--html=reports/pytest_report.html",
        "--self-contained-html"
    ]

    # Запускаем тесты
    exit_code = pytest.main(pytest_args)

    # Генерируем кастомный HTML отчет
    if exit_code == 0:
        custom_report_path = generate_custom_html_report()
        print(f"Все тесты прошли успешно!")
        print(f"Отчеты доступны:")
        print(f"   - Стандартный: reports/pytest_report.html")
        print(f"   - Кастомный: {custom_report_path}")
    else:
        print("Некоторые тесты не прошли")  # Генерируем кастомный HTML отчет
