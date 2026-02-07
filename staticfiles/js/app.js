document.addEventListener('DOMContentLoaded', () => {

    // Закрытие по крестику
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.parentElement.style.display = 'none';
        });
    });

    // Автоматическое исчезновение через 3 секунды
    setTimeout(() => {
        document.querySelectorAll('.message').forEach(msg => {
            msg.classList.add('fade-out');
            setTimeout(() => msg.remove(), 300);
        });
    }, 3000);

});
