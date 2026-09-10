(() => {
  const cover = document.querySelector('.cover');
  if (!cover) return;

  // Without motion paths, the original sixteen posters remain a static collage.
  if (!CSS.supports('offset-path', 'path("M0 0 L1 1")')) return;
  const collage = cover.querySelector('.cover-collage');
  const originals = [...collage.children];
  const templates = originals.map((tile) => tile.cloneNode(true));
  let tiles = [...originals];
  let media = [];
  const button = cover.querySelector('.cover-pause');
  const label = button.querySelector('.cover-pause-label');
  const icon = button.querySelector('.cover-pause-icon');
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = motionPreference.matches;
  let visible = true;
  let active;
  let lastLayout;

  function prepareTile(tile) {
    const image = tile.querySelector('img[data-animation]');
    if (!image) return;
    image.dataset.poster = image.getAttribute('src');
    image.addEventListener('error', () => {
      if (image.getAttribute('src') !== image.dataset.poster) {
        image.src = image.dataset.poster;
      }
    });
  }
  originals.forEach(prepareTile);

  function layoutFlow() {
    const width = collage.clientWidth;
    const height = collage.clientHeight;
    const tileWidth = parseFloat(getComputedStyle(tiles[0]).width);
    const gap = parseFloat(getComputedStyle(collage).getPropertyValue('--tile-gap'));
    const layout = [width, height, tileWidth, gap].join(':');
    if (!width || !height || layout === lastLayout) return;
    lastLayout = layout;

    const tileHeight = (height - 3 * gap) / 4;
    const step = tileHeight + gap;
    const y = Array.from({ length: 4 }, (_, row) => tileHeight / 2 + row * step);
    const left = -tileWidth;
    const right = width + tileWidth;
    const returnX = left - step - tileWidth;
    // One closed belt visits all four rows. Turns and the return leg stay offscreen.
    const path = [
      `M ${left} ${y[0]} H ${right}`,
      `C ${right + step} ${y[0]} ${right + step} ${y[1]} ${right} ${y[1]}`,
      `H ${left}`,
      `C ${left - step} ${y[1]} ${left - step} ${y[2]} ${left} ${y[2]}`,
      `H ${right}`,
      `C ${right + step} ${y[2]} ${right + step} ${y[3]} ${right} ${y[3]}`,
      `H ${returnX} V ${y[0]} Z`,
    ].join(' ');
    const measure = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    measure.setAttribute('d', path);
    const length = measure.getTotalLength();
    const count = Math.max(originals.length, Math.floor(length / (tileWidth + gap)));
    const duration = length / 32;

    while (tiles.length < count) {
      const tile = templates[tiles.length % templates.length].cloneNode(true);
      prepareTile(tile);
      collage.append(tile);
      tiles.push(tile);
    }
    while (tiles.length > count) tiles.pop().remove();
    collage.style.setProperty('--tile-height', `${tileHeight}px`);
    collage.style.setProperty('--cover-path', `path("${path}")`);
    collage.style.setProperty('--flow-duration', `${duration}s`);
    tiles.forEach((tile, index) => {
      tile.style.setProperty('--flow-delay', `${-duration * index / count}s`);
    });
    media = [...collage.querySelectorAll('img[data-animation]')];
    cover.classList.add('has-animation');
    active = undefined;
    updateVisibility();
  }

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
  layoutFlow();
  new ResizeObserver(layoutFlow).observe(collage);
})();
