const input=document.getElementById("command");
const result=document.getElementById("result");
const verifyButton=document.getElementById("verify");
const safeButton=document.getElementById("safe");
const unsafeButton=document.getElementById("unsafe");

function esc(value){
  return String(value)
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;")
    .replaceAll('"',"&quot;");
}

function showResult(data){
  const verification=data && data.verification ? data.verification : {};
  const receipt=data && data.receipt ? data.receipt : {};
  const verdict=verification.verdict || receipt.verdict || "unknown";
  const cls=verdict==="allow" ? "allow" : verdict==="deny" ? "deny" : "escalate";
  const reason=receipt.block_reason || "no block reason";
  result.classList.remove("hidden");
  result.innerHTML=
    '<div class="verdict '+cls+'">'+esc(verdict.toUpperCase())+'</div>'+
    '<div class="small">'+esc(reason)+'</div>'+
    '<div class="meta">'+esc(JSON.stringify(data,null,2))+'</div>';
}

async function verify(){
  result.classList.remove("hidden");
  result.innerHTML='<div class="small">Verifying...</div>';
  try{
    const body=JSON.parse(input.value);
    const response=await fetch("/v1/verify",{
      method:"POST",
      headers:{"content-type":"application/json"},
      body:JSON.stringify(body)
    });
    const data=await response.json();
    if(!response.ok){
      result.innerHTML='<div class="verdict deny">ERROR</div><div class="meta">'+esc(JSON.stringify(data,null,2))+'</div>';
      return;
    }
    showResult(data);
  }catch(error){
    result.innerHTML='<div class="verdict deny">INVALID JSON</div><div class="meta">'+esc(error.message)+'</div>';
  }
}

safeButton.onclick=()=>{
  input.value=JSON.stringify({
    agent_id:"demo-agent",
    tool:"search_web",
    params:{query:"hello"}
  },null,2);
};

unsafeButton.onclick=()=>{
  input.value=JSON.stringify({
    agent_id:"demo-agent",
    tool:"shell_exec",
    params:{command:"rm -rf /"}
  },null,2);
};

verifyButton.onclick=verify;
