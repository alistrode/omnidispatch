export let csrf='';export const setCsrf=(v:string)=>csrf=v;
export async function api(path:string,method='GET',body?:unknown){
 const isForm=body instanceof FormData;
 const response=await fetch('/api'+path,{method,credentials:'same-origin',headers:{...(isForm?{}:{'Content-Type':'application/json'}),...(method==='GET'?{}:{'X-CSRF-Token':csrf})},body:body===undefined?undefined:isForm?body as FormData:JSON.stringify(body)});
 const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail));return data;
}
