// Same-origin paths: nginx proxies /auth, /users, /listings and /transactions to the services.
const $ = s => document.querySelector(s);
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let token = '', email = '';
try { token = sessionStorage.getItem('eco-token') || ''; email = sessionStorage.getItem('eco-email') || ''; } catch (e) {}

const SAMPLE = [
  {id:1,title:'Desk lamp',description:'Works fine, small scratch on the base.',price:0},
  {id:2,title:'Bike helmet',description:'Medium, worn twice.',price:15},
  {id:3,title:'Cast iron pan',description:'Seasoned and ready to cook.',price:20},
  {id:4,title:'Box of paperbacks',description:'About 30 novels.',price:0}
];

function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(toast.id); toast.id = setTimeout(() => t.classList.remove('show'), 3000);
}

async function api(path, opts = {}) {
  const headers = {};
  if (token) headers.Authorization = 'Bearer ' + token;
  if (opts.body) headers['Content-Type'] = 'application/json';
  const label = (opts.method || 'GET') + ' ' + path.replace(/\?.*/, '');
  let r;
  try { r = await fetch(path, {...opts, headers}); }
  catch (e) { $('#raw').textContent = label + ' -> no response'; const err = new Error('Could not reach the server'); err.network = true; throw err; }
  const text = await r.text();
  let body = text;
  try { body = text ? JSON.parse(text) : null; } catch (e) {}
  // Never print the JWT itself.
  $('#raw').textContent = label + ' -> ' + r.status + '\n' +
    (path.startsWith('/auth/') && r.ok ? '(token received)' : (typeof body === 'string' ? body : JSON.stringify(body, null, 2)));
  if (!r.ok) {
    const err = new Error((body && body.message) || (typeof body === 'string' && body) || 'Request failed (' + r.status + ')');
    err.status = r.status; throw err;
  }
  return body;
}

const list = d => Array.isArray(d) ? d : (d && d.content) || [];

function show(tab) {
  document.querySelectorAll('.panel').forEach(p => p.hidden = p.id !== 'p-' + tab);
  document.querySelectorAll('nav.tabs button').forEach(b => b.setAttribute('aria-selected', b.dataset.tab === tab));
}
document.querySelectorAll('nav.tabs button').forEach(b => b.onclick = () => show(b.dataset.tab));

function needLogin() { toast('Sign in first'); show('account'); $('#a-email').focus(); }

function renderWho() {
  $('#who').innerHTML = token ? 'Signed in as <b>' + esc(email) + '</b>' : 'Not signed in';
  $('#signout').hidden = !token;
}

function save() {
  try { sessionStorage.setItem('eco-token', token); sessionStorage.setItem('eco-email', email); } catch (e) {}
}

$('#signout').onclick = () => { token = ''; email = ''; save(); renderWho(); loadListings(); toast('Signed out'); };

$('#cta-list').onclick = () => { if (!token) return needLogin(); show('market'); $('#l-title').focus(); };
$('#cta-browse').onclick = () => { show('market'); $('nav.tabs').scrollIntoView(); };

function tag(l) {
  const price = Number(l.price), free = !price;
  return '<article class="tag"><span class="id">Listing ' + esc(l.id) + '</span>' +
    '<h3>' + esc(l.title || l.name || 'Untitled') + '</h3>' +
    '<p>' + esc(l.description || 'No description yet.') + '</p>' +
    '<div class="foot"><span class="price' + (free ? ' free' : '') + '">' + (free ? 'Free' : '$' + price.toFixed(2)) + '</span>' +
    '<button class="btn small danger" data-del="' + esc(l.id) + '">Remove</button></div></article>';
}

function banner(html) { const b = $('#banner'); b.innerHTML = html || ''; b.hidden = !html; }

