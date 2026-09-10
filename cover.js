(() => {
  const cover = document.querySelector('.cover');
  if (!cover) return;

  // Identical groups make each row wrap continuously, including on wide screens.
  cover.querySelectorAll('.cover-row').forEach((row) => {
    row.append(row.querySelector('.cover-group').cloneNode(true));
  });
  cover.classList.add('has-animation');

  const media = [...cover.querySelectorAll('img[data-animation]')];
  media.forEach((image) => { image.dataset.poster = image.getAttribute('src'); });
  const button = cover.querySelector('.cover-pause');
  const label = button.querySelector('.cover-pause-label');
  const icon = button.querySelector('.cover-pause-icon');
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = motionPreference.matches;
  let visible = true;
  let active;

  function updatePlayback() {
    const playing = !paused && visible && !document.hidden;
    button.setAttribute('aria-pressed', String(paused));
    button.setAttribute('aria-label', paused ? 'Play cover animation' : 'Pause cover animation');
    label.textContent = paused ? 'Play' : 'Pause';
    icon.textContent = paused ? '▷' : 'Ⅱ';
    if (active === playing) return;
    active = playing;
    cover.classList.toggle('is-playing', playing);
    // GIFs cannot be paused in place. Posters also stop their decoding offscreen.
    media.forEach((image) => {
      image.src = playing ? image.dataset.animation : image.dataset.poster;
    });
  }

  media.forEach((image) => {
    image.addEventListener('error', () => {
      if (image.getAttribute('src') !== image.dataset.poster) {
        image.src = image.dataset.poster;
      }
    });
  });
  button.hidden = false;
  button.addEventListener('click', () => {
    paused = !paused;
    updatePlayback();
  });
  motionPreference.addEventListener('change', (event) => {
    paused = event.matches;
    updateVisibility();
  });
  document.addEventListener('visibilitychange', updatePlayback);
  let visibilityFrame;
  function updateVisibility() {
    visibilityFrame = undefined;
    const bounds = cover.getBoundingClientRect();
    visible = bounds.bottom > 0 && bounds.top < window.innerHeight;
    // The introduction stays in normal flow as its backdrop dissolves into white.
    const progress = Math.min(1, Math.max(0, -bounds.top / bounds.height));
    cover.style.setProperty('--cover-fade', motionPreference.matches ? '0' : String(progress * .75));
    updatePlayback();
  }
  function scheduleVisibility() {
    if (visibilityFrame === undefined) {
      visibilityFrame = window.requestAnimationFrame(updateVisibility);
    }
  }
  window.addEventListener('scroll', scheduleVisibility, { passive: true });
  window.addEventListener('resize', scheduleVisibility);
  updateVisibility();
})();
