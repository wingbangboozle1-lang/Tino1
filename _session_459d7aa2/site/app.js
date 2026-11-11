document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-tab-group]').forEach(group => {
    const groupName = group.getAttribute('data-tab-group');
    const buttons = group.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-target');
        buttons.forEach(b => b.classList.toggle('active', b === btn));
        document.querySelectorAll(`[data-tab-panel="${groupName}"]`).forEach(panel => {
          panel.style.display = (panel.id === target) ? '' : 'none';
        });
      });
    });
  });

  document.querySelectorAll('[data-table-filter]').forEach(input => {
    const tableId = input.getAttribute('data-table-filter');
    const table = document.getElementById(tableId);
    if (!table) return;
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      table.querySelectorAll('tbody tr').forEach(tr => {
        tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  });
});
