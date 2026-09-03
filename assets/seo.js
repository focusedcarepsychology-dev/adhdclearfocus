(function(){
  'use strict';
  function track(name,params){try{if(typeof window.gtag==='function')window.gtag('event',name,params||{});}catch(e){}}
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
      const res=await fetch('/api/mailchimp-subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,consent:true,tags:['seo-organic','adhd-toolkit',page.slice(0,70)]})});
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