// script.js
document.addEventListener('DOMContentLoaded', () => {
    const mathExpressionInput = document.getElementById('mathExpressionInput');
    const solveButton = document.getElementById('solveButton');
    const resultsSection = document.getElementById('resultsSection');
    const resultText = document.getElementById('resultText');
    const explanationText = document.getElementById('explanationText');

    solveButton.addEventListener('click', async () => {
        const expression = mathExpressionInput.value.trim();

        if (expression === "") {
            alert("Please enter an equation:");
            return;
        }

        try {
            // ĐÂY LÀ CÁCH JAVASCRIPT GIAO TIẾP VỚI BACKEND PYTHON CỦA BẠN
            // Nó gửi một yêu cầu HTTP POST đến địa chỉ mà backend Python đang chạy.
            const response = await fetch('http://127.0.0.1:8000/solve', { // Thay 5000 bằng 8000
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ expression: expression })
})

            const data = await response.json(); // Nhận phản hồi JSON từ Backend

            if (data.success) {
                resultText.textContent = data.result;
                explanationText.textContent = data.explanation;
                resultsSection.classList.remove('hidden'); // Hiển thị phần kết quả
            } else {
                resultText.textContent = "Error: " + data.message;
                explanationText.textContent = data.explanation || "Không thể giải quyết phép tính này.";
                resultsSection.classList.remove('hidden');
            }

        } catch (error) {
            resultText.textContent = "Something went wrong!";
            explanationText.textContent = "Something went wrong!";
            resultsSection.classList.remove('hidden');
            console.error("Error when sending command:", error);
        }
    });
});