/**
 * EcoStyle - JavaScript principal
 * Maneja: carrito AJAX, navbar scroll, notificaciones toast
 */
'use strict';

// ── CSRF Token helper ─────────────────────────────────────────────
function getCsrfToken() {
  return document.cookie.split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

// ── Toast de notificaciones ───────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container') || (() => {
    const el = document.createElement('div');
    el.id = 'toast-container';
    el.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;';
    document.body.appendChild(el);
    return el;
  })();

  const toast = document.createElement('div');
  const bg = type === 'success' ? 'var(--eco-green)' : '#e53935';
  toast.style.cssText = `background:${bg};color:white;padding:12px 20px;border-radius:10px;
    font-size:0.9rem;max-width:320px;box-shadow:0 4px 20px rgba(0,0,0,0.15);
    animation:fadeInUp 0.3s ease;font-family:var(--font-body);`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = '0.3s'; }, 3000);
  setTimeout(() => toast.remove(), 3300);
}

// ── Agregar al carrito (AJAX) ─────────────────────────────────────
document.addEventListener('click', async function(e) {
  const btn = e.target.closest('[data-add-to-cart]');
  if (!btn) return;

  e.preventDefault();
  const productId = btn.dataset.addToCart;
  const quantity = parseInt(btn.dataset.quantity || '1');

  btn.disabled = true;
  const originalText = btn.innerHTML;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

  try {
    const response = await fetch('/cart/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCsrfToken(),
      },
      body: `product_id=${productId}&quantity=${quantity}`,
    });

    const data = await response.json();
    if (data.success) {
      showToast(data.message || '¡Producto agregado!');
      // Actualizar badge del carrito
      document.querySelectorAll('.eco-cart-badge').forEach(el => {
        el.textContent = data.cart_total_items;
        el.style.display = 'flex';
      });
      if (data.cart_total_items === 0) {
        document.querySelectorAll('.eco-cart-badge').forEach(el => el.style.display = 'none');
      }
    } else {
      showToast(data.message || 'No se pudo agregar.', 'error');
    }
  } catch {
    showToast('Error de conexión. Intenta de nuevo.', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalText;
  }
});

// ── Navbar scroll effect ──────────────────────────────────────────
window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.eco-navbar');
  if (!navbar) return;
  navbar.style.boxShadow = window.scrollY > 50
    ? '0 2px 20px rgba(44,44,42,0.12)'
    : 'none';
});

// ── Quantity controls en carrito ──────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.eco-qty-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
      const input = this.closest('.eco-qty-control').querySelector('input');
      const productId = this.dataset.product;
      let qty = parseInt(input.value);
      qty += this.dataset.action === 'plus' ? 1 : -1;
      if (qty < 0) return;

      const res = await fetch('/cart/update/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCsrfToken() },
        body: `product_id=${productId}&quantity=${qty}`,
      });
      if (res.ok) location.reload();
    });
  });
});
