/* Customers tab: who buys, and how. Built from customer_patterns.ipynb.
   Uses the helpers defined in app.js ($, R, plot, base, kpi, fmt, esc, color, COLORS, current). */
'use strict';

// Same age groups as the notebook (dataset ages run from 18 to 64)
const AGE_GROUPS = [
  { label: '18-25', min: 18, max: 25 },
  { label: '26-35', min: 26, max: 35 },
  { label: '36-45', min: 36, max: 45 },
  { label: '46-55', min: 46, max: 55 },
  { label: '56-64', min: 56, max: 64 },
];
const ageGroup = r => (AGE_GROUPS.find(g => r.age >= g.min && r.age <= g.max) || { label: 'Other' }).label;

// Unit prices are 25, 30, 50, 300 or 500, so they split cleanly into two tiers
const HIGH_PRICE = 300;
const TIER_COLORS = { 'Share of transactions': '#a8cfb8', 'Share of revenue': '#207969' };

function customers() {
  const rows = current;
  const s = R.stats(rows);
  $('customerEmpty').hidden = !!s.count;
  $('customerCharts').hidden = !s.count;
  const highRows = rows.filter(r => r.price >= HIGH_PRICE);
  const high = R.stats(highRows);
  const people = new Set(rows.map(r => r.customer)).size;
  const avgAge = s.count ? rows.reduce((t, r) => t + r.age, 0) / s.count : 0;

  $('customerKpis').innerHTML =
    kpi('Customers', fmt(people), 'Each buys once in this dataset') +
    kpi('Average age', fmt(avgAge, 1), 'Of customers in this selection') +
    kpi('Average purchase', fmt(s.aov, 2), 'Revenue ÷ transactions') +
    kpi('High-price revenue', s.revenue ? fmt(high.revenue / s.revenue * 100, 1) + '%' : '–', 'Items priced 300 or more');
  if (!s.count) return;

  const cats = Object.keys(COLORS).filter(c => rows.some(r => r.category === c));

  // 1. Average purchase by age group
  const ages = R.group(rows, ageGroup);
  const byAge = AGE_GROUPS.map(g => ages.find(a => a.key === g.label)).filter(Boolean);
  plot('ageSpend', [{
    x: byAge.map(a => a.key), y: byAge.map(a => a.aov), type: 'bar',
    marker: { color: '#207969', cornerradius: 5 },
    text: byAge.map(a => fmt(a.aov)), textposition: 'outside', cliponaxis: false,
    customdata: byAge.map(a => a.count),
    hovertemplate: 'Age %{x}<br>Average purchase: %{y:,.2f}<br>Transactions: %{customdata}<extra></extra>',
  }], { margin: { ...base.margin, t: 30 }, xaxis: { ...base.xaxis, type: 'category', title: { text: 'Age group', font: { size: 10 } } }, yaxis: { ...base.yaxis, rangemode: 'tozero' }, bargap: .45 });

  // 2. Category mix within each age group (each group's bars add up to 100%)
  plot('ageMix', cats.map(c => ({
    name: c, type: 'bar',
    x: byAge.map(a => a.key),
    y: byAge.map(a => {
      const groupRows = rows.filter(r => ageGroup(r) === a.key);
      return R.stats(groupRows.filter(r => r.category === c)).revenue / a.revenue * 100;
    }),
    marker: { color: color(c), cornerradius: 4 },
    hovertemplate: esc(c) + ' · age %{x}<br>%{y:.1f}% of the group\'s revenue<extra></extra>',
  })), { barmode: 'group', bargap: .3, bargroupgap: .08, showlegend: true, legend: { orientation: 'h', y: -.25, font: { size: 9 } }, margin: { ...base.margin, b: 70 }, xaxis: { ...base.xaxis, type: 'category' }, yaxis: { ...base.yaxis, ticksuffix: '%', rangemode: 'tozero' } });

  // 3. Revenue by gender and category
  const genders = [...new Set(rows.map(r => r.gender))].sort();
  plot('genderMix', cats.map(c => ({
    name: c, type: 'bar', x: genders,
    y: genders.map(g => R.stats(rows.filter(r => r.gender === g && r.category === c)).revenue),
    marker: { color: color(c), cornerradius: 4 },
    hovertemplate: esc(c) + ' · %{x}<br>Revenue: %{y:,.0f}<extra></extra>',
  })), { barmode: 'group', bargap: .35, bargroupgap: .08, showlegend: true, legend: { orientation: 'h', y: -.25, font: { size: 9 } }, margin: { ...base.margin, b: 70 }, xaxis: { ...base.xaxis, type: 'category' }, yaxis: { ...base.yaxis, rangemode: 'tozero' } });

  // 4. Price tiers: share of transactions vs share of revenue
  const low = R.stats(rows.filter(r => r.price < HIGH_PRICE));
  const tiers = ['25-50', '300-500'], tierStats = [low, high];
  plot('priceTiers', Object.keys(TIER_COLORS).map(name => ({
    name, type: 'bar', orientation: 'h', y: tiers,
    x: tierStats.map(t => name === 'Share of revenue' ? t.revenue / s.revenue * 100 : t.count / s.count * 100),
    marker: { color: TIER_COLORS[name], cornerradius: 4 },
    text: tierStats.map(t => fmt(name === 'Share of revenue' ? t.revenue / s.revenue * 100 : t.count / s.count * 100, 1) + '%'),
    textposition: 'auto',
    hovertemplate: 'Unit price %{y}<br>' + name + ': %{x:.1f}%<extra></extra>',
  })), { barmode: 'group', bargap: .35, showlegend: true, legend: { orientation: 'h', y: -.3, font: { size: 9 } }, margin: { l: 70, r: 25, t: 20, b: 70 }, xaxis: { ...base.yaxis, ticksuffix: '%', range: [0, 100] }, yaxis: { ...base.xaxis, type: 'category', title: { text: 'Unit price', font: { size: 10 } } } });

  $('customerInsight').innerHTML = '<span class="icon">◉</span><div><strong>Price, not people, drives revenue.</strong> Items priced 300 or more are ' +
    fmt(high.count / s.count * 100, 1) + '% of transactions but ' + fmt(high.revenue / s.revenue * 100, 1) +
    '% of revenue. Differences between age groups and genders are small.' +
    '<small>Statistical tests on all 1,000 transactions (customer_patterns.ipynb) found none of the age, gender or weekday differences significant (every p-value above 0.2), so treat these gaps as descriptive.</small></div>';
}
