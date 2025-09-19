document.addEventListener('DOMContentLoaded', function () {
    const startBtn = document.getElementById('startBtn');
    const outputDiv = document.getElementById('output');

    startBtn.addEventListener('click', startStream);

    async function startStream() {
        const prompt = document.getElementById('prompt').value.trim();
        const model = document.getElementById('model').value.trim();
        const maxTokens = parseInt(document.getElementById('max_tokens').value, 10);

        if (!prompt || !model) {
            alert('Пожалуйста, заполните промпт и модель.');
            return;
        }

        startBtn.disabled = true;
        outputDiv.textContent = "Подключение к модели...\n";

        try {
            const response = await fetch("/generate?stream=true", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    prompt: prompt,
                    model: model,
                    max_tokens: maxTokens
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";
            let fullText = ""; // ← НАКОПИТЕЛЬ ВСЕГО ТЕКСТА (новая строка!)

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                let lines = buffer.split("\n\n");
                buffer = lines.pop();

                for (let line of lines) {
                    if (line.trim() === "[DONE]") {
                        outputDiv.textContent += "\n\nГенерация завершена.";
                        startBtn.disabled = false;
                        return;
                    }

                    if (line.trim()) {
                        // ДОБАВЛЯЕМ СИМВОЛЫ В БУФЕР
                        fullText += line;

                        // ОЧИЩАЕМ ЛИШНИЕ ПРОБЕЛЫ: заменяем 2+ пробела на 1
                        let cleaned = fullText.replace(/\s+/g, " ").trim();

                        // ОБНОВЛЯЕМ ТОЛЬКО ЕСЛИ ИЗМЕНИЛОСЬ
                        if (outputDiv.textContent !== cleaned) {
                            outputDiv.textContent = cleaned;
                            outputDiv.scrollTop = outputDiv.scrollHeight;
                        }
                    }
                }
            }

        } catch (err) {
            console.error("Ошибка:", err);
            outputDiv.textContent += "\n\nОшибка: " + err.message;
            startBtn.disabled = false;
        }
    }
});