/* statement-ink: scroll-ink-paragraph. The paragraph is wrapped word by word (text normalised to NFC so Vietnamese
   letters keep their marks; inline markup such as the .bl-hl accent is walked into, not flattened). The words stay
   readable to screen readers: no aria-hidden, no aria-label on the paragraph. Each word's opacity runs from 0.2 to 1
   in reading order while the paragraph moves from 85% to 40% of the screen height (GSAP scrub, one ScrollTrigger).
   Reduced motion: no wrapping effect, the paragraph is in full ink. */
(function () {
  var BL = window.BL, gsap = window.gsap;
  function wrap(el) {
    if (el.__inkWords) return el.__inkWords;
    var words = [];
    (function walk(node) {
      [].slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 1) { if (n.tagName !== 'BR') walk(n); return; }
        if (n.nodeType !== 3) return;
        var frag = document.createDocumentFragment();
        n.nodeValue.normalize('NFC').split(/(\s+)/).forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
          var w = document.createElement('span');
          w.className = 'bl-statement-ink__w';
          w.textContent = part;
          words.push(w);
          frag.appendChild(w);
        });
        n.parentNode.replaceChild(frag, n);
      });
    })(el);
    el.__inkWords = words;
    return words;
  }

  document.querySelectorAll('[data-ink]').forEach(function (el) {
    if (!BL || !gsap || !window.ScrollTrigger) return;
    BL.motion.media(function (reduce) {
      if (reduce) return;
      var words = wrap(el);
      gsap.fromTo(words, { opacity: 0.2 }, {
        opacity: 1, ease: 'none', duration: 1, stagger: 0.35,
        scrollTrigger: { trigger: el, start: 'top 85%', end: 'bottom 40%', scrub: 0.4 }
      });
    });
  });
})();
