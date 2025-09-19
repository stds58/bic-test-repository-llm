document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('benchmarkForm');
    const resultsDiv = document.getElementById('results');
    const modelSearchInput = document.getElementById('modelSearch');
    const modelHiddenInput = document.getElementById('model');
    const modelDropdown = document.getElementById('modelDropdown');

    let allModels = []; // Глобальный массив моделей

    // Загружаем модели
    fetch('/api/models?per_page=100')
        .then(response => response.json())
        .then(models => {
            allModels = models;
            // Устанавливаем первую модель по умолчанию
            if (models.length > 0) {
                const firstModel = models[0];
                modelSearchInput.value = firstModel.name || firstModel.id;
                modelHiddenInput.value = firstModel.id;
            }
        })
        .catch(err => {
            console.error('Ошибка загрузки моделей:', err);
            modelSearchInput.placeholder = 'Ошибка загрузки';
        });

    // Показываем/скрываем дропдаун при фокусе/блюре
    modelSearchInput.addEventListener('focus', () => {
        filterModels('');
        modelDropdown.classList.add('active');
    });

    modelSearchInput.addEventListener('blur', () => {
        // Ждём немного, чтобы клик по элементу успел сработать
        setTimeout(() => {
            modelDropdown.classList.remove('active');
        }, 200);
    });

    // Фильтруем модели при вводе
    modelSearchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        filterModels(query);
    });

    // Фильтрация и рендеринг моделей
    function filterModels(query) {
        modelDropdown.innerHTML = '';

        const filteredModels = allModels.filter(model => {
            const name = (model.name || model.id).toLowerCase();
            return name.includes(query);
        });

        if (filteredModels.length === 0) {
            modelDropdown.innerHTML = '<div class="dropdown-item">Модели не найдены</div>';
            return;
        }

        filteredModels.forEach(model => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';

            // Подсвечиваем совпадения
            const name = model.name || model.id;
            const highlightedName = highlightMatch(name, query);

            item.innerHTML = highlightedName;
            item.dataset.modelId = model.id;

            item.addEventListener('click', () => {
                modelSearchInput.value = name;
                modelHiddenInput.value = model.id;
                modelDropdown.classList.remove('active');
            });

            modelDropdown.appendChild(item);
        });
    }

    // Подсветка совпадений
    function highlightMatch(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData();
        const fileInput = document.getElementById('prompt_file');
        const modelInput = document.getElementById('model');
        const runsInput = document.getElementById('runs');
        const visualizeCheckbox = document.getElementById('visualize');
        const downloadBtn = document.getElementById('downloadCsvBtn');
        downloadBtn.style.display = 'none';

        if (fileInput.files.length > 0) {
            formData.append('prompt_file', fileInput.files[0]);
        }
        formData.append('model', modelInput.value);
        formData.append('runs', runsInput.value);
        formData.append('visualize', visualizeCheckbox.checked ? "true" : "false");

        const button = form.querySelector('button');
        const resultsDiv = document.getElementById('results');
        button.disabled = true;
        resultsDiv.innerHTML = '<p>Запускаем бенчмарк... Это может занять несколько минут.</p>';

        try {
            // 1. Отправляем POST-запрос на /api/benchmark с формой
            const response = await fetch('/api/benchmark', {
                method: 'POST',
                body: formData
            });

            // 2. Проверяем, успешен ли HTTP-ответ (статус 200-299)
            if (!response.ok) {
                // Если нет — выбрасываем ошибку с кодом и текстом
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // 3. Смотрим Content-Type ответа
            const contentType = response.headers.get('content-type');

            // 4. Если сервер вернул HTML (visualize=true) — вставляем его как есть
            if (contentType && contentType.includes('text/html')) {
                const html = await response.text();
                resultsDiv.innerHTML = html;
                return;
            }

            // 5. Если не HTML — значит, JSON (visualize=false)
            const responseData = await response.json();
            const data = responseData.results;
            const csvFilename = responseData.csv_filename;

            // 6. Показываем JSON в красивом формате
            resultsDiv.innerHTML = `
                <h2>Результаты (JSON)</h2>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;

        } catch (err) {
            // 7. Ловим ЛЮБУЮ ошибку: сеть, сервер, парсинг, логика
            console.error("Ошибка:", err);  // ← Логируем в консоль для отладки
            resultsDiv.innerHTML = `
                <p style="color: red; font-weight: bold;">
                    Ошибка: ${err.message}
                </p>
            `;
        } finally {
            // 8. Включаем кнопку "Запустить" обратно — даже если была ошибка
            button.disabled = false;
        }
    });
});

// Вспомогательные функции
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
}
