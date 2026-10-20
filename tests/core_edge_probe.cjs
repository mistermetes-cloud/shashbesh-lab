'use strict';
// Dependency/runtime preflight, NOT a workerd/Cloudflare execution test.
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../artifacts/core/0.1.0-g0.65e1ec3/package');
const context = vm.createContext({TextEncoder, TextDecoder, structuredClone, crypto: require('node:crypto').webcrypto});
const cache = new Map();
function load(file) {
  file = fs.realpathSync(file);
  assert.ok(file.startsWith(root + path.sep));
  if (cache.has(file)) return cache.get(file).exports;
  const module = {exports:{}}; cache.set(file,module);
  const localRequire = (name) => {
    if (name.startsWith('node:') || require('node:module').builtinModules.includes(name))
      throw new Error('Node builtin forbidden in Core graph: ' + name);
    // Resolve the bundled package's browser/WebCrypto implementation explicitly.
    const resolved = name === '@noble/hashes/crypto'
      ? path.join(root, 'node_modules/@noble/hashes/crypto.js')
      : require.resolve(name,{paths:[path.dirname(file)]});
    return load(resolved);
  };
  const execute = vm.runInContext('(function(require,module,exports){' + fs.readFileSync(file,'utf8') + '\n})',context);
  execute(localRequire,module,module.exports);
  return module.exports;
}
const edge = load(path.join(root,'dist/packages/engine/src/index.js'));
const native = require(root);
const csv = fs.readFileSync(path.join(root,'data/igra_64_koordinaty.csv'),'utf8');
const results=[];
for (const count of [2,3,4]) {
  const players=Array.from({length:count},(_,i)=>i+1);
  const hashes=[];
  for (const Core of [native,edge]) {
    const engine=new Core.Engine(Core.parseGeometry(csv),{journalVersion:2,timeSource:'logical'});
    let state=engine.create(players,'edge-probe','probe-seed');
    state=engine.initialRoll(state,Object.fromEntries(players.map(p=>[p,p===1?6:1])));
    state=engine.roll(state,[6,6]);
    for(let i=0;i<4;i++) {
      const actions=engine.legalActions(state);
      if(!actions.length) break;
      state=engine.applyAction(state,actions[0]);
    }
    if(state.phase==='resolving_roll'&&!engine.legalActions(state).length) state=engine.finishRoll(state);
    assert.equal(Core.stateHash(engine.replay(state.eventLog)),Core.stateHash(state));
    hashes.push(Core.stateHash(state));
  }
  assert.equal(hashes[0],hashes[1]);results.push({players:count,hash:hashes[0]});
}
console.log(JSON.stringify({status:'PREFLIGHT_PASS',node_builtins_in_core:0,cloudflare_runtime_verified:false,
                           browser_crypto_mapping:true,modules:cache.size,results}));
