/* statement-band: wrap each word so the headline lights up word by word when revealed.
   A highlighted phrase (.bl-hl) stays one unit so gradient text keeps working. */
(function () {
  if (window.BL.RM) return;
  document.querySelectorAll('[data-split-words]').forEach(function (el) {
    var n = 0;
    function unit(node) {
      node.classList.add('bl-sw');
      node.style.setProperty('--w', String(n++));
    }
    Array.prototype.slice.call(el.childNodes).forEach(function (child) {
      if (child.nodeType === 1) { unit(child); return; }
      if (child.nodeType !== 3) return;
      var frag = document.createDocumentFragment();
      child.textContent.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
        var span = document.createElement('span');
        span.textContent = part;
        unit(span);
        frag.appendChild(span);
      });
      el.replaceChild(frag, child);
    });
  });
})();
