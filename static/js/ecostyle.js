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
  const quantity  = parseInt(btn.dataset.quantity || '1');

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
        el.style.display = data.cart_total_items === 0 ? 'none' : 'flex';
      });
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

// ── Eliminar item del carrito (AJAX) ──────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  document.querySelectorAll('.btn-remove-item').forEach(btn => {
    btn.addEventListener('click', async function () {
      const productId = this.dataset.product;
      const itemRow   = this.closest('.eco-cart-item');

      try {
        const res = await fetch('/cart/remove/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken(),
          },
          body: `product_id=${productId}`,
        });

        const data = await res.json();

        if (data.success) {
          // ✅ Eliminar la fila del DOM con animación
          if (itemRow) {
            itemRow.style.transition = 'opacity 0.3s ease';
            itemRow.style.opacity    = '0';
            setTimeout(() => itemRow.remove(), 300);
          }

          // Actualizar badge del navbar
          document.querySelectorAll('.eco-cart-badge').forEach(el => {
            el.textContent   = data.cart_total_items;
            el.style.display = data.cart_total_items === 0 ? 'none' : 'flex';
          });

          // Toast de confirmación
          showToast('Producto eliminado del carrito.');

          // Si no quedan items, recargar para mostrar carrito vacío
          if (data.cart_total_items === 0) {
            setTimeout(() => location.reload(), 400);
          }

        } else {
          showToast(data.message || 'No se pudo eliminar.', 'error');
        }

      } catch (err) {
        console.error('Error al eliminar:', err);
        showToast('Error de conexión.', 'error');
      }
    });
  });

});

// ── Quantity controls en carrito ──────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  document.querySelectorAll('.eco-qty-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      const productId = this.dataset.product;                        // data-product
      const control   = this.closest('.eco-qty-control');
      const span      = control.querySelector('.qty-value');         // <span class="qty-value">

      if (!span) return;

      let qty = parseInt(span.textContent.trim(), 10);
      if (isNaN(qty)) return;

      qty += this.dataset.action === 'plus' ? 1 : -1;
      if (qty < 0) return;

      try {
        const res = await fetch('/cart/update/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCsrfToken(),
          },
          body: `product_id=${productId}&quantity=${qty}`,
        });

        const data = await res.json();

        if (data.success) {
          if (qty === 0) {
            location.reload();
            return;
          }

          // Actualizar cantidad en el span
          span.textContent = qty;

          // Actualizar total de línea
          const lineTotal = document.querySelector(`.line-total[data-product="${productId}"]`);
          if (lineTotal && data.line_total) {
            lineTotal.textContent = `$${parseFloat(data.line_total).toFixed(0)} MXN`;
          }

          // Actualizar resumen
          const subtotalEl = document.getElementById('cart-subtotal');
          const totalEl    = document.getElementById('cart-total');
          if (subtotalEl && data.subtotal) {
            subtotalEl.textContent = `$${parseFloat(data.subtotal).toFixed(0)} MXN`;
          }
          if (totalEl && data.total) {
            totalEl.textContent = `$${parseFloat(data.total).toFixed(0)} MXN`;
          }

          // Actualizar badge navbar
          document.querySelectorAll('.eco-cart-badge').forEach(el => {
            el.textContent   = data.cart_total_items;
            el.style.display = data.cart_total_items === 0 ? 'none' : 'flex';
          });

        } else {
          showToast(data.message || 'No se pudo actualizar.', 'error');
        }
      } catch (err) {
        console.error('Error en qty update:', err);
        showToast('Error de conexión.', 'error');
      }
    });
  });

});