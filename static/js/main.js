// 列表页 JS
document.addEventListener('DOMContentLoaded', function() {
    const selectAll = document.getElementById('select-all');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');
    const batchForm = document.getElementById('batch-form');

    // 全选功能
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('input[name="record_ids"]');
            checkboxes.forEach(cb => cb.checked = this.checked);
            toggleBatchButton();
        });
    }

    // 监听选项变化
    document.querySelectorAll('input[name="record_ids"]').forEach(function(cb) {
        cb.addEventListener('change', toggleBatchButton);
    });

    // 批量删除
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', function() {
            if (confirm('确定删除选中的记录？')) {
                batchForm.submit();
            }
        });
    }
});

function toggleBatchButton() {
    const checkboxes = document.querySelectorAll('input[name="record_ids"]:checked');
    const btn = document.getElementById('batch-delete-btn');
    if (btn) {
        btn.style.display = checkboxes.length > 0 ? 'inline-block' : 'none';
    }
}