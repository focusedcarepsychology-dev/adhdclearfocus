/* ADHDclearfocus v2 shared UX helpers — dependency-free and no build step. */
(function(){
  'use strict';
  var ACF = window.ACF = window.ACF || {};
  ACF.version = '2.0.0-low-cost-premium';

  ACF.toast = function(message, ms){
    try{
      var old = document.querySelector('.acf-toast');
      if(old) old.remove();
      var el = document.createElement('div');
      el.className = 'acf-toast';
      el.setAttribute('role','status');
      el.setAttribute('aria-live','polite');
      el.textContent = String(message || 'Saved');
      document.body.appendChild(el);
      setTimeout(function(){ el.style.opacity = '0'; el.style.transition = 'opacity .22s ease'; setTimeout(function(){el.remove();}, 260); }, ms || 2800);
    }catch(e){}
  };

  function addTargetBlankSafety(){
    document.querySelectorAll('a[target="_blank"]').forEach(function(a){
      var rel = (a.getAttribute('rel') || '').split(/\s+/);
      ['noopener','noreferrer'].forEach(function(x){ if(rel.indexOf(x) === -1) rel.push(x); });
      a.setAttribute('rel', rel.join(' ').trim());
    });
  }

  function addExternalClickAnalytics(){
    document.addEventListener('click', function(e){
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if(!a || typeof window.gtag !== 'function') return;
      var href = a.getAttribute('href') || '';
      if(/^https?:\/\//.test(href) && href.indexOf(location.hostname) === -1){
        try{ window.gtag('event','external_link_click',{link_url:href,link_text:(a.textContent||'').trim().slice(0,80)}); }catch(_e){}
      }
    }, {passive:true});
  }

  function restoreScroll(){
    var key = 'acf_scroll_' + location.pathname;
    try{
      var saved = +sessionStorage.getItem(key);
      if(saved && saved > 120 && !location.hash) setTimeout(function(){ scrollTo({top:saved, behavior:'instant'}); }, 80);
      addEventListener('pagehide', function(){ sessionStorage.setItem(key, String(scrollY || 0)); });
    }catch(e){}
  }

  function pwaInstallHint(){
    var deferred;
    window.addEventListener('beforeinstallprompt', function(e){ deferred = e; });
    ACF.promptInstall = function(){
      if(!deferred){ ACF.toast('Use your browser menu to add ADHDclearfocus to your home screen.'); return; }
      deferred.prompt();
      deferred = null;
    };
  }

  function setupFocusMode(){
    var k = 'acf_low_stimulation';
    ACF.toggleLowStimulation = function(force){
      var on = typeof force === 'boolean' ? force : localStorage.getItem(k) !== '1';
      localStorage.setItem(k, on ? '1' : '0');
      document.documentElement.classList.toggle('acf-low-stimulation', on);
      document.body.classList.toggle('focus-mode', on);
      ACF.toast(on ? 'Low-stimulation mode on' : 'Low-stimulation mode off');
      return on;
    };
    try{
      var on = localStorage.getItem(k) === '1';
      document.documentElement.classList.toggle('acf-low-stimulation', on);
      document.body.classList.toggle('focus-mode', on);
    }catch(e){}
  }

  function addSkipLink(){
    if(document.querySelector('.skip-link')) return;
    var target = document.querySelector('#main-content,#root,.main,main');
    if(target && !target.id) target.id = 'main-content';
    var a = document.createElement('a');
    a.className = 'skip-link';
    a.href = '#' + (target ? target.id : 'root');
    a.textContent = 'Skip to main content';
    document.body.insertBefore(a, document.body.firstChild);
  }

  function init(){
    addSkipLink();
    addTargetBlankSafety();
    addExternalClickAnalytics();
    restoreScroll();
    pwaInstallHint();
    setupFocusMode();
    if('serviceWorker' in navigator){ navigator.serviceWorker.register('/sw.js').catch(function(){}); }
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
