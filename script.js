// script.js
document.addEventListener('DOMContentLoaded', () => {
    // Phần tử HTML chính
    const mathExpressionInput = document.getElementById('mathExpressionInput');
    const solveButton = document.getElementById('solveButton');
    const resultsSection = document.getElementById('resultsSection');
    const resultText = document.getElementById('resultText');
    const explanationText = document.getElementById('explanationText');

    // Phần tử cho thanh điều hướng và overlay
    const btnVersions = document.getElementById('btnVersions');
    const btnInstructions = document.getElementById('btnInstructions');
    const versionsSection = document.getElementById('versionsSection');
    const instructionsSection = document.getElementById('instructionsSection');
    const closeVersions = document.getElementById('closeVersions');
    const closeInstructions = document.getElementById('closeInstructions');

    // Hàm để mở overlay
    function openOverlay(overlayElement) {
        overlayElement.classList.remove('hidden');
        // Thêm class 'visible' để kích hoạt hiệu ứng CSS opacity
        setTimeout(() => {
            overlayElement.classList.add('visible');
        }, 10); // Một độ trễ nhỏ để đảm bảo display:block được áp dụng trước khi transition opacity
    }

    // Hàm để đóng overlay
    function closeOverlay(overlayElement) {
        overlayElement.classList.remove('visible'); // Bỏ class 'visible' để kích hoạt hiệu ứng opacity
        setTimeout(() => {
            overlayElement.classList.add('hidden'); // Sau khi transition, ẩn hoàn toàn
        }, 300); // Thời gian chờ bằng thời gian transition trong CSS
    }

    // Lắng nghe sự kiện click cho nút "AMS 1.0" (Versions)
    btnVersions.addEventListener('click', () => {
        openOverlay(versionsSection);
    });

    // Lắng nghe sự kiện click cho nút "Hướng dẫn" (Instructions)
    btnInstructions.addEventListener('click', () => {
        openOverlay(instructionsSection);
    });

    // Lắng nghe sự kiện click cho nút đóng Versions
    closeVersions.addEventListener('click', () => {
        closeOverlay(versionsSection);
    });

    // Lắng nghe sự kiện click cho nút đóng Instructions
    closeInstructions.addEventListener('click', () => {
        closeOverlay(instructionsSection);
    });

    // Lắng nghe sự kiện click bên ngoài nội dung overlay để đóng (tùy chọn)
    versionsSection.addEventListener('click', (event) => {
        if (event.target === versionsSection) { // Chỉ đóng nếu click trực tiếp vào nền mờ
            closeOverlay(versionsSection);
        }
    });

    instructionsSection.addEventListener('click', (event) => {
        if (event.target === instructionsSection) { // Chỉ đóng nếu click trực tiếp vào nền mờ
            closeOverlay(instructionsSection);
        }
    });


    // --- Logic giải toán (Không thay đổi) ---
    solveButton.addEventListener('click', async () => {
        const expression = mathExpressionInput.value.trim();

        if (expression === "") {
            alert("Please enter an equation:"); // Đã đổi ngôn ngữ cảnh báo
            return;
        }

        try {
            // Đảm bảo địa chỉ này khớp với cổng Backend Flask của bạn (thường là 5000)
            const response = await fetch('http://127.0.0.1:5000/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expression: expression })
            });

            const data = await response.json();

            if (data.success) {
                resultText