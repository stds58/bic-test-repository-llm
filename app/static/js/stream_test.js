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
        outputDiv.innerText = "Подключение к модели...\n";

        try {
            const response = await fetch("/api/benchmark", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    prompt: prompt,
                    model: model,
                    max_tokens: maxTokens,
                    stream: true
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                let lines = buffer.split("\n\n");
                buffer = lines.pop();

                for (let line of lines) {
                    if (line.trim() === "[DONE]") {
                        outputDiv.innerText += "\n\nГенерация завершена.";
                        startBtn.disabled = false;
                        return;
                    }

                    if (line.startsWith(" ")) {
                        line = line.slice(1);
                    }

                    if (line) {
                        try {
                            const chunk = JSON.parse(line);
                            const content = chunk.choices?.[0]?.delta?.content || "";
                            if (content) {
                                outputDiv.innerText += content;
                                outputDiv.scrollTop = outputDiv.scrollHeight;
                            }
                        } catch (e) {
                            console.warn("Не удалось распарсить чанк:", line);
                        }
                    }
                }
            }

        } catch (err) {
            console.error("Ошибка:", err);
            outputDiv.innerText += "\n\nОшибка: " + err.message;
            startBtn.disabled = false;
        }
    }
});
