// KaTeX 0.19.0. Arithmatex already rewrote `$` and `$$` into these delimiters.
(() => {
  const render = (body) => {
    if (typeof renderMathInElement !== "function" || !(body instanceof Element)) {
      return;
    }
    renderMathInElement(body, {
      delimiters: [
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true },
      ],
    });
  };

  if (typeof document$ !== "undefined" && typeof document$.subscribe === "function") {
    document$.subscribe(({ body }) => render(body));
    return;
  }
  document.addEventListener("DOMContentLoaded", () => render(document.body));
})();
