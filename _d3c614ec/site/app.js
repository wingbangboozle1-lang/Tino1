document.addEventListener('DOMContentLoaded', () => {
  // Inheritance year switcher (2040 / 2045 / 2050)
  document.querySelectorAll('[data-year-group]').forEach(group => {
    const buttons = group.querySelectorAll('[data-yr-btn]');
    const targetName = group.getAttribute('data-year-group');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const yr = btn.getAttribute('data-yr-btn');
        buttons.forEach(b => b.classList.toggle('active', b === btn));
        document.querySelectorAll(`[data-yr-panel="${targetName}"]`).forEach(p => {
          p.hidden = p.getAttribute('data-yr') !== yr;
        });
      });
    });
  });

  // 50-year projection table decade filter
  const decBtns = document.querySelectorAll('[data-decade-btn]');
  if (decBtns.length) {
    decBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const dec = btn.getAttribute('data-decade-btn');
        decBtns.forEach(b => b.classList.toggle('active', b === btn));
        document.querySelectorAll('#proj50 tbody tr').forEach(tr => {
          const y = parseInt(tr.children[0].textContent.trim(), 10);
          if (dec === 'all') tr.hidden = false;
          else if (dec === 'milestones') tr.hidden = ![2026,2030,2035,2040,2044,2045,2046,2050,2055,2060,2065,2070,2076].includes(y);
          else {
            const start = parseInt(dec, 10);
            tr.hidden = !(y >= start && y <= start + 9);
          }
        });
      });
    });
  }

  // Interactive Cash Headroom Estimator ($10-rounded)
  const cashInput = document.getElementById('cash-bequest-input');
  const cashYr = document.getElementById('cash-year-select');
  const cashMode = document.getElementById('cash-mode-select');
  const cashOut = document.getElementById('cash-calc-output');
  if (cashInput && cashYr && cashMode && cashOut) {
    const presets = JSON.parse(cashOut.getAttribute('data-presets'));
    const r10 = x => Math.round(x / 10) * 10;
    const fmt = x => '$' + r10(x).toLocaleString('en-US');
    const update = () => {
      const cash = Math.max(0, r10(parseFloat(cashInput.value || '0')));
      const row = presets[cashYr.value];
      const excl = cashMode.value === 'married' ? row.married : (cashMode.value === 'cut50' ? row.cut50 : row.single);
      const gross = row.cup_fmv + cash;
      const taxable = Math.max(0, gross - excl);
      const fedTax = r10(taxable * 0.40);
      const roomLeft = Math.max(0, excl - gross);
      cashOut.innerHTML =
        `<strong>${cashYr.value} Result ($10-rounded):</strong> Gross Estate = ${fmt(gross)} ` +
        `(Property A ${fmt(row.cup_fmv)} + Cash ${fmt(cash)}; Property B = $0 already owned) · ` +
        `Applicable Federal Exclusion = ${fmt(excl)} · ` +
        `Estimated Federal Estate Tax (40%) = <strong>${fmt(fedTax)}</strong> · ` +
        `California Estate/Inheritance Tax = <strong>$0</strong> · ` +
        `Remaining Tax-Free Room = <strong>${fmt(roomLeft)}</strong>.`;
    };
    cashInput.addEventListener('input', update);
    cashYr.addEventListener('change', update);
    cashMode.addEventListener('change', update);
    update();
  }
});
