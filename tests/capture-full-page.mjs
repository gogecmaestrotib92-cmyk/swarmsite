import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';
const exec=promisify(execFile),dir=fs.mkdtempSync(path.join(os.tmpdir(),'capture-full-test-'));
const server=http.createServer((req,res)=>{res.writeHead(200,{'content-type':'text/html'});res.end(`<!doctype html><title>A real restaurant</title><main><h1>A real restaurant</h1><p>${'Food and friends in the local restaurant. '.repeat(20)}</p><section style="height:3257px;background:linear-gradient(red,blue)">Long page content</section></main>`)});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try {
 const url=`http://127.0.0.1:${server.address().port}/`;
 await exec(process.execPath,['lib/pipeline/capture.mjs',url,'--out',dir,'--chrome',process.env.CHROME_PATH||'/usr/bin/google-chrome'],{timeout:120000,maxBuffer:1024*1024});
 const slug=url.replace(/^https?:\/\//,'').replace(/[^a-z0-9.-]+/gi,'_').replace(/_+$/,'').toLowerCase();
 const file=path.join(dir,slug,'before-full.jpg');assert.ok(fs.existsSync(file));
 browser=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined});const page=await browser.newPage();await page.goto(pathToFileURL(file).href);
 const size=await page.locator('img').evaluate(i=>({w:i.naturalWidth,h:i.naturalHeight}));assert.equal(size.w,1440);assert.ok(size.h>3000,`capture was only ${size.h}px tall`);
 console.log(`Full-page capture includes content beyond viewport: ${size.w}×${size.h}`);
}finally{if(browser)await browser.close();server.close();fs.rmSync(dir,{recursive:true,force:true})}
