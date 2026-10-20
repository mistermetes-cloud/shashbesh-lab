import {mkdir,readFile,writeFile,copyFile,cp} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url)),publicPreview=process.argv.includes('--public-preview'),out=path.join(root,publicPreview?'dist-public':'dist');
const pages=['home','arena','rules','strategy','learning','developers','benchmarks','rankings','documentation'];
const en=JSON.parse(await readFile(path.join(root,'locales/en.json'))),ru=JSON.parse(await readFile(path.join(root,'locales/ru.json')));
if(JSON.stringify(Object.keys(en).sort())!==JSON.stringify(Object.keys(ru).sort())||JSON.stringify(Object.keys(en.nav).sort())!==JSON.stringify(Object.keys(ru.nav).sort()))throw Error('Translation parity');
await mkdir(out,{recursive:true});
await writeFile(path.join(out,'build-config.json'),JSON.stringify({mode:publicPreview?'public-preview':'local',interactive:!publicPreview})+'\n');
for(const f of ['index.html','app.js','i18n.js','styles.css'])await copyFile(path.join(root,'src',f),path.join(out,f));
await cp(path.join(root,'locales'),path.join(out,'locales'),{recursive:true});
const html=await readFile(path.join(root,'src/index.html'),'utf8');
for(const lang of ['en','ru'])for(const page of pages){const dir=path.join(out,lang,page);await mkdir(dir,{recursive:true});await writeFile(path.join(dir,'index.html'),html.replace('lang="en"',`lang="${lang}"`));}
await writeFile(path.join(out,'404.html'),html);
await mkdir(path.join(out,'docs'),{recursive:true});
for(const name of ['ARCHITECTURE','BILINGUAL_I18N','AGENT_PROTOCOL_V1','RULES_BENCHMARK','EXPERIMENTAL_METHODOLOGY','SECURITY_MODEL','BILLING_CREDITS','CLOUDFLARE_DEPLOYMENT','IMPLEMENTATION_ROADMAP'])await copyFile(path.join(root,'../../docs/platform',name+'.md'),path.join(out,'docs',name+'.md'));
await copyFile(path.join(root,'agent_client.py'),path.join(out,'agent_client.py'));
await writeFile(path.join(out,'_headers'),"/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'\n");
console.log('BUILD PASS: '+(publicPreview?'PUBLIC PREVIEW (interactive backend disabled)':'LOCAL')+'; 18 routes; no Core/backend/credentials bundled.');
