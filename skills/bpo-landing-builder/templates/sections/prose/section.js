/* prose: toc-spy. The contents link of the block crossing the upper third of the screen is marked current. */
(function () {
  var navs = document.querySelectorAll('[data-toc]');
  if (!navs.length || !('IntersectionObserver' in window)) return;
  navs.forEach(function (nav) {
    var links = [].slice.call(nav.querySelectorAll('a[href^="#"]'));
    var blocks = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
    var visible = {};
    function mark() {
      var current = null;
      blocks.forEach(function (b, i) { if (b && visible[b.id] && current === null) current = i; });
      if (current === null) return;
      links.forEach(function (a, i) {
        if (i === current) a.setAttribute('aria-current', 'location');
        else a.removeAttribute('aria-current');
      });
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
      mark();
    }, { rootMargin: '-20% 0px -60% 0px' });
    blocks.forEach(function (b) { if (b) io.observe(b); });
  });
})();
