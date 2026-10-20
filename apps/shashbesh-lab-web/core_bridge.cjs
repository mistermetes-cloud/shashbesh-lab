'use strict';
// Host adapter only. All decisions and validation belong to the pinned Core.
const fs=require('node:fs'),path=require('node:path'),readline=require('node:readline');
const root=process.env.SHASHBESH_CORE_PACKAGE,Core=require(root);
const version=require(path.join(root,'package.json')).version;
const geometry=Core.parseGeometry(fs.readFileSync(path.join(root,'data/igra_64_koordinaty.csv'),'utf8'));
const engine=new Core.Engine(geometry,{journalVersion:2,timeSource:'logical'}),games=new Map();
function ref(id,s){return {protocol_version:'1.1',environment_id:'shashbesh.core',environment_version:'1.0.0',core_version:version,
 core_artifact_sha256:process.env.SHASHBESH_CORE_SHA256,worker_state_id:id,active_player:s.activePlayer-1,
 phase:s.phase,winner_player:s.winner,current_roll:s.currentRoll,pieces:s.pieces};}
function state(r){if(!games.has(r.state.worker_state_id))throw Error('expired');return games.get(r.state.worker_state_id);}
function handle(r){switch(r.operation){
 case 'hello':return {core_version:version,core_artifact_sha256:process.env.SHASHBESH_CORE_SHA256};
 case 'geometry':return {cells:geometry.cells,homes:geometry.homes,starts:geometry.starts,corners:geometry.corners,width:13,height:13};
 case 'fixture':{
  if(games.size>=32)throw Error('capacity');
  const players=Array.from({length:r.players},(_,i)=>i+1);
  let s=engine.create(players,r.id,'research-fixture-v1');
  s=engine.initialRoll(s,Object.fromEntries(players.map(p=>[p,p===1?6:1])));
  if(r.position==='developed'){
   s=engine.roll(s,[6,6]);
   for(let i=0;i<4;i++){const actions=engine.legalActions(s);if(!actions.length)break;s=engine.applyAction(s,actions.find(a=>a.kind==='deploy')||actions[0]);}
   if(!engine.legalActions(s).length)s=engine.finishRoll(s);
  }
  s=engine.roll(s,r.dice);
  // Zero-action roll stays visible as a completed Core roll, without invented moves.
  if(!engine.legalActions(s).length)s=engine.finishRoll(s);
  games.set(r.id,s);return {state:ref(r.id,s)};
 }
 case 'legal_actions':return {actions:engine.legalActions(state(r))};
 case 'validate':{
  const s=state(r),before=Core.stateHash(s);
  try{engine.applyAction(s,r.action);return {valid:true,state_hash:before};}
  catch(e){return {valid:false,category:'illegal_action',reason:String(e.message).slice(0,400),state_hash:before};}
 }
 case 'step':{
  const id=r.state.worker_state_id;
  let s=engine.applyAction(state(r),r.action,{kind:'agent',id:'web-agent-v1',version:'1'});
  if(!engine.winner(s)&&!engine.legalActions(s).length)s=engine.finishRoll(s);
  games.set(id,s);return {state:ref(id,s)};
 }
 case 'inspect':{const s=state(r);return {state_hash:Core.stateHash(s),event_head:s.eventLog.at(-1)?.hash,events:s.eventLog};}
 case 'release':games.delete(r.id);return {released:true};
 case 'shutdown':return {shutdown:true};
 default:throw Error('unknown_operation');
}}
readline.createInterface({input:process.stdin,crlfDelay:Infinity}).on('line',line=>{
 let r;try{if(Buffer.byteLength(line)>65536)throw Error('size');r=JSON.parse(line);const data=handle(r);
 process.stdout.write(JSON.stringify({protocol:'lab-node-protocol/1',request_id:r.request_id,ok:true,data})+'\n');
 if(r.operation==='shutdown')process.exit(0);
 }catch(e){process.stdout.write(JSON.stringify({protocol:'lab-node-protocol/1',request_id:r?.request_id,ok:false,error:{name:e.name,message:e.message}})+'\n');}
});
