/**
 * LOOZY Cafe – Interactive Client-Side JavaScript
 * Dynamic Cart, Search Filtering, Toast Notifications, & AJAX Updates
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialize Toasts
  const toastEl = document.getElementById('liveToast');
  let toastInstance = null;
  if (toastEl && typeof bootstrap !== 'undefined') {
    toastInstance = new bootstrap.Toast(toastEl, { delay: 3500 });
  }

  function showToast(title, message, isSuccess = true) {
    if (!toastEl) return;
    const titleEl = document.getElementById('toastTitle');
    const msgEl = document.getElementById('toastMessage');
    const iconEl = document.getElementById('toastIcon');

    if (titleEl) titleEl.innerText = title;
    if (msgEl) msgEl.innerText = message;
    if (iconEl) {
      iconEl.className = isSuccess ? 'bi bi-check-circle-fill text-success fs-5' : 'bi bi-exclamation-triangle-fill text-warning fs-5';
    }
    if (toastInstance) toastInstance.show();
  }

  // 2. Global AJAX Add To Cart
  document.querySelectorAll('.ajax-add-cart-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = this.querySelector('button[type="submit"]');
      const originalHtml = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span> Adding...';
      }

      const formData = new FormData(this);

      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // Update navbar badges
          document.querySelectorAll('.cart-badge-count').forEach(badge => {
            badge.innerText = data.cart_count;
            badge.classList.add('animate__animated', 'animate__pulse');
            setTimeout(() => badge.classList.remove('animate__animated', 'animate__pulse'), 800);
          });

          showToast('Added to Cart! 🍔', data.message || 'Item added to your order.');

          if (submitBtn) {
            submitBtn.innerHTML = '<i class="bi bi-check2"></i> Added!';
            submitBtn.classList.add('btn-success');
            setTimeout(() => {
              submitBtn.innerHTML = originalHtml;
              submitBtn.classList.remove('btn-success');
              submitBtn.disabled = false;
            }, 1200);
          }
        } else {
          showToast('Notice', data.message || 'Could not add item to cart.', false);
          if (submitBtn) {
            submitBtn.innerHTML = originalHtml;
            submitBtn.disabled = false;
          }
        }
      })
      .catch(err => {
        console.error('Add to cart error:', err);
        // Fallback to normal submission if fetch fails
        form.submit();
      });
    });
  });

  // 3. Cart Page Dynamic Quantity & Remove Handlers
  const cartContainer = document.getElementById('cartPageContainer');
  if (cartContainer) {
    // Quantity Buttons (Increase/Decrease)
    cartContainer.addEventListener('click', function (e) {
      const btn = e.target.closest('.cart-qty-ajax-btn');
      if (btn) {
        e.preventDefault();
        const action = btn.dataset.action;
        const productId = btn.dataset.productId;
        const row = document.getElementById(`cart-row-${productId}`);

        const formData = new FormData();
        formData.append('action', action);

        fetch(`/cart/update/${productId}`, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (data.is_removed) {
              if (row) {
                row.style.transition = 'all 0.3s ease';
                row.style.opacity = '0';
                setTimeout(() => {
                  row.remove();
                  checkIfCartEmpty();
                }, 300);
              }
            } else {
              const qtyDisplay = document.getElementById(`qty-display-${productId}`);
              const subtotalDisplay = document.getElementById(`item-subtotal-${productId}`);
              if (qtyDisplay) qtyDisplay.innerText = data.item_quantity;
              if (subtotalDisplay) subtotalDisplay.innerText = `₹${data.item_subtotal.toFixed(2)}`;
            }
            updateCartSummaryUI(data);
          }
        })
        .catch(err => console.error(err));
      }

      // Remove button
      const removeBtn = e.target.closest('.cart-remove-ajax-btn');
      if (removeBtn) {
        e.preventDefault();
        const productId = removeBtn.dataset.productId;
        const row = document.getElementById(`cart-row-${productId}`);

        fetch(`/cart/remove/${productId}`, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (row) {
              row.style.transition = 'all 0.3s ease';
              row.style.opacity = '0';
              setTimeout(() => {
                row.remove();
                checkIfCartEmpty();
              }, 300);
            }
            updateCartSummaryUI(data);
            showToast('Cart Updated', data.message);
          }
        })
        .catch(err => console.error(err));
      }
    });

    function updateCartSummaryUI(data) {
      // Update badge
      document.querySelectorAll('.cart-badge-count').forEach(badge => {
        badge.innerText = data.cart_count;
      });

      const subtotalEl = document.getElementById('summarySubtotal');
      const taxEl = document.getElementById('summaryTax');
      const deliveryEl = document.getElementById('summaryDelivery');
      const totalEl = document.getElementById('summaryGrandTotal');
      const itemCountEl = document.getElementById('summaryItemCount');

      if (subtotalEl) subtotalEl.innerText = `₹${data.subtotal.toFixed(2)}`;
      if (taxEl) taxEl.innerText = `₹${data.tax.toFixed(2)}`;
      if (deliveryEl) {
        deliveryEl.innerText = data.delivery_fee === 0 ? 'FREE' : `₹${data.delivery_fee.toFixed(2)}`;
      }
      if (totalEl) totalEl.innerText = `₹${data.grand_total.toFixed(2)}`;
      if (itemCountEl) itemCountEl.innerText = data.cart_count;
    }

    function checkIfCartEmpty() {
      const itemsLeft = document.querySelectorAll('.cart-item-row');
      if (itemsLeft.length === 0) {
        const fullTableSection = document.getElementById('cartFullSection');
        const emptyState = document.getElementById('cartEmptySection');
        if (fullTableSection) fullTableSection.classList.add('d-none');
        if (emptyState) emptyState.classList.remove('d-none');
      }
    }
  }

  // 4. Live Menu Search Filter (instant in-page filtering)
  const menuSearchInput = document.getElementById('menuLiveSearch');
  if (menuSearchInput) {
    menuSearchInput.addEventListener('input', function () {
      const val = this.value.toLowerCase().trim();
      const items = document.querySelectorAll('.menu-product-col');
      let visibleCount = 0;

      items.forEach(item => {
        const title = item.dataset.name ? item.dataset.name.toLowerCase() : '';
        const desc = item.dataset.desc ? item.dataset.desc.toLowerCase() : '';
        const category = item.dataset.category ? item.dataset.category.toLowerCase() : '';

        if (title.includes(val) || desc.includes(val) || category.includes(val)) {
          item.style.display = '';
          visibleCount++;
        } else {
          item.style.display = 'none';
        }
      });

      const emptyResults = document.getElementById('noMenuResults');
      if (emptyResults) {
        if (visibleCount === 0) {
          emptyResults.classList.remove('d-none');
        } else {
          emptyResults.classList.add('d-none');
        }
      }
    });
  }

  // 5. Auto dismiss bootstrap alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
        const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
        if (alertInstance) alertInstance.close();
      }
    }, 5000);
  });
});
