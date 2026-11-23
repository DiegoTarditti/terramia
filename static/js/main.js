// Nav scroll — en páginas sin hero el fondo aparece siempre
const nav = document.getElementById('siteNav');
if (nav && window.location.pathname !== '/') nav.classList.add('scrolled');
window.addEventListener('scroll', () => nav?.classList.toggle('scrolled', window.scrollY > 40 || window.location.pathname !== '/'));

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

// Franja de fotos: cambia sola cada 5,5 s, se pausa con el mouse encima o si la pestaña está oculta,
// y no avanza sola si el usuario prefiere menos movimiento. Los puntos y el deslizar con el dedo la cambian a mano.
(function () {
  const franja = document.querySelector('.franja');
  if (!franja) return;
  const slides = [...franja.querySelectorAll('.franja-slide')];
  const dots = [...franja.querySelectorAll('.franja-dot')];
  if (slides.length < 2) return;
  let actual = 0, timer = null;
  const ir = n => {
    actual = (n + slides.length) % slides.length;
    slides.forEach((s, i) => s.classList.toggle('is-active', i === actual));
    dots.forEach((d, i) => d.classList.toggle('is-active', i === actual));
  };
  const parar = () => { clearInterval(timer); timer = null };
  const arrancar = () => {
    if (timer || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    timer = setInterval(() => ir(actual + 1), 5500);
  };
  dots.forEach((d, i) => d.addEventListener('click', () => { ir(i); parar(); arrancar(); }));
  franja.addEventListener('mouseenter', parar);
  franja.addEventListener('mouseleave', arrancar);
  document.addEventListener('visibilitychange', () => document.hidden ? parar() : arrancar());
  let x0 = null;
  franja.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
  franja.addEventListener('touchend', e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 40) { ir(actual + (dx < 0 ? 1 : -1)); parar(); arrancar(); }
  }, { passive: true });
  arrancar();
})();
