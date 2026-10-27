export let csrf='';export const setCsrf=(v:string)=>csrf=v;
export async function api(path:string,method='GET',body?:unknown,extraHeaders:Record<string,string>={}){
 const isForm=body instanceof FormData;const isBinary=body instanceof Blob||body instanceof ArrayBuffer;
 const response=await fetch('/api'+path,{method,credentials:'same-origin',headers:{...(isForm?{}:{'Content-Type':isBinary?'application/octet-stream':'application/json'}),...(method==='GET'?{}:{'X-CSRF-Token':csrf}),...extraHeaders},body:body===undefined?undefined:isForm||isBinary?body as BodyInit:JSON.stringify(body)});
 const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail));return data;
}
