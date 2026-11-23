/* Export the generated editable pages with the actual diagrams.net web engine.
 * Set DRAWIO_WEBAPP to the src/main/webapp folder of a draw.io checkout.
 * Install puppeteer-core and @sparticuz/chromium; see DIAGRAMS.md. */
const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');
const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium').default;
const base = __dirname;
const inputs = {
  'fig-erd': ['fig-erd','fig-erd-b','fig-erd-c'],
  'fig-usecase': ['fig-usecase-student','fig-usecase-officer','fig-usecase-administrator','fig-usecase-public-visitor'],
  'fig-class': ['fig-class','fig-class-b'],
  'fig-activity': ['fig-activity','fig-activity-b','fig-activity-c','fig-activity-d','fig-activity-e'],
  'fig-deployment': ['fig-deployment'],
  'fig-modules': ['fig-modules']
};
(async () => {
  if (!process.env.DRAWIO_WEBAPP) throw new Error('Set DRAWIO_WEBAPP to the diagrams.net webapp directory');
  const browser = await puppeteer.launch({headless:true, executablePath:await chromium.executablePath(), args:[...chromium.args,'--allow-file-access-from-files']});
  try {
    const page = await browser.newPage();
    await page.setViewport({width:1600,height:1700,deviceScaleFactor:1.5});
    const app = pathToFileURL(path.join(process.env.DRAWIO_WEBAPP,'index.html')).href+'?offline=1&ui=min';
    await page.goto(app,{waitUntil:'load',timeout:30000});
    await page.waitForFunction('typeof Graph !== "undefined" && typeof mxCodec !== "undefined"');
    for (const [file,names] of Object.entries(inputs)) {
      const xml=fs.readFileSync(path.join(base,'diagrams',file+'.drawio'),'utf8');
      for (let index=0;index<names.length;index++) {
        const size=await page.evaluate(({xml,index})=>{
          document.body.innerHTML='';
          const doc=mxUtils.parseXml(xml);
          const model=doc.getElementsByTagName('diagram')[index].getElementsByTagName('mxGraphModel')[0];
          const w=Number(model.getAttribute('pageWidth')),h=Number(model.getAttribute('pageHeight'));
          const container=document.createElement('div');container.id='render';
          Object.assign(container.style,{position:'absolute',left:'0',top:'0',overflow:'hidden',background:'white',width:w+'px',height:h+'px'});
          document.body.appendChild(container);
          const graph=new Graph(container);graph.setEnabled(false);
          // Isolate each page: IDs are reused across pages.
          const isolated=mxUtils.parseXml(mxUtils.getXml(model));
          new mxCodec(isolated).decode(isolated.documentElement,graph.getModel());
          graph.refresh();graph.view.validate();
          return {w,h};
        },{xml,index});
        if (size.w>1600 || size.h>1700) throw new Error('Page exceeds rendering viewport');
        await page.screenshot({path:path.join(base,'images',names[index]+'.png'),clip:{x:0,y:0,width:size.w,height:size.h}});
        console.log(names[index]+'.png');
      }
    }
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1});
