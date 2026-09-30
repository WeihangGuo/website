(() => {
  const entries = [...document.querySelectorAll('.research-keyword')]
    .map((trigger) => ({
      trigger,
      tooltip: document.getElementById(trigger.getAttribute('aria-describedby')),
      triggerHovered: false,
      tooltipHovered: false,
      keyboardFocused: false,
      pinned: false,
    }))
    .filter((entry) => entry.tooltip);
  if (!entries.length) return;

  let active;
  let closeTimer;

  function cancelClose() {
    window.clearTimeout(closeTimer);
    closeTimer = undefined;
  }

  function close() {
    cancelClose();
    if (!active) return;
    active.tooltip.hidden = true;
    active.trigger.classList.remove('is-active');
    active.tooltipHovered = false;
    active.pinned = false;
    active = undefined;
  }

  function position(entry) {
    const margin = 16;
    const gap = 8;
    const triggerBounds = entry.trigger.getBoundingClientRect();
    const tooltipBounds = entry.tooltip.getBoundingClientRect();
    const width = window.innerWidth;
    const height = window.innerHeight;
    const maxLeft = Math.max(margin, width - tooltipBounds.width - margin);
    const maxTop = Math.max(margin, height - tooltipBounds.height - margin);
    const left = Math.min(maxLeft, Math.max(margin,
      triggerBounds.left + (triggerBounds.width - tooltipBounds.width) / 2));
    let top = triggerBounds.bottom + gap;
    if (top + tooltipBounds.height > height - margin) {
      top = triggerBounds.top - tooltipBounds.height - gap;
    }
    entry.tooltip.style.left = `${left}px`;
    entry.tooltip.style.top = `${Math.min(maxTop, Math.max(margin, top))}px`;
  }

  function open(entry) {
    cancelClose();
    if (active !== entry) close();
    active = entry;
    entry.tooltip.hidden = false;
    entry.trigger.classList.add('is-active');
    position(entry);
  }

  function scheduleClose(entry) {
    cancelClose();
    // Allow the pointer to cross the small gap into the tooltip itself.
    closeTimer = window.setTimeout(() => {
      if (active === entry && !entry.triggerHovered && !entry.tooltipHovered
          && !entry.keyboardFocused && !entry.pinned) close();
    }, 180);
  }

  entries.forEach((entry) => {
    const { trigger, tooltip } = entry;
    trigger.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'touch') return;
      entry.triggerHovered = true;
      open(entry);
    });
    trigger.addEventListener('pointerleave', (event) => {
      if (event.pointerType === 'touch') return;
      entry.triggerHovered = false;
      scheduleClose(entry);
    });
    trigger.addEventListener('pointerdown', () => {
      entry.keyboardFocused = false;
    });
    trigger.addEventListener('focus', () => {
      entry.keyboardFocused = trigger.matches(':focus-visible');
      if (entry.keyboardFocused) open(entry);
    });
    trigger.addEventListener('blur', () => {
      entry.keyboardFocused = false;
      entry.pinned = false;
      scheduleClose(entry);
    });
    trigger.addEventListener('click', () => {
      if (active === entry && entry.pinned) {
        close();
      } else {
        // Hover or keyboard focus may already have opened it before this click.
        open(entry);
        entry.pinned = true;
      }
    });
    tooltip.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'touch') return;
      entry.tooltipHovered = true;
      cancelClose();
    });
    tooltip.addEventListener('pointerleave', (event) => {
      if (event.pointerType === 'touch') return;
      entry.tooltipHovered = false;
      scheduleClose(entry);
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') close();
  });
  document.addEventListener('pointerdown', (event) => {
    if (active && !active.trigger.contains(event.target)
        && !active.tooltip.contains(event.target)) close();
  });
  window.addEventListener('scroll', close, { passive: true, capture: true });
  window.addEventListener('resize', close);
})();