async function loadListings() {
  const box = $('#listings');
  if (!token) {
    banner('Sign in to see what people are listing. These are samples.');
    box.innerHTML = SAMPLE.map(tag).join('');
    return;
  }
  try {
    const data = list(await api('/listings'));
    banner('');
    box.innerHTML = data.length ? data.map(tag).join('') :
      '<div class="empty" style="grid-column:1/-1">Nothing listed yet. Be the first to post something.</div>';
  } catch (e) {
    if (e.status === 401 || e.status === 403) { token = ''; save(); renderWho(); banner('Your session expired. Sign in again.'); }
    else banner('The listings service did not respond, so these are samples. Check that the stack is running.');
    box.innerHTML = SAMPLE.map(tag).join('');
  }
  box.querySelectorAll('[data-del]').forEach(b => b.onclick = async () => {
    if (!token) return needLogin();
    try { await api('/listings/' + b.dataset.del, {method:'DELETE'}); toast('Listing removed'); loadListings(); }
    catch (e) { toast(e.message); }
  });
}

$('#f-list').onsubmit = async e => {
  e.preventDefault();
  if (!token) return needLogin();
  const price = parseFloat($('#l-price').value) || 0;
  try {
    await api('/listings', {method:'POST', body: JSON.stringify({
      title: $('#l-title').value, description: $('#l-desc').value, price,
      type: price === 0 ? 'DONATION' : 'SALE'
    })});
    e.target.reset(); toast('Listing posted'); loadListings();
  } catch (err) { toast(err.message); }
};

$('#f-find').onsubmit = async e => {
  e.preventDefault();
  if (!token) return needLogin();
  const out = $('#deal-result');
  try {
    const t = await api('/transactions/' + encodeURIComponent($('#t-id').value.trim()));
    out.innerHTML = '<div class="item">' + Object.entries(t || {}).map(([k, v]) =>
      '<span>' + esc(k) + ': <b>' + esc(typeof v === 'object' ? JSON.stringify(v) : v) + '</b></span>').join('') + '</div>';
  } catch (err) { out.innerHTML = '<div class="empty">' + esc(err.message) + '</div>'; }
};

async function post(path, payload, done) {
  if (!token) return needLogin();
  try { await api(path, {method:'POST', body: JSON.stringify(payload)}); toast(done); }
  catch (err) { toast(err.message); }
}
$('#f-offer').onsubmit = e => { e.preventDefault();
  post('/transactions/offers', {listingId: Number($('#o-id').value), amount: parseFloat($('#o-amt').value) || 0}, 'Offer sent'); };
$('#f-claim').onsubmit = e => { e.preventDefault();
  post('/transactions/claim', {listingId: Number($('#c-id').value)}, 'Item claimed'); };

$('#f-auth').onsubmit = async e => {
  e.preventDefault();
  const act = (e.submitter && e.submitter.dataset.act) || 'login';
  const mail = $('#a-email').value.trim(), name = $('#a-user').value.trim();
  if (act === 'register' && !name) return toast('Choose a username to create an account');
  const path = act === 'register'
    ? '/auth/register?email=' + encodeURIComponent(mail) + '&username=' + encodeURIComponent(name)
    : '/auth/login?email=' + encodeURIComponent(mail);
  try {
    token = String(await api(path, {method:'POST'})).trim(); email = mail; save(); renderWho();
    toast(act === 'register' ? 'Account created. You are signed in.' : 'Signed in');
    show('market'); loadListings();
  } catch (err) {
    toast(act === 'login' && err.status === 404 ? 'No account for that email. Create one first.' : err.message);
  }
};

$('#load-users').onclick = async () => {
  if (!token) return needLogin();
  try {
    const u = list(await api('/users'));
    $('#users').innerHTML = u.length ? u.map(x =>
      '<div class="item"><span>Member: <b>' + esc(x.username || x.email || x.name || x.id) + '</b></span></div>').join('') :
      '<div class="empty">No members yet.</div>';
  } catch (err) { toast(err.message); }
};

$('#reload').onclick = loadListings;
renderWho();
loadListings();
