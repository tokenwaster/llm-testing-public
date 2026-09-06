const Experience = (() => {
  function el(tag, text, cls) { const node=document.createElement(tag); if(text!==undefined) node.textContent=text; if(cls) node.className=cls; return node; }
  function link(text,href,cls='action') { const a=el('a',text,cls); a.href=href; return a; }
  async function copy(text,status) {
    try { await navigator.clipboard.writeText(text); status.textContent='Copied. Ready to share.'; }
    catch { status.textContent='Copy is unavailable here. Select and copy the text below.';
      const field=el('textarea'); field.className='citation'; field.value=text; field.setAttribute('aria-label','Text to copy'); status.append(field); field.focus(); field.select(); }
  }
  function download(name,body,type) { const blob=new Blob([body],{type}); const url=URL.createObjectURL(blob); const a=link('',url); a.download=name; document.body.append(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),1000); }
  function csv(rows) { return rows.map(row=>row.map(v=>{let s=v===null||v===undefined?'':String(v); if(/^[=+@\-\t\r]/.test(s))s="'"+s; return '"'+s.replaceAll('"','""')+'"';}).join(',')).join('\r\n'); }
  function citation(version,asof) { return `Token Waster. ${document.title}. Suite ${version}; data as of ${asof.slice(0,10)}. ${location.href}`; }
  function paired(a,b,tids) {
    const differences=[]; let excluded=0,once=0;
    for(const tid of tids) {const x=a.cells[tid],y=b.cells[tid];
      if(!x||!y||x.score===null||y.score===null||!x.condition||x.condition!==y.condition){excluded++;continue;}
      differences.push(x.score-y.score); if(x.n===1||y.n===1)once++;
    }
    if(differences.length<8) return `Paired uncertainty unavailable: ${differences.length} matching tasks; at least 8 required. ${excluded} excluded for missing scores, task changes, unknown or differing conditions. This does not establish a tie.`;
    let seed=1729;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
    const n=differences.length, samples=[];
    for(let i=0;i<2000;i++){let sum=0;for(let j=0;j<n;j++)sum+=differences[Math.floor(random()*n)];samples.push(sum/n);}
    samples.sort((x,y)=>x-y);const lo=samples[49],hi=samples[1949],delta=differences.reduce((x,y)=>x+y,0)/n;
    return `Paired task bootstrap: A − B ${delta.toFixed(3)}, 95% interval ${lo.toFixed(3)} to ${hi.toFixed(3)} across ${n} matching tasks. ${excluded} excluded; ${once} pairs contain a single measurement. ${lo>0?'A leads on the matched subset.':hi<0?'B leads on the matched subset.':'The interval includes zero; that is not proof of equivalence.'} Conditional on this task set and recorded conditions; not a repeatability interval or adjusted for multiple comparisons.`;
  }
  return {el,link,copy,download,csv,citation,paired};
})();
