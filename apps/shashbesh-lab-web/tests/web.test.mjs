import test from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';
import {chooseLanguage,translate,route,pages} from '../src/i18n.js';
const en=JSON.parse(await readFile(new URL('../locales/en.json',import.meta.url))),ru=JSON.parse(await readFile(new URL('../locales/ru.json',import.meta.url)));
test('language negotiation and saved preference',()=>{assert.equal(chooseLanguage('/',null,['ru-RU']),'ru');assert.equal(chooseLanguage('/',null,['fr']),'en');assert.equal(chooseLanguage('/en/rules/','ru',['ru']),'en');assert.equal(chooseLanguage('/','ru',['en']),'ru');});
test('English fallback and matching catalogs',()=>{assert.deepEqual(Object.keys(en).sort(),Object.keys(ru).sort());assert.deepEqual(Object.keys(en.nav).sort(),Object.keys(ru.nav).sort());assert.equal(translate({},en,'nav.rules'),'Rules Lab');assert.equal(translate({},en,'missing'),'missing');});
test('all bilingual routes and unknown route',()=>{for(const lang of ['ru','en'])for(const page of pages){assert.equal(route(`/${lang}/${page}/`).page,page);assert.ok(route(`/${lang}/${page}/`).valid);}assert.equal(route('/en/nonexistent/').valid,false);assert.equal(route('/en/rules/secret').valid,false);});
test('built route files and separate assets',async()=>{for(const lang of ['ru','en'])for(const page of pages)assert.match(await readFile(new URL(`../dist/${lang}/${page}/index.html`,import.meta.url),'utf8'),new RegExp(`lang="${lang}"`));assert.match(await readFile(new URL('../dist/_headers',import.meta.url),'utf8'),/frame-ancestors 'none'/);});

test('local build config explicitly enables only local interaction',async()=>{const config=JSON.parse(await readFile(new URL('../dist/build-config.json',import.meta.url)));assert.equal(config.mode,'local');assert.equal(config.interactive,true);});

test('public build disables interactive functionality and uses independent output',async()=>{const config=JSON.parse(await readFile(new URL('../dist-public/build-config.json',import.meta.url)));assert.equal(config.mode,'public-preview');assert.equal(config.interactive,false);assert.match(await readFile(new URL('../wrangler.jsonc',import.meta.url),'utf8'),/dist-public/);});
