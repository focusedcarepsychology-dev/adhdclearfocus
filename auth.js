/* ADHDclearfocus shared account widget — include with <script src="/auth.js"></script>
   Provides window.acfAuth: {isLoggedIn, name, email, open(mode), logout, syncPush, syncPull, onChange}
   Talks to /api/auth (see api/auth.py). Free-tier, token in localStorage. */
(function(){
  var TOKEN_KEY='acf_token', NAME_KEY='acf_account_name', EMAIL_KEY='acf_account_email';
  var listeners=[];

  function token(){ return localStorage.getItem(TOKEN_KEY)||''; }
  function fire(){ listeners.forEach(function(f){ try{f(api);}catch(e){} }); }

  function collectTrackerData(){
    var d={};
    ['streak','last-visit','acf_challenge','last_diary','trial-start'].forEach(function(k){
      var v=localStorage.getItem(k); if(v!==null)d[k]=v;
    });
    d._synced=Date.now();
    return d;
  }
  function mergeTrackerData(remote){
    if(!remote)return;
    // streak: keep the larger
    var rs=parseInt(remote['streak']||'0'), ls=parseInt(localStorage.getItem('streak')||'0');
    if(rs>ls)localStorage.setItem('streak',String(rs));
    // challenge days: union
    try{
      var r=JSON.parse(remote['acf_challenge']||'[]'), l=JSON.parse(localStorage.getItem('acf_challenge')||'[]');
      var u=Array.from(new Set(r.concat(l)));
      localStorage.setItem('acf_challenge',JSON.stringify(u));
    }catch(e){}
    ['last-visit','last_diary','trial-start'].forEach(function(k){
      if(remote[k]&&!localStorage.getItem(k))localStorage.setItem(k,remote[k]);
    });
  }

  var api={
    get isLoggedIn(){ return !!token(); },
    get name(){ return localStorage.getItem(NAME_KEY)||''; },
    get email(){ return localStorage.getItem(EMAIL_KEY)||''; },
    onChange:function(f){ listeners.push(f); },
    logout:function(){
      localStorage.removeItem(TOKEN_KEY);localStorage.removeItem(NAME_KEY);localStorage.removeItem(EMAIL_KEY);
      fire();
    },
    syncPush:function(){
      if(!token())return Promise.resolve(false);
      return fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({action:'set_data',token:token(),data:collectTrackerData()})})
        .then(function(r){return r.ok;}).catch(function(){return false;});
    },
    syncPull:function(){
      if(!token())return Promise.resolve(false);
      return fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({action:'get_data',token:token()})})
        .then(function(r){return r.ok?r.json():null;})
        .then(function(d){
          if(d&&d.data){mergeTrackerData(d.data);fire();return true;}
          if(d===null)api.logout();
          return false;
        }).catch(function(){return false;});
    },
    open:function(mode){ showModal(mode||'login'); }
  };
  window.acfAuth=api;

  // ── Modal UI ──
  var css='#acfAuthModal{position:fixed;inset:0;background:rgba(10,22,40,0.94);z-index:2000;display:flex;align-items:center;justify-content:center;padding:16px}'+
  '#acfAuthModal .box{background:#112240;border:1px solid #1E3A5F;border-radius:18px;width:100%;max-width:400px;padding:24px}'+
  '#acfAuthModal h3{color:#fff;font-size:19px;font-weight:900;margin:0 0 4px;font-family:inherit}'+
  '#acfAuthModal p{color:#7B93B4;font-size:12.5px;line-height:1.6;margin:0 0 14px}'+
  '#acfAuthModal input{width:100%;background:#0A1628;border:1px solid #1E3A5F;border-radius:10px;padding:12px 14px;color:#fff;font-size:14px;font-family:inherit;outline:none;margin-bottom:10px;box-sizing:border-box}'+
  '#acfAuthModal input:focus{border-color:#00D4DD}'+
  '#acfAuthModal .go{width:100%;background:linear-gradient(135deg,#00D4DD,#4FC3F7);color:#0A1628;border:none;border-radius:10px;padding:13px;font-weight:900;font-size:14px;cursor:pointer;font-family:inherit}'+
  '#acfAuthModal .alt{background:none;border:none;color:#00D4DD;font-size:12.5px;cursor:pointer;margin-top:12px;font-family:inherit;padding:0}'+
  '#acfAuthModal .x{position:absolute;top:14px;right:16px;background:none;border:none;color:#7B93B4;font-size:20px;cursor:pointer}'+
  '#acfAuthModal .err{color:#FF5252;font-size:12px;margin:-4px 0 10px;display:none}'+
  '#acfAuthModal .note{color:#7B93B4;font-size:10.5px;line-height:1.55;margin-top:12px}';
  var style=document.createElement('style');style.textContent=css;document.head.appendChild(style);

  function showModal(mode){
    var old=document.getElementById('acfAuthModal'); if(old)old.remove();
    var m=document.createElement('div');m.id='acfAuthModal';
    m.innerHTML='<div class="box" style="position:relative">'+
      '<button class="x" onclick="document.getElementById(\'acfAuthModal\').remove()">✕</button>'+
      '<h3 id="aamTitle"></h3><p id="aamSub"></p>'+
      '<input id="aamName" type="text" placeholder="Display name (shown on posts)" maxlength="40" style="display:none"/>'+
      '<input id="aamEmail" type="email" placeholder="Email"/>'+
      '<input id="aamPw" type="password" placeholder="Password (8+ characters)"/>'+
      '<div class="err" id="aamErr"></div>'+
      '<button class="go" id="aamGo"></button>'+
      '<button class="alt" id="aamAlt"></button>'+
      '<div class="note">Free forever. We store your email, display name, a securely hashed password (never the password itself), and your tracker progress — nothing else. Delete any time by emailing us. See our <a href="/legal.html" style="color:#00D4DD">Privacy Policy</a>.</div>'+
      '</div>';
    document.body.appendChild(m);
    m.addEventListener('click',function(e){if(e.target===m)m.remove();});
    setMode(mode);
    function setMode(mo){
      mode=mo;
      document.getElementById('aamTitle').textContent = mo==='signup'?'Create your free account':'Welcome back';
      document.getElementById('aamSub').textContent = mo==='signup'
        ? 'One account for the community and your progress tracker — synced across your devices.'
        : 'Log in to post and pick up your progress on any device.';
      document.getElementById('aamName').style.display = mo==='signup'?'block':'none';
      document.getElementById('aamGo').textContent = mo==='signup'?'Create account →':'Log in →';
      document.getElementById('aamAlt').textContent = mo==='signup'?'Already have an account? Log in':'New here? Create a free account';
    }
    document.getElementById('aamAlt').onclick=function(){setMode(mode==='signup'?'login':'signup');};
    document.getElementById('aamPw').onkeydown=function(e){if(e.key==='Enter')go();};
    document.getElementById('aamGo').onclick=go;
    function go(){
      var email=(document.getElementById('aamEmail').value||'').trim().toLowerCase();
      var pw=document.getElementById('aamPw').value||'';
      var name=(document.getElementById('aamName').value||'').trim();
      var err=document.getElementById('aamErr');
      err.style.display='none';
      if(!email.includes('@')){err.textContent='Please enter a valid email';err.style.display='block';return;}
      if(pw.length<8){err.textContent='Password must be at least 8 characters';err.style.display='block';return;}
      var btn=document.getElementById('aamGo');btn.textContent='...';
      fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(mode==='signup'?{action:'signup',email:email,password:pw,name:name}
                                           :{action:'login',email:email,password:pw})})
      .then(function(r){return r.json().then(function(d){return {ok:r.ok,d:d};});})
      .then(function(res){
        if(!res.ok){
          err.textContent=(res.d&&res.d.message)||
            (res.d&&res.d.error==='auth_not_configured'
              ? 'Accounts are not switched on yet — the site owner needs to set the auth keys.'
              : 'Something went wrong — please try again.');
          err.style.display='block';setModeBtn();return;
        }
        localStorage.setItem(TOKEN_KEY,res.d.token);
        localStorage.setItem(NAME_KEY,res.d.name||email.split('@')[0]);
        localStorage.setItem(EMAIL_KEY,email);
        if(res.d.data)mergeTrackerData(res.d.data);
        m.remove();
        if(typeof gtag==='function')gtag('event',mode==='signup'?'account_signup':'account_login');
        api.syncPush();
        fire();
      })
      .catch(function(){err.textContent='Network error — please try again.';err.style.display='block';setModeBtn();});
      function setModeBtn(){btn.textContent=mode==='signup'?'Create account →':'Log in →';}
    }
  }

  // On load: if logged in, pull remote data once
  if(token())api.syncPull();
  // Push tracker changes when leaving the page
  window.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='hidden'&&token())api.syncPush();
  });
})();
