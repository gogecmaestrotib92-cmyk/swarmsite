/* track.js — tells our own server that a page was opened: which kind of page, the host the visitor came from, a
   campaign's tags. No cookie, nothing kept in the browser, no third party; the server keeps no address (server/track.mjs).
   It never waits, never throws and never runs outside swarmsite.si (a local copy, a test, an automated browser).
   swarmsiteTrack('design_opened', {j: <job id>}) is the one other thing a page reports. */
(function () {
  function send(name, extra) {
    try {
      if (!/(^|\.)swarmsite\.si$/.test(location.hostname) || navigator.webdriver) return;
      try { if (localStorage.getItem('swarmsite_notrack')) return; } catch (e) { /* no storage: counted like anyone */ }
      var q = new URLSearchParams(location.search), ref = '';
      try { ref = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) { ref = ''; }
      var body = { n: name, p: location.pathname, r: ref, s: q.get('utm_source') || '', m: q.get('utm_medium') || '', c: q.get('utm_campaign') || '' };
      if (extra && extra.j) body.j = extra.j;
      var api = (window.SWARMSITE_API || 'https://swarmsite-production.up.railway.app') + '/e';
      if (window.fetch) fetch(api, { method: 'POST', body: JSON.stringify(body), headers: { 'content-type': 'text/plain' }, keepalive: true, credentials: 'omit', mode: 'cors' }).catch(function () {});
    } catch (e) { /* a page is never broken by its own counting */ }
  }
  window.swarmsiteTrack = send;
  send('visit');
})();
