/**
 * EcoStyle – JavaScript principal
 * Módulos: Navbar scroll, Carrito AJAX, Notificaciones, Cantidad
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Navbar: efecto scroll ──────────────────────────────────────────
  const navbar = document.querySelector('.navbar-ecostyle');
  if (navbar) {
    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 30);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ── Notificaciones automáticas (Django messages) ───────────────────
  const toasts = document.querySelectorAll('.eco-toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.transition = 'opacity 0.5s ease';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 500);
    }, 4000);
  });

  // ── Agregar al carrito (AJAX) ──────────────────────────────────────
  document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
    btn.addEventListener('click', async function (e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const quantity = document.querySelector('#qty-input')?.value || 1;
      const csrfToken = getCsrfToken();

      const originalText = this.innerHTML;
      this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Añadiendo...';
      this.disabled = true;

      try {
        const res = await fetch(`/cart/add/${productId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `quantity=${quantity}`,
        });

        const data = await res.json();

        if (data.success) {
          showNotification(data.message, 'success');
          updateCartCount(data.cart_count);
          this.innerHTML = '✓ Añadido';
          setTimeout(() => { this.innerHTML = originalText; this.disabled = false; }, 1500);
        } else {
          showNotification(data.message, 'error');
          this.innerHTML = originalText;
          this.disabled = false;
        }
      } catch (err) {
        showNotification('Error de conexión. Intenta de nuevo.', 'error');
        this.innerHTML = originalText;
        this.disabled = false;
      }
    });
  });

  // ── Controles de cantidad en el carrito ────────────────────────────
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
      const productId = this.dataset.productId;
      const input = document.querySelector(`.qty-input[data-product-id="${productId}"]`);
      if (!input) return;

      let qty = parseInt(input.value);
      if (this.dataset.action === 'increase') qty++;
      else if (this.dataset.action === 'decrease') qty--;

      if (qty < 0) return;
      await updateCartItem(productId, qty);
    });
  });

  // ── Eliminar ítem del carrito ──────────────────────────────────────
  document.querySelectorAll('.btn-remove-item').forEach(btn => {
    btn.addEventListener('click', async function () {
      const productId = this.dataset.productId;
      const csrfToken = getCsrfToken();

      const row = document.querySelector(`.cart-item-row[data-product-id="${productId}"]`);
      if (row) {
        row.style.opacity = '0.5';
        row.style.pointerEvents = 'none';
      }

      try {
        const res = await fetch(`/cart/remove/${productId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          },
        });
        const data = await res.json();

        if (data.success) {
          row?.remove();
          updateCartCount(data.cart_count);
          updateCartTotals(data);

          if (data.cart_count === 0) {
            const cartContainer = document.querySelector('.cart-items-container');
            if (cartContainer) {
              cartContainer.innerHTML = '<p class="text-center py-5 text-muted">Tu carrito está vacío.</p>';
            }
          }
        }
      } catch (err) {
        console.error('Error al eliminar ítem:', err);
        if (row) { row.style.opacity = '1'; row.style.pointerEvents = 'auto'; }
      }
    });
  });

  // ── Helpers ────────────────────────────────────────────────────────
  function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value
        || document.cookie.split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1] || '';
  }

  async function updateCartItem(productId, quantity) {
    const csrfToken = getCsrfToken();
    const input = document.querySelector(`.qty-input[data-product-id="${productId}"]`);

    try {
      const res = await fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity }),
      });
      const data = await res.json();

      if (data.success) {
        if (data.removed) {
          document.querySelector(`.cart-item-row[data-product-id="${productId}"]`)?.remove();
        } else {
          if (input) input.value = quantity;
          const lineTotal = document.querySelector(`.line-total[data-product-id="${productId}"]`);
          if (lineTotal) lineTotal.textContent = formatCurrency(data.item_total);
        }
        updateCartCount(data.cart_count);
        updateCartTotals(data);
      } else {
        showNotification(data.message, 'error');
      }
    } catch (err) {
      console.error('Error actualizando carrito:', err);
    }
  }

  function updateCartCount(count) {
    document.querySelectorAll('.cart-count').forEach(el => {
      el.textContent = count;
      el.style.display = count > 0 ? 'flex' : 'none';
    });
  }

  function updateCartTotals(data) {
    const fmt = formatCurrency;
    const el = (id) => document.querySelector(id);
    if (el('#cart-subtotal')) el('#cart-subtotal').textContent = fmt(data.subtotal);
    if (el('#cart-tax'))      el('#cart-tax').textContent      = fmt(data.tax);
    if (el('#cart-shipping')) el('#cart-shipping').textContent = fmt(data.shipping);
    if (el('#cart-total'))    el('#cart-total').textContent    = fmt(data.total);
  }

  function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
    }).format(amount);
  }

  function showNotification(message, type = 'success') {
    const container = document.getElementById('toast-container')
        || (() => {
          const div = document.createElement('div');
          div.id = 'toast-container';
          div.style.cssText = 'position:fixed;top:1.5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;';
          document.body.appendChild(div);
          return div;
        })();

    const toast = document.createElement('div');
    toast.className = `eco-toast alert-eco-${type}`;
    toast.style.cssText = `
      padding: 0.875rem 1.25rem;
      border-radius: 6px;
      font-size: 0.875rem;
      max-width: 340px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.12);
      animation: fadeInUp 0.3s ease-out;
      background: ${type === 'success' ? 'rgba(168,196,184,0.95)' : 'rgba(232,168,130,0.95)'};
      border: 1px solid ${type === 'success' ? '#5C7A6B' : '#C4744A'};
      color: ${type === 'success' ? '#2C4A3E' : '#7B3B1F'};
      backdrop-filter: blur(8px);
    `;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.4s';
      setTimeout(() => toast.remove(), 400);
    }, 3500);
  }

  // Exponer para uso global (en templates inline)
  window.EcoStyle = { showNotification, updateCartCount };
});
