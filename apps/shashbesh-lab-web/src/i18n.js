export const pages=['home','arena','rules','strategy','learning','developers','benchmarks','rankings','documentation'];
export function chooseLanguage(path,saved,languages=[]){const first=path.split('/')[1];if(['ru','en'].includes(first))return first;if(['ru','en'].includes(saved))return saved;return languages[0]?.toLowerCase().startsWith('ru')?'ru':'en';}
export function translate(catalog,fallback,key){return key.split('.').reduce((v,k)=>v?.[k],catalog)??key.split('.').reduce((v,k)=>v?.[k],fallback)??key;}
export function route(path){const bits=path.split('/').filter(Boolean);return bits.length===0?{page:'home',valid:true}:{page:bits[1]||'home',valid:['ru','en'].includes(bits[0])&&bits.length<=2&&pages.includes(bits[1]||'home')};}
