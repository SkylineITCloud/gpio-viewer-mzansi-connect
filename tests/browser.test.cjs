// Real Edge rendering with mocked device transport. No hardware claims.
let pw;try{pw=require('playwright');}catch{pw=require('../../tmp/zek03-qa/node_modules/playwright');}
const {chromium}=pw;
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.BROWSER_PATH||(process.platform==='win32'?'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe':chromium.executablePath()),headless:true});
 fs.mkdirSync('test-results',{recursive:true});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const html=fs.readFileSync(path.join(__dirname,'../web/index.html'),'utf8');
 await page.route(/^http:\/\/192\.168\.101\.50(?::8080)?\//,async route=>{
  const url=route.request().url();if(url.includes('/api/status'))return route.fulfill({json:{deviceId:'TEST-DEVICE',version:'test-fixture',gpioViewer:{active:true,samplingMs:250}}});
  if(url.includes('/pinmodes'))return route.fulfill({json:[{pin:'3',mode:'2'},{pin:'20',mode:'1'},{pin:'8',mode:'2'}],headers:{'Access-Control-Allow-Origin':'*'}});
  return route.fulfill({body:html,contentType:'text/html'});
 });
 await page.addInitScript(()=>{window.sources=[];window.EventSource=class{constructor(url){this.url=url;this.handlers={};this.closed=false;window.sources.push(this);setTimeout(()=>this.onopen?.(),10);}addEventListener(n,f){this.handlers[n]=f;}close(){this.closed=true;}};});
 await page.goto('http://192.168.101.50/gpio-mzansi');
 await page.locator('#key').fill('test-key');await page.locator('#connect').click();await page.waitForSelector('#viewer:not([hidden])');
 await page.waitForFunction(()=>window.sources.length===1);
 await page.waitForFunction(()=>document.querySelector('[data-id="left-1"]').textContent.includes('OUTPUT'));
 const frame=async data=>page.evaluate(d=>window.sources.at(-1).handlers['gpio-state']({data:JSON.stringify(d)}),data);
 await frame({'3':{s:256,v:1,t:0},'20':{s:0,v:0,t:0},'8':{s:0,v:0,t:0}});
 await frame({'20':{s:256,v:1,t:0}});
 assert.match(await page.locator('[data-id="left-1"]').innerText(),/HIGH/,'unchanged HIGH survives delta');
 await page.locator('#right-4 .ring').click();assert.match(await page.locator('#pinTitle').innerText(),/TX \/ GPIO21/);
 await page.locator('#right-6 .ring').click();assert.match(await page.locator('#pinDescription').innerText(),/No software voltage measurement/);
 await page.locator('#left-1 .ring').click();await page.screenshot({path:'test-results/desktop.png',fullPage:true});
 await page.locator('#pause').click();await frame({'3':{s:0,v:0,t:0}});assert.match(await page.locator('[data-id="left-1"]').innerText(),/HIGH/);
 await page.locator('#pause').click();await page.waitForFunction(()=>window.sources.length===2);await frame({'3':{s:0,v:0,t:0}});assert.match(await page.locator('[data-id="left-1"]').innerText(),/LOW/);
 await page.evaluate(()=>window.sources.at(-1).onerror());assert.match(await page.locator('#connection').innerText(),/Disconnected/);assert.match(await page.locator('#left-1 .pin-state').textContent(),/STALE/);
 await page.waitForFunction(()=>window.sources.length===3);await frame({'3':{s:256,v:1,t:0}});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'test-results/mobile.png',fullPage:true});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'no mobile horizontal overflow');
 await page.locator('#boardSelect').selectOption('generic');assert.equal(await page.locator('#board').isVisible(),false);
 await page.locator('#logout').click();assert.equal(await page.evaluate(()=>sessionStorage.getItem('mzansiKey')),null);
 assert.equal(await page.locator('#login').isVisible(),true);assert.deepEqual(errors,[]);
 await browser.close();console.log('PASS: Edge live transport fixture, deltas, power pins, pause/resume, stale/reconnect, mobile, logout');
})().catch(e=>{console.error(e);process.exit(1);});
