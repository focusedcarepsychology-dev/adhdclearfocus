(function(){
  'use strict';
  function track(name,params){try{if(typeof window.gtag==='function')window.gtag('event',name,params||{});}catch(e){}}
  async function subscribe(form){
    const email=(form.querySelector('input[type="email"]')?.value||'').trim();
    const msg=form.querySelector('[data-newsletter-msg]');
    if(!email || !email.includes('@')){if(msg)msg.textContent='Enter a valid email address.';return;}
    const button=form.querySelector('button');
    if(button)button.disabled=true;
    if(msg)msg.textContent='Saving…';
    try{
      const page=location.pathname.replace(/^\//,'')||'home';
      const res=await fetch('/api/mailchimp-subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,tags:['seo-organic','adhd-toolkit',page.slice(0,70)]})});
      if(!res.ok && res.status!==202)throw new Error('subscribe');
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
})();