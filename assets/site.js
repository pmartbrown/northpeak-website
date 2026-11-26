/* North Peak Recovery: shared JS (forms + map modal). */
var NP_CONFIG={
  API_BASE:'https://northpeak-forms.aged-field-fe53.workers.dev',
  SUBMIT_PATH:'/api/submissions',
  SOURCE:'northpeak',
  LIVE_SUBMIT:true
};
NP_CONFIG.submit=function(fd){
  fd.append('source',NP_CONFIG.SOURCE);
  fd.append('page',location.pathname);
  return fetch(NP_CONFIG.API_BASE+NP_CONFIG.SUBMIT_PATH,{method:'POST',body:fd,credentials:'same-origin'}).then(function(r){return {ok:r.ok}});
};
function npPhoneValue(form){
  var phone=form.querySelector('[name=phone]');
  return phone?String(phone.value||'').trim():'';
}
function npSyncConsent(form){
  var consent=form.querySelector('[name=consent]');
  var hint=form.querySelector('.consent-hint');
  if(!consent)return;
  var needed=!!npPhoneValue(form);
  if(form.querySelector('[name=form][value="c"], [name=form][value=c]'))return;
  consent.required=needed;
  if(hint)hint.hidden=!needed;
  if(!needed)consent.setCustomValidity('');
}
function npAddHoneypot(form){
  if(form.querySelector('[name=company]'))return;
  var wrap=document.createElement('div');
  wrap.className='hp';
  wrap.setAttribute('aria-hidden','true');
  wrap.innerHTML='<label>Company<input type="text" name="company" tabindex="-1" autocomplete="off"></label>';
  form.insertBefore(wrap,form.firstChild);
}
function npWire(form){
  npAddHoneypot(form);
  var phone=form.querySelector('[name=phone]');
  if(phone){
    phone.addEventListener('input',function(){npSyncConsent(form)});
    npSyncConsent(form);
  }
  form.addEventListener('submit',function(e){
    e.preventDefault();
    var err=form.querySelector('.err');if(err)err.textContent='';
    npSyncConsent(form);
    if(!form.checkValidity()){form.reportValidity();return}
    var btn=form.querySelector('[type=submit]');
    var btnText=btn?btn.textContent:'Submit';
    if(btn){btn.disabled=true;btn.textContent='Sending…'}
    NP_CONFIG.submit(new FormData(form)).then(function(res){
      if(!res.ok)throw 0;
      var t=document.createElement('div');t.className='thanks';t.setAttribute('role','status');t.tabIndex=-1;
      t.innerHTML='<h3>Thank you. We have it.</h3><p>We will look at public records and reach out the way you asked, usually within one business day. There is no cost and no obligation, and you can still choose to file on your own.</p>';
      form.replaceWith(t);t.focus();
    }).catch(function(){
      if(btn){btn.disabled=false;btn.textContent=btnText}
      if(err)err.textContent='Something went wrong sending this. Please try again.';
    });
  });
}
document.querySelectorAll('form.lead').forEach(npWire);
/* Map + dropdown -> modal */
(function(){
  var dlg=document.getElementById('stateDialog');if(!dlg)return;
  var title=dlg.querySelector('#dlgTitle'),stateIn=dlg.querySelector('input[name=state]'),link=dlg.querySelector('#dlgLink'),last;
  function open(abbr,name,slug){last=document.activeElement;title.textContent='Let’s see if money is waiting for you in '+name;
    stateIn.value=name;link.href=(document.documentElement.dataset.base||'')+'/states/'+slug+'/';link.textContent='Read the '+name+' guide';
    dlg.showModal();dlg.querySelector('input[name=name]').focus();}
  document.querySelectorAll('.usmap a[data-state]').forEach(function(a){
    a.addEventListener('click',function(e){e.preventDefault();open(a.dataset.state,a.dataset.name,a.dataset.slug)});
    a.addEventListener('keydown',function(e){if(e.key===' '||e.key==='Enter'){e.preventDefault();open(a.dataset.state,a.dataset.name,a.dataset.slug)}});
  });
  var sel=document.getElementById('statePick'),go=document.getElementById('statePickGo');
  if(go)go.addEventListener('click',function(){var o=sel.options[sel.selectedIndex];if(!o.value){sel.focus();return}open(o.value,o.text,o.dataset.slug)});
  var h=location.hash.match(/^#check-([A-Z]{2})$/);if(h){var a=document.querySelector('.usmap a[data-state='+h[1]+']');if(a)open(a.dataset.state,a.dataset.name,a.dataset.slug)}
  dlg.querySelector('.x').addEventListener('click',function(){dlg.close()});
  dlg.addEventListener('close',function(){if(last)last.focus()});
  dlg.addEventListener('click',function(e){if(e.target===dlg)dlg.close()});
})();
