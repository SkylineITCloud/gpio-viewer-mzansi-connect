// GPIOViewer 1.7.1 SSE contract. Delta frames must merge, never clear other pins.
function applyFrame(cache, frame) {
  if (!frame || typeof frame !== 'object' || Array.isArray(frame)) return [];
  const changed=[];
  for (const [key,value] of Object.entries(frame)) {
    if (!/^\d+$/.test(key) || !value || typeof value!=='object') continue;
    if (![value.s,value.v,value.t].every(Number.isFinite) || ![0,1,2].includes(value.t)) continue;
    cache[key]={s:value.s,v:value.v,t:value.t}; changed.push(Number(key));
  }
  return changed;
}
function describeValue(sample) {
  if (!sample) return 'WAITING';
  if (sample.t===0) return sample.v===0?'LOW':'HIGH';
  return (sample.t===1?'PWM ':'ADC ')+sample.v;
}
if(typeof module!=='undefined') module.exports={applyFrame,describeValue};
