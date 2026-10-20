// Local compatibility fixtures only. No server, network, agent code, or rule implementation.
import * as Core from '../../artifacts/core/0.1.0-g0.65e1ec3/package/dist/packages/engine/src/index.js';
import csv from '../../artifacts/core/0.1.0-g0.65e1ec3/package/data/igra_64_koordinaty.csv';
const geometry=Core.parseGeometry(csv);
const engine=new Core.Engine(geometry,{journalVersion:2,timeSource:'logical'});
const check=(condition,message)=>{if(!condition)throw Error(message);};
function fixture(count,dice=[6,6]){
 let state=engine.create(Array.from({length:count},(_,i)=>i+1),'release-runtime-fixture','public-test-fixture');
 state=engine.initialRoll(state,Object.fromEntries(state.players.map(p=>[p,p===1?6:1])));
 return engine.roll(state,dice);
}
function trial(state,mode){return {state,mode,closed:false,audit:[]};}
function submit(t,action){
 if(t.closed)return {accepted:false,closed:true};
 let accepted=false,next=t.state;
 try{next=engine.applyAction(t.state,action);accepted=true;}catch{/* Core alone rejects the action. */}
 t.audit.push({action,accepted});
 if(accepted)t.state=next;
 t.closed=accepted||t.mode==='exam';
 return {accepted,closed:t.closed,feedback:accepted?'accepted':'invalid_action'};
}
export function runCase(count,repeats=1){
 const start=fixture(count),before=Core.stateHash(start),legal=engine.legalActions(start);
 check(start.pieces.length===count*5,'piece count');check(legal.length>0,'legal calculation');
 // Agent projection never includes the private oracle or original internal state.
 const task={protocol:'shashbesh-agent/1',observation:{active_seat:start.activePlayer-1,pieces:start.pieces,dice:start.currentRoll.dice},geometry};
 const serialized=JSON.stringify(task);
 for(const hidden of ['legalActions','action_id','eventLog','rng_counter','seedMetadata'])check(!serialized.includes(hidden),'agent leakage');
 const exam=trial(start,'exam');check(!submit(exam,{kind:'invented'}).accepted,'Core validation');
 check(exam.closed&&exam.audit.length===1,'Exam first attempt');
 check(Core.stateHash(exam.state)===before&&Core.stateHash(start)===before,'Exam mutation');
 check(!submit(exam,legal[0]).accepted&&exam.audit.length===1,'Exam seal');
 const learning=trial(start,'learning');check(!submit(learning,{}).accepted&&!learning.closed,'Learning error');
 check(submit(learning,legal[0]).accepted&&learning.audit.length===2,'Learning recovery');
 check(Core.stateHash(engine.replay(learning.state.eventLog))===Core.stateHash(learning.state),'replay');
 const zero=fixture(count,[3,3]);check(engine.legalActions(zero).length===0,'empty roll');
 const finished=engine.finishRoll(zero);check(finished.activePlayer===zero.activePlayer,'Core bonus turn');
 const sum11=fixture(count,[6,5]);check(sum11.currentRoll.extraRoll,'Core 6+5');
 check(start.currentRoll.remainingActions.length===4,'Core double units');
 let last;
 for(let n=0;n<repeats;n++){
  let s=fixture(count);
  for(let i=0;i<4;i++){const actions=engine.legalActions(s);if(!actions.length)break;s=engine.applyAction(s,actions[0]);}
  if(!engine.winner(s)&&!engine.legalActions(s).length)s=engine.finishRoll(s);
  check(Core.stateHash(engine.replay(s.eventLog))===Core.stateHash(s),'stress replay');last=Core.stateHash(s);
 }
 return {players:count,initial_hash:before,accepted_hash:Core.stateHash(learning.state),final_hash:last,
         repeats,exam:'PASS',learning:'PASS',core_validation:'PASS',agent_projection:'PASS'};
}
export const players2={async test(){console.log('CORE_RESULT '+JSON.stringify(runCase(2)));}};
export const players3={async test(){console.log('CORE_RESULT '+JSON.stringify(runCase(3)));}};
export const players4={async test(){console.log('CORE_RESULT '+JSON.stringify(runCase(4)));}};
export const stress4={async test(){console.log('CORE_RESULT '+JSON.stringify(runCase(4,25)));}};
export default {async test(){for(const count of [2,3,4])console.log('CORE_RESULT '+JSON.stringify(runCase(count)));}};
