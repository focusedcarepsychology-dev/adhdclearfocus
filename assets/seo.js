(function(){
  'use strict';

  const FIRST_KEY='acf_first_touch_v1';
  const LAST_KEY='acf_last_touch_v1';

  function clean(v,max){return String(v||'').trim().toLowerCase().replace(/[^a-z0-9._-]+/g,'-').replace(/^-+|-+$/g,'').slice(0,max||70);}
  function read(key){try{return JSON.parse(localStorage.getItem(key)||'null');}catch(e){return null;}}
  function write(key,value){try{localStorage.setItem(key,JSON.stringify(value));}catch(e){}}
  function referrerSource(){
    try{
      if(!document.referrer)return 'direct';
      const host=new URL(document.referrer).hostname.toLowerCase();
      if(host===location.hostname||host.endsWith('.'+location.hostname))return 'internal';
      if(/google\./.test(host))return 'google';
      if(/bing\./.test(host))return 'bing';
      if(/facebook|instagram|threads/.test(host))return 'meta';
      if(/linkedin/.test(host))return 'linkedin';
      if(/reddit/.test(host))return 'reddit';
      if(/tiktok/.test(host))return 'tiktok';
      return 'referral';
    }catch(e){return 'referral';}
  }
  function currentTouch(){
    const qs=new URLSearchParams(location.search);
    const source=clean(qs.get('utm_source')||referrerSource(),40)||'direct';
    return {
      source:source,
      medium:clean(qs.get('utm_medium'),40)||'unknown',
      campaign:clean(qs.get('utm_campaign'),70)||'none',
      content:clean(qs.get('utm_content'),70)||'none',
      landing:clean(location.pathname.replace(/^\//,'')||'home',70),
      captured_at:new Date().toISOString()
    };
  }
  const touch=currentTouch();
  const first=read(FIRST_KEY)||touch;
  if(!read(FIRST_KEY))write(FIRST_KEY,first);
  write(LAST_KEY,touch);

  function snapshot(){return {first:first,last:read(LAST_KEY)||touch};}
  function tags(){
    const s=snapshot();
    return [
      'source-'+clean(s.first.source,35),
      'landing-'+clean(s.first.landing,50),
      'campaign-'+clean(s.last.campaign,50)
    ].filter(Boolean);
  }
  function params(extra){
    const s=snapshot();
    return Object.assign({
      first_source:s.first.source,
      first_landing:s.first.landing,
      last_source:s.last.source,
      last_campaign:s.last.campaign
    },extra||{});
  }
  function track(name,extra){try{if(typeof window.gtag==='function')window.gtag('event',name,params(extra));}catch(e){}}

  window.ACFAttribution={snapshot:snapshot,tags:tags,eventParams:params};

  function ensureConsent(){
    document.querySelectorAll('[data-seo-newsletter]').forEach(function(form){
      if(form.querySelector('input[name="consent"]')) return;
      const small=form.querySelector('[data-newsletter-msg]');
      const label=document.createElement('label');
      label.className='newsletter-consent';
      label.innerHTML='<input type="checkbox" name="consent" required/> <span>I agree to receive ADHDclearfocus educational emails. I can unsubscribe at any time. <a href="/legal">Privacy information</a>.</span>';
      if(small) form.insertBefore(label,small); else form.appendChild(label);
    });
  }
  async function subscribe(form){
    const email=(form.querySelector('input[type="email"]')?.value||'').trim();
    const msg=form.querySelector('[data-newsletter-msg]');
    const consent=!!form.querySelector('input[name="consent"]:checked');
    if(!email || !email.includes('@')){if(msg)msg.textContent='Enter a valid email address.';return;}
    if(!consent){if(msg)msg.textContent='Please confirm you want to receive ADHDclearfocus emails.';return;}
    const button=form.querySelector('button');
    if(button)button.disabled=true;
    if(msg)msg.textContent='Saving…';
    try{
      const page=location.pathname.replace(/^\//,'')||'home';
      const attributionTags=tags();
      const res=await fetch('/api/mailchimp-subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,consent:true,tags:['seo-organic','adhd-toolkit',page.slice(0,70)].concat(attributionTags)})});
      const data=await res.json().catch(()=>({}));
      if(!res.ok || !data.success)throw new Error(data.error||'subscribe');
      if(msg)msg.textContent='You’re in. We’ll send practical ADHDclearfocus resources, not daily noise.';
      form.reset();
      track('seo_email_signup',{page:location.pathname});
    }catch(e){
      if(msg)msg.textContent='We could not save that just now. You can still use all free resources on the site.';
    }finally{if(button)button.disabled=false;}
  }
  document.addEventListener('submit',function(e){
    const form=e.target.closest&&e.target.closest('[data-seo-newsletter]');
    if(!form)return;
    e.preventDefault();subscribe(form);
  });
  document.addEventListener('click',function(e){
    const a=e.target.closest&&e.target.closest('[data-share]');
    if(a)track('seo_share_click',{network:a.getAttribute('data-share'),page:location.pathname});
  },{passive:true});
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',ensureConsent); else ensureConsent();
})();