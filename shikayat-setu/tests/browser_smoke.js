// Optional browser smoke test. Use ONLY with a fresh disposable database.
// See TESTING.md for setup and required environment variables.
const puppeteer=require('puppeteer-core');
const args=process.env.CHROMIUM_SERVERLESS === '1' ? require('@sparticuz/chromium').args : ['--no-sandbox', '--disable-setuid-sandbox'];
const executablePath=process.env.CHROMIUM_EXECUTABLE_PATH;
const testRoll=process.env.SHIKAYAT_TEST_ROLL || 'MCA2026996';
if (!executablePath) throw new Error('Set CHROMIUM_EXECUTABLE_PATH to a compatible Chromium/Chrome executable.');
if (process.env.SHIKAYAT_DISPOSABLE_DB_CONFIRMED !== '1') throw new Error('This test creates accounts and complaints; point the app at a disposable database and set SHIKAYAT_DISPOSABLE_DB_CONFIRMED=1.');
(async()=>{
 const b=await puppeteer.launch({executablePath, args,headless:true});
 const pg=await b.newPage(), root=process.env.SHIKAYAT_TEST_URL || 'http://127.0.0.1:5014'; let errors=[], checked=0, external=[];
 pg.on('pageerror',e=>errors.push('JS '+e.message));
 pg.on('response',r=>{if(r.status()>=500) errors.push('HTTP '+r.status()+' '+r.url());});
 pg.on('request',r=>{if(r.url().startsWith('http') && !r.url().startsWith(root))external.push(r.url())});
 async function view(path){let r=await pg.goto(root+path,{waitUntil:'networkidle0'});if(r.status()!==200)throw Error(`${path}: HTTP ${r.status()}`);checked++;let over=await pg.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth,off:[...document.querySelectorAll('body *')].filter(x=>x.getBoundingClientRect().right>innerWidth+1&&!x.closest('.table-wrap')&&!x.closest('.sidebar')).slice(0,3).map(x=>x.tagName+'.'+x.className)}));if(over.scroll>over.viewport) errors.push('Overflow '+path+' '+JSON.stringify(over));}
 async function login(u,p){await pg.deleteCookie(...await pg.cookies(root));await view('/login');await pg.type('#login-user',u);await pg.type('#login-pass',p);await Promise.all([pg.waitForNavigation(),pg.click('.auth-btn')]);if(!pg.url().endsWith('/dashboard'))throw Error('login '+u)}
 async function submit(sel){await Promise.all([pg.waitForNavigation({waitUntil:'networkidle0'}),pg.$eval(sel,f=>f.requestSubmit())])}
 await pg.setViewport({width:390,height:844});await view('/register');await pg.type('#reg-name','Deep Browser Student');await pg.type('#reg-roll',testRoll);await pg.type('#reg-email','test@example.com');await pg.type('#reg-phone','9876543210');await pg.type('#reg-pwd','testpass');await pg.type('#reg-pwd2','testpass');await submit('.auth-card form');if(!pg.url().endsWith('/login'))throw Error('registration failed');
 await login(testRoll,'testpass');await view('/lodge');await pg.type('#lodge-title','Hostel room furniture broken');await pg.type('#lodge-desc','Hostel room furniture is broken and requires repair.');await pg.select('#lodge-cat','5');await pg.waitForSelector('#route-preview.show');await submit('#lodge-form');let path=await pg.$eval('a[href^="/complaint/"]',e=>e.getAttribute('href'));await view(path);
 await login('hostel.officer','officer123');await view(path);await submit('form[action$="/acknowledge"]');await submit('form[action$="/progress"]');await pg.type('#resolve-remark','Repaired and tested the furniture.');await submit('form[action$="/resolve"]');
 await login(testRoll,'testpass');await view(path);await pg.type('#reopen-reason','The repair failed again.');await submit('form[action$="/reopen"]');await login('hostel.officer','officer123');await view(path);await pg.type('#resolve-remark','Furniture replaced and checked.');await submit('form[action$="/resolve"]');await login(testRoll,'testpass');await view(path);await pg.type('#fb-comment','Now it works well.');await submit('form[action$="/feedback"]');
 await pg.deleteCookie(...await pg.cookies(root));await view('/track');await pg.type('#track-code',path.split('/').pop());await pg.type('#track-roll',testRoll);await submit('form');if(!(await pg.content()).includes('Closed'))throw Error('tracking failed');
 for(let width of [320,390,768,1366,1920]){
  await pg.setViewport({width,height:900});await pg.deleteCookie(...await pg.cookies(root));for(let p of ['/login','/register','/track'])await view(p);
  await login(testRoll,'testpass');for(let p of ['/dashboard','/lodge','/my-complaints','/track','/change-password',path])await view(p);
  await login('hostel.officer','officer123');for(let p of ['/dashboard','/queue','/track','/change-password',path])await view(p);
  await login('admin','admin123');for(let p of ['/dashboard','/queue','/console','/users','/change-password','/reports?report=pendency','/reports?report=sla','/reports?report=restime','/reports?report=trend','/reports?report=feedback','/reports?report=routing',path])await view(p);
 }
 await pg.setViewport({width:1366,height:900});await view('/users');if(await pg.$eval('#off-pwd',e=>e.type)!=='password')throw Error('password should be masked');await pg.click('[data-pwd-toggle]');if(await pg.$eval('#off-pwd',e=>e.type)!=='text')throw Error('password toggle show');await pg.click('[data-pwd-toggle]');if(await pg.$eval('#off-pwd',e=>e.type)!=='password')throw Error('password toggle hide');
 await pg.type('[data-filter-table="#users-table"]','no-such-officer-xyzz');let visible=await pg.$$eval('#users-table tbody tr',rs=>rs.filter(r=>getComputedStyle(r).display!=='none').length);if(visible!==0)throw Error('user filter returned '+visible);
 await view('/dashboard');await pg.$eval('[aria-label="Toggle dark mode"]',e=>e.click());let theme=await pg.evaluate(()=>document.documentElement.classList.contains('dark'));await view('/console');if((await pg.evaluate(()=>document.documentElement.classList.contains('dark')))!==theme)throw Error('theme failed to persist');
 await pg.type('[data-filter-table="#console-table"]','no-such-complaint-xyzz');if(!(await pg.$eval('#console-count',e=>e.textContent)).startsWith('0 of'))throw Error('console filter count');
 await view('/reports?report=trend');await pg.evaluate(()=>{window.print=()=>window.__printCalled=true});await pg.click('[data-print]');if(!await pg.evaluate(()=>window.__printCalled))throw Error('print button');
 await pg.setViewport({width:794,height:1123});await pg.emulateMediaType('print');
 for(let report of ['pendency','sla','restime','trend','feedback','routing']){
  await view('/reports?report='+report);
  let layout=await pg.evaluate(()=>[...document.querySelectorAll('table.tbl')].map(t=>({table:t.getBoundingClientRect().right,head:t.querySelector('thead').getBoundingClientRect().top,row:t.querySelector('tbody tr')?.getBoundingClientRect().top})));
  if(layout.some(x=>x.table>794+1 || (x.row!==undefined && x.head>x.row)))throw Error('Invalid print layout '+report+' '+JSON.stringify(layout));
  if((await pg.pdf({format:'A4',printBackground:true,preferCSSPageSize:true})).length<1000)throw Error('Empty print PDF '+report);
 }
 await pg.emulateMediaType(null);
 await pg.setViewport({width:390,height:844});await view('/dashboard');await pg.click('.hamburger');if(!await pg.evaluate(()=>document.body.classList.contains('nav-open')))throw Error('drawer did not open');await pg.keyboard.press('Escape');if(await pg.evaluate(()=>document.body.classList.contains('nav-open')))throw Error('drawer did not close');
 console.log('Checked pages:',checked,'across 5 widths; registration, full lifecycle including reopen, tracking, filters, dark theme, password toggle, six A4 PDF renders and mobile navigation passed.');console.log('Browser issues:',errors,'External requests:',external);await b.close();if(errors.length||external.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
