/* North Peak Recovery: shared JS (forms + map modal). */
var NP_CONFIG={
  API_BASE:'https://api.txfhub.com',           // same backend pattern as RQF
  SUBMIT_PATH:'/api/submissions',              
  SOURCE:'northpeak',
  LIVE_SUBMIT:false                            // keep false until the endpoint is confirmed; then set true
};
/* Pluggable submit handler: swap this out (HubSpot, Worker, etc.) without touching the forms. */
NP_CONFIG.submit=function(fd){
  fd.append('source',NP_CONFIG.SOURCE);fd.append('page',location.pathname);
  if(!NP_CONFIG.LIVE_SUBMIT){console.info('[NP] demo submit',Object.fromEntries(fd));return Promise.resolve({ok:true,demo:true})}
  return fetch(NP_CONFIG.API_BASE+NP_CONFIG.SUBMIT_PATH,{method:'POST',body:fd}).then(function(r){return {ok:r.ok}});
};
function npWire(form){
  form.addEventListener('submit',function(e){
    e.preventDefault();var err=form.querySelector('.err');if(err)err.textContent='';
    if(!form.checkValidity()){form.reportValidity();return}
    var btn=form.querySelector('[type=submit]');btn.disabled=true;btn.textContent='Sending…';
    NP_CONFIG.submit(new FormData(form)).then(function(res){
      if(!res.ok)throw 0;
      var t=document.createElement('div');t.className='thanks';t.setAttribute('role','status');t.tabIndex=-1;
      t.innerHTML='<h3>Thank you. We\u2019ve got it.</h3><p>We\u2019ll look at public records and reach out the way you asked, usually within one business day. There\u2019s no cost and no obligation, and you can still choose to file on your own.</p>';
      form.replaceWith(t);t.focus();
    }).catch(function(){btn.disabled=false;btn.textContent='Check for my funds';if(err)err.textContent='Something went wrong sending this. Please try again.'});
  });
}
document.querySelectorAll('form.lead').forEach(npWire);
/* Map + dropdown -> modal */
(function(){
  var dlg=document.getElementById('stateDialog');if(!dlg)return;
  var title=dlg.querySelector('#dlgTitle'),stateIn=dlg.querySelector('input[name=state]'),link=dlg.querySelector('#dlgLink'),last;
  function open(abbr,name,slug){last=document.activeElement;title.textContent='Let\u2019s see if money is waiting for you in '+name;
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
