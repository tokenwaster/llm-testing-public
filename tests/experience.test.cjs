const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const context = {};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../harness/presentation/experience.js'), 'utf8') + '\nthis.api=Experience;', context);
const {csv, paired} = context.api;

test('CSV preserves newlines and quotes while neutralizing spreadsheet formulas', () => {
  assert.equal(csv([['a,b', '=1+1', null], ['"quoted"', 'line\nbreak', 0]]),
    '"a,b","\'=1+1",""\r\n"""quoted""","line\nbreak","0"');
});

test('paired uncertainty refuses unknown conditions and is deterministic on matching tasks', () => {
  const ids = Array.from({length: 12}, (_, i) => 't' + i);
  const a = {cells: {}}, b = {cells: {}};
  ids.forEach(t => { a.cells[t] = {score: 1, n: 2, condition: 'same'}; b.cells[t] = {score: 0.7, n: 1, condition: 'same'}; });
  const first = paired(a, b, ids);
  assert.equal(paired(a, b, ids), first);
  assert.match(first, /A leads on the matched subset/);
  assert.match(first, /12 pairs contain a single measurement/);
  ids.forEach(t => { b.cells[t].condition = null; });
  assert.match(paired(a, b, ids), /unavailable: 0 matching tasks/);
});
