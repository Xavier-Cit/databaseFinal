// 在线学习平台 JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // 自动关闭提示框
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            new bootstrap.Alert(alert).close();
        });
    }, 5000);
});
