(function () {
  "use strict";
  const D = window.VERIFIED_SUITE_DATA;
  if (!D) return;

  function r10(v) {
    return Math.round(v / 10) * 10;
  }

  function fmt(v) {
    const n = r10(v);
    return n < 0 ? "-$" + Math.abs(n).toLocaleString("en-US") : "$" + n.toLocaleString("en-US");
  }

  // 1. Render SVG Line Charts on Projections Page
  function renderSvgChart(containerId, seriesList, yMaxOverride) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const W = 560, H = 250, padL = 68, padR = 18, padT = 16, padB = 32;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;
    const years = D.cupertino_projections.map(r => r.year);
    let maxVal = yMaxOverride || 0;
    if (!maxVal) {
      seriesList.forEach(s => s.values.forEach(v => { if (v > maxVal) maxVal = v; }));
      maxVal = maxVal * 1.08;
    }
    const xPos = i => padL + (i / (years.length - 1)) * plotW;
    const yPos = v => padT + plotH - (Math.max(0, v) / maxVal) * plotH;

    // Shade 2040-2050 inheritance window
    const idx2040 = years.indexOf(2040);
    const idx2050 = years.indexOf(2050);
    const winX = xPos(idx2040);
    const winW = xPos(idx2050) - winX;

    let gridHtml = `<rect x="${winX.toFixed(1)}" y="${padT}" width="${winW.toFixed(1)}" height="${plotH}" fill="#e0f2fe" opacity="0.55"/>`;
    for (let g = 0; g <= 4; g++) {
      const val = (maxVal / 4) * g;
      const y = yPos(val);
      const label = val >= 1000000 ? "$" + (val / 1000000).toFixed(1) + "M" : "$" + Math.round(val / 1000) + "k";
      gridHtml += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="#e2e8f0" stroke-width="1"/>`;
      gridHtml += `<text x="${padL - 6}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-size="10" fill="#64748b">${label}</text>`;
    }
    [2026, 2030, 2035, 2040, 2045, 2050].forEach(yr => {
      const idx = years.indexOf(yr);
      if (idx >= 0) {
        const x = xPos(idx);
        gridHtml += `<text x="${x.toFixed(1)}" y="${H - 10}" text-anchor="middle" font-size="10" fill="#475569">${yr}</text>`;
      }
    });

    let pathsHtml = "";
    seriesList.forEach(s => {
      const pts = s.values.map((v, i) => `${xPos(i).toFixed(1)},${yPos(v).toFixed(1)}`).join(" ");
      pathsHtml += `<polyline fill="none" stroke="${s.color}" stroke-width="2.4" points="${pts}"/>`;
    });

    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="auto" role="img" aria-label="Projection chart">${gridHtml}${pathsHtml}</svg>`;
  }

  renderSvgChart("chart-values", [
    { color: "#0284c7", values: D.cupertino_projections.map(r => r.fmv) },
    { color: "#059669", values: D.sf_projections.map(r => r.fmv) },
    { color: "#64748b", values: D.cupertino_projections.map(r => r.fbyv_prop13) }
  ]);

  renderSvgChart("chart-taxes", [
    { color: "#dc2626", values: D.cupertino_projections.map(r => r.tax_if_inherited_rent) },
    { color: "#d97706", values: D.cupertino_projections.map(r => r.tax_if_inherited_live) },
    { color: "#059669", values: D.cupertino_projections.map(r => r.tax_prop13_current) }
  ]);

  // 2. CSV Download on Projections Page
  const csvBtn = document.getElementById("btn-download-csv");
  if (csvBtn) {
    csvBtn.addEventListener("click", function () {
      const headers = [
        "year", "cup_fmv", "cup_fbyv_prop13", "cup_tax_prop13", "prop19_cap",
        "cup_tax_if_inherited_live", "cup_tax_if_inherited_rent", "cup_total_opex_if_live",
        "sf_fmv", "sf_fbyv_prop13", "sf_tax_prop13", "sf_total_opex", "sf_rent_2units", "sf_net_cashflow_2units"
      ];
      const lines = [headers.join(",")];
      D.cupertino_projections.forEach((c, idx) => {
        const s = D.sf_projections[idx];
        lines.push([
          c.year, c.fmv, c.fbyv_prop13, c.tax_prop13_current, c.prop19_cap,
          c.tax_if_inherited_live, c.tax_if_inherited_rent, c.total_opex_if_live,
          s.fmv, s.fbyv_prop13, s.tax_prop13_current, s.total_opex_prop13, s.gross_rent_2units_yr, s.net_cashflow_2units_prop13
        ].join(","));
      });
      const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "verified_projections_2026_2050_rounded10.csv";
      a.click();
    });
  }

  // 3. Interactive Scenario Simulator on Scenarios Page
  const elYear = document.getElementById("sim-year");
  const elHor = document.getElementById("sim-horizon");
  const elCupG = document.getElementById("sim-cup-g");
  const elPortR = document.getElementById("sim-port-r");
  const elTrust = document.getElementById("sim-trust");
  const tbody = document.getElementById("sim-results-tbody");
  const banner = document.getElementById("sim-verdict-banner");

  function runSimulator() {
    if (!tbody || !elYear) return;
    const inheritYr = parseInt(elYear.value, 10);
    const horizon = parseInt(elHor.value, 10);
    const gCup = parseFloat(elCupG.value) / 100.0;
    const rPort = parseFloat(elPortR.value) / 100.0;
    const isRevocable = elTrust.value === "revocable";

    document.getElementById("lbl-sim-year").textContent = String(inheritYr);
    document.getElementById("lbl-sim-horizon").textContent = String(horizon);
    document.getElementById("lbl-sim-cup-g").textContent = (gCup * 100).toFixed(1) + "%";
    document.getElementById("lbl-sim-port-r").textContent = (rPort * 100).toFixed(1) + "%";

    const t0 = inheritYr - 2026;
    const cFmv0 = 3100000 * Math.pow(1 + gCup, t0);
    const cFbyv0 = 550537 * Math.pow(1.02, t0);
    const steps = Math.floor((inheritYr - 2025) / 2);
    const p19Cap0 = 1044586 * Math.pow(1.035, 2 * steps);

    const cBaseLive0 = cFbyv0 + Math.max(0, cFmv0 - (cFbyv0 + p19Cap0));
    const cBaseRent0 = cFmv0;

    let day1SaleCash = cFmv0 * 0.95;
    if (!isRevocable) {
      // IRS Rev. Rul. 2023-2: carryover basis (~cFbyv0) triggers 37.1% combined Fed+NIIT+CA capital gains tax!
      const capGainTax = Math.max(0, day1SaleCash - cFbyv0) * 0.371;
      day1SaleCash -= capGainTax;
    }

    let s1Port = day1SaleCash, s2aCash = 0, s2bCash = 0, s3Cash = 0;
    let yr1CfS1 = 0, yr1CfS2a = 0, yr1CfS2b = 0, yr1CfS3 = 0;
    let yr1TaxLive = 0, yr1TaxRent = 0;

    for (let k = 0; k < horizon; k++) {
      const yr = inheritYr + k;
      const t = yr - 2026;
      const sfFbyv = 114248 * 1.02 * Math.pow(1.02, t);
      const sfParcel = 1110 * Math.pow(1.02, t);
      const sfRb = 90 * Math.pow(1.02, t);
      const sfTaxOwner = Math.max(0, sfFbyv - 7000) * 0.01181622 + sfParcel;
      const sfTaxNon = sfFbyv * 0.01181622 + sfParcel;
      const sfOpex = sfRb + 4440 * Math.pow(1.045, t) + 600 * Math.pow(1.035, t) + 3600 * Math.pow(1.04, t) + 12600 * Math.pow(1.028, t);
      const sfRent2 = 7150 * 12 * Math.pow(1.028, t);
      const sfUnit3 = 3600 * 12 * Math.pow(1.028, t) * 0.95;

      const sfAfOwner = (sfRent2 - (sfTaxOwner + sfOpex)) * 0.70;
      const sfAfNon2 = (sfRent2 - (sfTaxNon + sfOpex)) * 0.70;
      const sfAfAll3 = ((sfRent2 + sfUnit3) - (sfTaxNon + sfOpex * 1.12)) * 0.68;

      const cParcel = 950 * Math.pow(1.02, t);
      const cTaxLive = Math.max(0, cBaseLive0 * Math.pow(1.02, k) - 7000) * 0.011636 + cParcel;
      const cTaxRent = (cBaseRent0 * Math.pow(1.02, k)) * 0.011636 + cParcel;

      const cWater = 1560 * Math.pow(1.032, t);
      const cElec = yr < 2038 ? -240 * Math.pow(0.995, t) : 660 * Math.pow(1.035, t);
      const cInsLive = 2600 * Math.pow(1.04, t);
      const cInsRent = 3120 * Math.pow(1.04, t);
      const cMaint = 7800 * Math.pow(1.028, t);

      const cHoldLive = cTaxLive + cWater + cElec + cInsLive + cMaint;
      const cEffRent = (7000 * 12 * Math.pow(1.03, t)) * 0.87;
      const cRentNoi = cEffRent - (cTaxRent + cInsRent + cMaint);
      const cDepr = ((isRevocable ? cFmv0 : cFbyv0) * 0.30) / 27.5;
      const cRentAf = cRentNoi - Math.max(0, (cRentNoi - cDepr) * 0.35);

      const cf1 = sfAfOwner;
      const cf2a = sfAfNon2 - cHoldLive;
      const cf2b = sfAfAll3 - cHoldLive;
      const cf3 = sfAfOwner + cRentAf;

      if (k === 0) {
        yr1CfS1 = cf1; yr1CfS2a = cf2a; yr1CfS2b = cf2b; yr1CfS3 = cf3;
        yr1TaxLive = cTaxLive; yr1TaxRent = cTaxRent;
      }

      s1Port = s1Port * (1 + rPort) + cf1;
      s2aCash = s2aCash * (1 + rPort) + cf2a;
      s2bCash = s2bCash * (1 + rPort) + cf2b;
      s3Cash = s3Cash * (1 + rPort) + cf3;
    }

    const tEnd = (inheritYr + horizon) - 2026;
    const cFmvEnd = 3100000 * Math.pow(1 + gCup, tEnd);
    const sfFmvEnd = 1800000 * Math.pow(1.035, tEnd);
    const cNetEnd = cFmvEnd * 0.95;
    const basisStart = isRevocable ? cFmv0 : cFbyv0;
    const gainEnd = Math.max(0, cNetEnd - basisStart);
    const capTaxLive = Math.max(0, gainEnd - 250000) * 0.371;
    const cumDepr = ((basisStart * 0.30) / 27.5) * horizon;
    const capTaxRent = gainEnd * 0.371 + cumDepr * 0.421;

    const eqLive = cNetEnd - capTaxLive;
    const eqRent = cNetEnd - capTaxRent;

    const rows = [
      { id: "S1", label: "Sell Cupertino & Reinvest + Live in SF Unit 3", cash0: day1SaleCash, tax1: 0, cf1: yr1CfS1, portEnd: s1Port, total: s1Port + sfFmvEnd, src: '<a href="https://www.irs.gov/pub/irs-drop/rr-23-02.pdf" target="_blank" rel="noopener noreferrer">IRS Rev. Rul. 2023-2 / § 1014</a>' },
      { id: "S3", label: "Rent Out Cupertino (No Prop 19) + Live in SF Unit 3", cash0: 0, tax1: yr1TaxRent, cf1: yr1CfS3, portEnd: s3Cash, total: s3Cash + eqRent + sfFmvEnd, src: '<a href="https://boe.ca.gov/proptaxes/pdf/lta25015.pdf" target="_blank" rel="noopener noreferrer">CA BOE LTA 2025/015</a>' },
      { id: "S2B", label: "Live in Cupertino (Prop 19) + Rent All 3 SF Units", cash0: 0, tax1: yr1TaxLive, cf1: yr1CfS2b, portEnd: s2bCash, total: s2bCash + eqLive + sfFmvEnd, src: '<a href="https://www.boe.ca.gov/pdf/pub801.pdf" target="_blank" rel="noopener noreferrer">CA BOE Pub 801</a>' },
      { id: "S2A", label: "Live in Cupertino (Prop 19) + Keep SF Unit 3 Vacant", cash0: 0, tax1: yr1TaxLive, cf1: yr1CfS2a, portEnd: s2aCash, total: s2aCash + eqLive + sfFmvEnd, src: '<a href="https://www.irs.gov/publications/p523" target="_blank" rel="noopener noreferrer">IRS Pub 523 (§ 121)</a>' }
    ];

    rows.sort((a, b) => b.total - a.total);
    const best = rows[0];
    const runnerUp = rows[1];

    banner.innerHTML = `<strong>Simulated Winner (${inheritYr}–${inheritYr + horizon}): ${best.id} — ${best.label}</strong> · Builds <strong>${fmt(best.total)}</strong> in total household net worth, leading runner-up (${runnerUp.id}) by <strong>+${fmt(best.total - runnerUp.total)}</strong> (${isRevocable ? "Revocable Trust 100% § 1014 Step-Up active" : "WARNING: Irrevocable Trust carryover basis deducts 37.1% tax on sale!"}).`;

    tbody.innerHTML = rows.map((r, i) => `
      <tr${i === 0 ? ' style="background:#ecfdf5"' : ""}>
        <td><strong>${r.id}</strong>: ${r.label}${i === 0 ? ' <span class="badge badge-verified">#1 Net Worth</span>' : ""}</td>
        <td class="num">${fmt(r.cash0)}</td>
        <td class="num">${fmt(r.tax1)}</td>
        <td class="num">${fmt(r.cf1)}</td>
        <td class="num">${fmt(r.portEnd)}</td>
        <td class="num"><strong>${fmt(r.total)}</strong></td>
        <td>${r.src}</td>
      </tr>
    `).join("");
  }

  if (elYear) {
    [elYear, elHor, elCupG, elPortR, elTrust].forEach(el => el.addEventListener("input", runSimulator));
    runSimulator();
  }
})();
