import LocomotiveScroll from 'locomotive-scroll';

const anchorOffset = -24;

export function createSmoothScroll() {
  const scroll = new LocomotiveScroll({
    lenisOptions: {
      lerp: 0.12,
      duration: 0.8,
      smoothWheel: true,
      smoothTouch: false,
    },
  });

  document.addEventListener('click', (event) => {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }

    const link = (event.target as Element | null)?.closest('a[href^="#"]');
    if (!(link instanceof HTMLAnchorElement)) return;

    const id = link.getAttribute('href')?.slice(1);
    if (!id) return;

    const target = document.getElementById(id);
    if (!target) return;

    event.preventDefault();
    scroll.scrollTo(target, { offset: anchorOffset });
    history.pushState(null, '', `#${id}`);
  });

  return scroll;
}

if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  createSmoothScroll();
}
