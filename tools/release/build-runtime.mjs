// Only builds local audit artifacts; never ships Core in the website output.
import {createRequire} from 'node:module';
import {writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const [toolRoot,outRoot]=process.argv.slice(2);
if(!toolRoot||!outRoot)throw Error('Usage: node build-runtime.mjs TOOL_ROOT OUTPUT_ROOT');
const require=createRequire(path.resolve(toolRoot,'package.json'));
const esbuild=require('esbuild');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const result=await esbuild.build({entryPoints:[path.join(root,'tools/release/core-runtime.mjs')],bundle:true,format:'esm',platform:'browser',conditions:['browser'],loader:{'.csv':'text'},outfile:path.join(outRoot,'core-bundle.mjs'),metafile:true,legalComments:'eof'});
await writeFile(path.join(outRoot,'bundle-meta.json'),JSON.stringify(result.metafile,null,2));
