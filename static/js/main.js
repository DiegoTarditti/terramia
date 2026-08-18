// Nav scroll
const nav = document.getElementById('siteNav');
window.addEventListener('scroll', () => nav?.classList.toggle('scrolled', window.scrollY > 40));

// Mobile menu
const burger = document.getElementById('burgerBtn');
const navLinks = document.getElementById('navLinks');
const mobileNav = document.getElementById('mobileNav');
burger?.addEventListener('click', () => {
  navLinks?.classList.toggle('open');
  mobileNav?.classList.toggle('open');
});
document.querySelectorAll('.mobile-nav a, .nav-links a').forEach(a =>
  a.addEventListener('click', () => {
    navLinks?.classList.remove('open');
    mobileNav?.classList.remove('open');
  })
);

// Reveal on scroll
const io = new IntersectionObserver(es => {
  es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) } })
}, { threshold: .13 });
document.querySelectorAll('[data-rv]').forEach(el => io.observe(el));

// Flash auto-close
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  });
}, 3500);

// AJAX add to cart
document.querySelectorAll('.add-form').forEach(form => {
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const btn = this.querySelector('.btn-add');
    btn.style.transform = 'scale(1.3)';
    setTimeout(() => btn.style.transform = '', 250);
    fetch(this.action, {
      method: 'POST',
      body: new FormData(this),
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
          badge.textContent = data.cantidad_total;
        } else {
          const cartBtn = document.querySelector('.cart-btn');
          if (cartBtn) {
            const b = document.createElement('span');
            b.className = 'cart-badge';
            b.textContent = data.cantidad_total;
            cartBtn.appendChild(b);
          }
        }
      }
    })
    .catch(() => form.submit());
  });
});
