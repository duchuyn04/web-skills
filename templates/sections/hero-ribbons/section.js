/* hero-ribbons: ribbons, word-rise headline, dotted globe with arcs, carousel with progress dots, one pause control */
(function () {
  var R = window.BLRibbons;
  document.querySelectorAll('[data-hero-ribbons]').forEach(function (hero) {
    if (!R) return;
    var RM = R.RM, DPR = R.DPR, TAU = Math.PI * 2;
    var css = getComputedStyle(hero);
    var ink = css.getPropertyValue('--text-strong').trim() || '#fff';
    var accent = css.getPropertyValue('--c-accent').trim() || '#c2410c';
    var primary = css.getPropertyValue('--c-primary').trim() || '#0a1128';

    /* ribbons */
    var lines = hero.querySelector('[data-rib-lines]');
    if (lines) R.waves(lines, hero, {
      color: ink, revealMs: 2200, mouse: true,
      ribbons: [
        { y0: 0.92, y1: 0.38, amp: 0.07, freq: 0.9, spread: 0.26, twist: 1.7, shift: 0.4, speed: 0.00021, lines: 34, alpha: 0.42 },
        { y0: 0.12, y1: 0.78, amp: 0.06, freq: 1.2, spread: 0.16, twist: 1.2, shift: 2.1, speed: -0.00015, lines: 22, alpha: 0.24 }
      ]
    });
    (hero.getAttribute('data-echo') || '').split(/\s+/).forEach(function (id) {
      var sec = id && document.getElementById(id);
      if (!sec) return;
      var c = document.createElement('canvas');
      c.className = 'bl-rib-echo';
      c.setAttribute('aria-hidden', 'true');
      sec.insertBefore(c, sec.firstChild);
      R.waves(c, sec, {
        color: R.lighten(accent, 0.25), revealMs: 2600, mouse: true,
        ribbons: [{ y0: 0.95, y1: 0.2, amp: 0.08, freq: 0.8, spread: 0.3, twist: 1.4, shift: 1.2, speed: 0.00012, lines: 26, alpha: 0.3 }]
      });
    });

    /* word-rise headline */
    var title = hero.querySelector('[data-split]');
    var n = 0;
    function split(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var outer = document.createElement('span'), inner = document.createElement('span');
            outer.className = 'bl-rib-w';
            inner.textContent = part;
            inner.style.setProperty('--w', String(n++));
            outer.appendChild(inner);
            frag.appendChild(outer);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) { split(child); }
      });
    }
    if (title && !RM) split(title);
    requestAnimationFrame(function () { requestAnimationFrame(function () { hero.classList.add('is-live'); }); });

    /* dotted globe: 2.5 degree land cells of partials/world-dots.html, packed as row*144+col in base 36, 3 chars each */
    var DOTS = '00r00u00v00y00z01001101201301401501801901a01b01c01d01e01f01g01h01i01j01k01l01m01n01o01p01q01r02502602703403504n04q04s04v04w04z05805905a05b05c05d05e05f05g05h05i05j05k05l05m05n05o05p05q05r06o06p06q07307407507607707808m08n08o08p08y08z09109e09f09g09h09i09j09k09l09m09n09o09p09q09r0al0am0ax0ay0az0b00b10b20b30b40b50b60b70b80bk0c00c90cn0cp0cq0cr0cs0ct0cx0cy0d00d10d20d30d40d50d60df0dg0dh0di0dj0dk0dl0dm0dn0do0dp0dq0el0em0er0es0et0ev0ew0ex0ey0ez0f00f10f20f30f40f50f60f70f80f90fa0fb0fc0fd0fe0ff0fh0fi0fj0fk0fl0fm0fn0fo0g50g60g70g80g90ga0gb0gc0gd0ge0gf0gg0gh0gi0gj0gk0gl0gm0gn0go0gp0gr0gt0gy0gz0h00h20h30h60h70h80hf0hg0hh0hi0hj0hk0hl0hm0hn0ho0i70i80i90ia0ib0ic0id0ie0il0in0io0ip0iq0is0iu0iv0iw0ix0iy0iz0j00j10j20j30j40j50j60j70j80j90ja0jb0jc0jd0je0jf0jg0jh0ji0jj0jk0jl0jm0jn0jo0jp0jq0jr0js0jt0ju0jv0jw0jx0jy0jz0k00k10k20k30k60k70k80k90ka0kb0kc0kd0ke0kf0kg0kh0ki0kj0kk0kl0km0kn0ko0kp0kq0kr0ks0kt0ku0kv0kw0kx0ky0kz0l00l10l60l70l80l90la0lf0lg0lh0li0lj0lk0ll0lt0m50m60m70m80m90ma0mb0mc0md0mf0mi0mj0mk0ml0mm0mn0mo0mp0mq0mr0ms0mt0mu0mv0mw0mx0my0mz0n00n10n20n30n40n50n60n70n80n90na0nb0nc0nd0ne0nf0ng0nh0ni0nj0nk0nl0nm0nn0no0np0nq0nr0ns0nt0nu0nv0nw0nx0ny0nz0o80o90oa0ob0oc0od0oe0of0og0oh0oi0oj0ok0ol0om0on0oo0op0oq0or0os0ot0ou0ov0ow0ox0oy0oz0p10p30p70p80p90pf0pg0ph0pi0pj0ps0q40q50q60q70q90qa0qb0qc0qd0qe0qf0qg0qh0qi0qj0qk0ql0qm0qn0qo0qp0qq0qr0qs0qt0qu0qv0qw0qx0qy0qz0r00r10r20r30r40r50r60r70r80r90ra0rb0rc0rd0re0rf0rg0rh0ri0rj0rk0rl0rm0rn0ro0rp0rq0rr0rs0rt0ru0rv0rw0rx0ry0s60s70s80s90sa0sb0sc0sd0se0sf0sg0sh0si0sj0sk0sl0sm0sn0so0sp0sq0sr0ss0st0su0sv0sw0sx0t50t60tg0th0ti0u20u30u40u50u60u90ua0ub0uc0ud0ue0uf0ug0uh0ui0uj0uk0ul0um0un0uo0up0uq0ur0us0ut0uu0uv0uw0ux0uy0uz0v00v10v20v30v40v50v60v70v80v90va0vb0vc0vd0ve0vf0vg0vh0vi0vj0vk0vl0vm0vn0vo0vp0vq0vs0vt0vu0vv0vw0w70w80w90wa0wh0wi0wj0wk0wl0wm0wn0wo0wp0wq0wr0ws0wt0wu0wv0ww0wx0wy0x50x60x70x80xa0y20y30y40y50y60y90ya0yb0yc0yd0ye0yf0yg0yh0yi0yj0yk0yl0ym0yn0yo0yp0yq0yr0ys0yt0yu0yv0yw0yx0yy0yz0z00z10z20z30z40z50z60z70z80z90za0zb0zc0zd0ze0zf0zg0zh0zi0zj0zk0zs10810j10k10l10m10n10o10p10q10r10s10t10u10v10w10x10y10z11011511611711811911a11y12312512812912a12b12c12d12e12f12g12h12i12j12k12l12m12n12o12p12q12r12s12t12u12v12w12x12y12z13013113213313413513613713813913a13b13c13d13e13f13g13h13i13q13r13s14k14l14m14n14o14p14q14r14s14t14u14v14w14x14y14z15015115215415515615715815915a15b15c15w15x15z16316416516616716816916a16b16c16d16e16f16g16h16i16j16k16l16m16n16o16p16q16r16s16t16u16v16w16x16y16z17017117217317417517617717817917a17b17c17d17e17f17g17h17i17j17q17r18l18m18n18o18p18q18r18s18t18u18v18w18x18y18z19019119219319419519619719819919a19b19c19d19y19z1a01a11a21a31a41a51a61a71a81a91aa1ab1ac1ad1ae1af1ag1ah1ai1aj1ak1al1am1an1ao1ap1aq1ar1as1at1au1av1aw1ax1ay1az1b01b11b21b31b41b51b61b71b81b91ba1bb1bc1bd1be1bf1bg1bh1bi1bj1cm1cn1co1cp1cq1cr1cs1ct1cu1cv1cw1cx1cy1cz1d01d11d21d31d41d51d61d71d91dc1dd1de1dy1dz1e01e11e21e31e41e51e61e71e81e91ea1eb1ec1ed1ee1ef1eg1eh1ei1ej1ek1el1em1en1eo1ep1eq1er1es1et1eu1ev1ew1ex1ey1ez1f01f11f21f31f41f51f61f71f81f91fa1fb1fc1fd1fe1ff1fg1fh1fi1fj1gm1gn1go1gp1gq1gr1gs1gt1gu1gv1gw1gx1gy1gz1h01h11h21h31h41h51h61h71h81h91hz1i01i11i21i31i41i51i61i71i81i91ia1ib1id1if1ig1ih1ii1ij1ik1il1im1in1io1ip1iq1ir1is1it1iu1iv1iw1ix1iy1iz1j01j11j21j31j41j51j61j71j81j91ja1jb1jc1jd1je1jf1jg1jh1ji1km1kn1ko1kp1kq1kr1ks1kt1ku1kv1kw1kx1ky1kz1l01l11l21l31l41l51l61l71lz1m01m11m21m41m61m71m81m91ma1mg1mh1mi1mj1mk1ml1mm1mn1mo1mp1mq1mr1ms1mt1mu1mv1mw1mx1my1mz1n01n11n21n31n41n51n61n71n81n91na1nb1nc1nd1ne1nf1ng1nh1nl1om1on1oo1op1oq1or1os1ot1ou1ov1ow1ox1oy1oz1p01p11p21p31p41p51p61pw1px1py1pz1q01q51q61q81q91qa1qb1qd1qe1qg1qh1qi1qj1qk1ql1qm1qn1qo1qp1qq1qr1qs1qt1qu1qv1qw1qx1qy1qz1r01r11r21r31r41r51r61r71r81r91ra1rb1rc1rd1re1rf1rk1sn1so1sp1sq1sr1ss1st1su1sv1sw1sx1sy1sz1t01t11t21t31t41t51tw1tx1ty1tz1u61u81ub1uc1ud1ue1uf1ug1uh1ui1uj1uk1ul1um1un1uo1up1uq1ur1us1ut1uu1uv1uw1ux1uy1uz1v01v11v21v31v41v51v61v71v81v91va1ve1vk1wn1wo1wp1wq1wr1ws1wt1wu1wv1ww1wx1wy1wz1x01x11x21x31x41x51y01y11y21y31yd1ye1yf1yg1yh1yi1yj1yk1yl1ym1yn1yo1yp1yq1yr1ys1yt1yu1yv1yw1yx1yy1yz1z01z11z21z31z41z51z61z71z81z91za1zb1zf1zi1zj20p20q20r20s20t20u20v20w20x20y20z21021121221321421x21y21z22022122222322e22f22g22h22i22j22k22l22m22n22o22p22q22r22s22t22u22v22w22x22y22z23023123223323423523623723823923a23b23h24p24r24s24t24u24v24w24x24y24z25025125225w25x25y25z26026126226326426526626826926a26c26e26f26g26h26i26j26k26l26m26n26o26p26q26r26s26t26u26v26w26x26y26z27027127227327427527627727827927a27b27c28q28r28s28t28u28v28w28x29329w29x29y29z2a02a12a22a32a42a52a62a72a82a92aa2ab2ac2ad2ae2af2ag2ah2ai2ak2al2am2an2ao2ap2aq2ar2as2at2au2av2aw2ax2ay2az2b02b12b22b32b42b52b62b72b82b92ba2bb2bc2cs2ct2cu2cv2cw2d32du2dv2dw2dx2dy2dz2e02e12e22e32e42e52e62e72e82e92ea2eb2ec2ed2ef2eg2eh2ei2ej2em2en2eo2ep2eq2er2es2et2eu2ev2ew2ex2ey2ez2f02f12f22f32f42f52f62f72f82f92fa2fb2gt2gu2gv2gw2hu2hv2hw2hx2hy2hz2i02i12i22i32i42i52i62i72i82i92ia2ib2ic2id2if2ig2ih2ii2ij2ik2il2im2ir2is2it2iu2iv2iw2ix2iy2iz2j02j12j22j32j42j52j62j72j82j92ja2jc2ku2kv2kw2l02lt2lu2lv2lw2lx2ly2lz2m02m12m22m32m42m52m62m72m82m92ma2mb2mc2md2me2mg2mh2mi2mj2mk2ml2mm2mn2ms2mt2mu2mv2mw2mx2my2n12n22n32n42n52n62ou2ov2ow2ox2oz2p02p72p82pu2pv2pw2px2py2pz2q02q12q22q32q42q52q62q72q82q92qa2qb2qc2qd2qe2qg2qh2qi2qj2qk2ql2qm2qt2qu2qv2qw2qx2r22r32r42r52r72sx2sy2sz2t02tt2tu2tv2tw2tx2ty2tz2u02u12u22u32u42u52u62u72u82u92ua2ub2uc2ud2ue2uf2uh2ui2uj2uk2ut2uu2uv2uw2v32v42v52v62vc2x02x12x22xt2xu2xv2xw2xx2xy2xz2y02y12y22y32y42y52y62y72y82y92ya2yb2yc2yd2ye2yf2yg2yh2yi2yu2yv2z32z42z52z62z72zc2zd31631831u31v31w31x31y31z32032132232332432532632732832932a32b32c32d32e32f32g32j32u32v33333533635335535635735835935a35b35v35w35x35y35z36036136236336436536636736836936a36b36c36d36e36f36g36h36i36j37337e39539639739839939a39b39c39w39x39y39z3a03a23a33a43a53a63a73a83a93aa3ab3ac3ad3ae3af3ag3ah3ai3aj3aw3b43d53d63d73d83d93da3db3dc3dd3de3df3e43e53e63e73e83e93ea3eb3ec3ed3ee3ef3eg3eh3ei3f33f43f93fa3h43h53h63h73h83h93ha3hb3hc3hd3he3hf3i43i53i63i73i83i93ia3ib3ic3id3ie3if3ig3ih3j43j53j83j93ja3l43l53l63l73l83l93la3lb3lc3ld3le3lf3lg3lh3m43m53m63m73m83m93ma3mb3mc3md3me3mf3mg3n43n53n83n93na3nc3ng3nh3p43p53p63p73p83p93pa3pb3pc3pd3pe3pf3pg3ph3pi3pj3pk3q43q53q63q73q83q93qa3qb3qc3qd3qe3qf3r53rc3ri3rj3rk3rl3t43t53t63t73t83t93ta3tb3tc3td3te3tf3tg3th3ti3tj3tk3tl3u53u63u73u83u93ua3ub3uc3ud3ue3uf3v63vj3vk3vl3vm3x43x53x63x73x83x93xa3xb3xc3xd3xe3xf3xg3xh3xi3xj3xk3xl3y53y63y73y83y93ya3yb3yc3yd3ye3yf3zb3zc3ze3zk41541641741841941a41b41c41d41e41f41g41h41i41j41k42542642742842942a42b42c42d42e42f45545645745845945a45b45c45d45e45f45g45h45i45j46546646746846946a46b46c46d46e46f46j47g47h49749849949a49b49c49d49e49f49g49h49i49j4a54a64a74a84a94aa4ab4ac4ad4ae4af4ai4aj4bd4be4bf4bg4bh4bi4bl4d84d94da4db4dc4dd4de4df4dg4dh4di4dj4e54e64e74e84e94ea4eb4ec4ed4ei4ej4fd4fe4ff4fg4fh4fi4fj4fk4fl4fm4h84h94ha4hb4hc4hd4he4hf4hg4hh4hi4hj4i54i64i74i84i94ia4ib4ic4id4ih4ii4ja4jb4jc4jd4je4jf4jg4jh4ji4jj4jk4jl4jm4jn4l84l94la4lb4lc4ld4le4lf4lg4lh4m64m74m84m94ma4mb4mc4md4mh4mi4n94na4nb4nc4nd4ne4nf4ng4nh4ni4nj4nk4nl4nm4nn4p84p94pa4pb4pc4pd4pe4pf4pg4q64q74q84q94qa4qb4qc4r94ra4rb4rc4rd4re4rf4rg4rh4ri4rj4rk4rl4rm4rn4ro4t74t84t94ta4tb4tc4td4te4tf4u74u84u94ua4ub4uc4va4vb4vc4vd4ve4vf4vg4vh4vi4vj4vk4vl4vm4vn4vo4x74x84x94xa4xb4xc4xd4xe4xf4y74y84y94ya4yb4za4zb4zc4zd4ze4zf4zg4zh4zi4zj4zk4zl4zm4zn4zo51751851951a51b51c51d51e52752852953a53b53c53d53i53j53k53l53m53n53o55755855955a55b55c57k57l57m57n59759859959a59b5bm5by5d65d75d85d95fm5fx5h75h85h95jw5l65l75l85nv5p65p75p85t65t75tc5x75x8';
    var MARKETS = [[40.71, -74.0], [37.77, -122.42], [51.5, -0.12], [50.11, 8.68], [-33.87, 151.21], [35.68, 139.69], [1.35, 103.82]];
    function vec(lat, lon) {
      var p = lat * Math.PI / 180, l = lon * Math.PI / 180;
      return [Math.cos(p) * Math.sin(l), Math.sin(p), Math.cos(p) * Math.cos(l)];
    }
    function pairs(attr) {
      return (hero.getAttribute(attr) || '').split(';').map(function (s) { return s.split(',').map(parseFloat); })
        .filter(function (p) { return p.length === 2 && !isNaN(p[0]) && !isNaN(p[1]); });
    }
    function globe(canvas) {
      var ctx = canvas.getContext('2d'), size = R.fit(canvas), slide = canvas.closest('[data-slide]');
      var pts = [];
      for (var i = 0; i < DOTS.length; i += 3) {
        var c = parseInt(DOTS.substr(i, 3), 36);
        pts.push(vec(80 - (Math.floor(c / 144) + 0.5) * 2.5, -180 + (c % 144 + 0.5) * 2.5));
      }
      var homeLL = pairs('data-home')[0];
      var home = homeLL ? vec(homeLL[0], homeLL[1]) : null;
      var targets = pairs('data-arcs');
      if (home && !targets.length) targets = MARKETS;
      var arcs = home ? targets.map(function (d, k) {
        var b = vec(d[0], d[1]);
        var ang = Math.acos(Math.max(-1, Math.min(1, home[0] * b[0] + home[1] * b[1] + home[2] * b[2])));
        var seg = [];
        if (ang < 0.01) return null;
        for (var s = 0; s <= 40; s++) {
          var f = s / 40, a = Math.sin((1 - f) * ang) / Math.sin(ang), cc = Math.sin(f * ang) / Math.sin(ang);
          var lift = 1 + 0.22 * Math.sin(Math.PI * f) * (ang / Math.PI + 0.35);
          seg.push([(a * home[0] + cc * b[0]) * lift, (a * home[1] + cc * b[1]) * lift, (a * home[2] + cc * b[2]) * lift]);
        }
        return { pts: seg, end: b, off: k / targets.length };
      }).filter(Boolean) : [];
      var yaw = (homeLL ? -homeLL[1] : -100) * Math.PI / 180 - 0.35, tilt = 0.32, spin = 0.00006, drag = null, last = null;
      function project(v, Rr, cx, cy) {
        var cyw = Math.cos(yaw), syw = Math.sin(yaw);
        var x = v[0] * cyw + v[2] * syw, z = -v[0] * syw + v[2] * cyw, y = v[1];
        var ct = Math.cos(tilt), st = Math.sin(tilt);
        return [cx + x * Rr, cy - (y * ct - z * st) * Rr, y * st + z * ct];
      }
      function draw(ts) {
        if (slide && !slide.classList.contains('is-active') && !RM) { last = ts; return; }
        if (last !== null && !drag && !RM) yaw += (ts - last) * spin;
        last = ts;
        var w = size.w, h = size.h, Rr = Math.min(w, h) * 0.43, cx = w / 2, cy = h / 2;
        ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
        ctx.clearRect(0, 0, w, h);
        var g = ctx.createRadialGradient(cx - Rr * 0.35, cy - Rr * 0.4, Rr * 0.1, cx, cy, Rr);
        g.addColorStop(0, '#fff'); g.addColorStop(0.75, '#fff'); g.addColorStop(1, '#f2ece7');
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(cx, cy, Rr, 0, TAU); ctx.fill();
        ctx.fillStyle = accent;
        for (var i = 0; i < pts.length; i++) {
          var p = project(pts[i], Rr, cx, cy);
          if (p[2] <= 0.02) continue;
          ctx.globalAlpha = 0.35 + 0.65 * p[2];
          var r = 0.7 + 1.35 * p[2] * (Rr / 220);
          ctx.fillRect(p[0] - r, p[1] - r, r * 2, r * 2);
        }
        arcs.forEach(function (arc) {
          ctx.strokeStyle = primary; ctx.globalAlpha = 0.55; ctx.lineWidth = 1.4;
          ctx.beginPath();
          var pen = false, proj = arc.pts.map(function (v) {
            var p = project(v, Rr, cx, cy);
            p.push(p[2] > 0 || Math.pow(p[0] - cx, 2) + Math.pow(p[1] - cy, 2) > Rr * Rr);
            if (p[3]) { if (pen) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]); pen = true; } else pen = false;
            return p;
          });
          ctx.stroke();
          var q = proj[Math.round((RM ? 0.6 : (ts * 0.00018 + arc.off) % 1) * (proj.length - 1))];
          if (q[3]) { ctx.globalAlpha = 1; ctx.fillStyle = primary; ctx.beginPath(); ctx.arc(q[0], q[1], 3.2, 0, TAU); ctx.fill(); }
          var e = project(arc.end, Rr, cx, cy);
          if (e[2] > 0) { ctx.globalAlpha = 1; ctx.fillStyle = '#fff'; ctx.strokeStyle = primary; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(e[0], e[1], 4, 0, TAU); ctx.fill(); ctx.stroke(); }
        });
        if (home) {
          var hp = project(home, Rr, cx, cy);
          if (hp[2] > 0) {
            var pulse = RM ? 0.5 : (ts * 0.0008) % 1;
            ctx.globalAlpha = 1 - pulse; ctx.strokeStyle = accent; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(hp[0], hp[1], 6 + pulse * 18, 0, TAU); ctx.stroke();
            ctx.globalAlpha = 1; ctx.fillStyle = accent; ctx.beginPath(); ctx.arc(hp[0], hp[1], 6, 0, TAU); ctx.fill();
          }
        }
        ctx.globalAlpha = 1;
      }
      var l = R.loop(canvas, draw);
      canvas.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, yaw: yaw }; canvas.setPointerCapture(e.pointerId); });
      canvas.addEventListener('pointermove', function (e) { if (!drag) return; yaw = drag.yaw + (e.clientX - drag.x) * 0.008; if (RM || R.isPaused()) l.still(); });
      canvas.addEventListener('pointerup', function () { drag = null; });
      canvas.addEventListener('pointercancel', function () { drag = null; });
      window.addEventListener('resize', function () { size = R.fit(canvas); if (RM || R.isPaused()) l.still(); });
    }
    var gc = hero.querySelector('[data-globe]');
    if (gc) globe(gc);

    /* carousel */
    var stage = hero.querySelector('[data-carousel]');
    var slides = stage ? stage.querySelectorAll('[data-slide]') : [];
    var dots = stage ? stage.querySelectorAll('[data-dot]') : [];
    var MS = 6000, idx = 0, timer = 0, startedAt = 0, remaining = MS, hover = false;
    function schedule(ms) {
      clearTimeout(timer); timer = 0; remaining = ms;
      if (RM || R.isPaused() || hover) return;
      startedAt = Date.now();
      timer = setTimeout(function () { show(idx + 1); }, ms);
    }
    function hold() { if (timer) { clearTimeout(timer); timer = 0; remaining = Math.max(400, remaining - (Date.now() - startedAt)); } }
    function show(k) {
      var prev = slides[idx];
      idx = (k + slides.length) % slides.length;
      Array.prototype.forEach.call(slides, function (s, i) {
        s.classList.toggle('is-active', i === idx);
        s.classList.toggle('is-leaving', s === prev && i !== idx);
        s.setAttribute('aria-hidden', String(i !== idx));
      });
      Array.prototype.forEach.call(dots, function (d, i) { d.classList.remove('is-active'); d.setAttribute('aria-current', String(i === idx)); });
      void stage.offsetWidth;
      dots[idx].classList.add('is-active');
      if (prev && prev !== slides[idx]) setTimeout(function () { prev.classList.remove('is-leaving'); }, 900);
      schedule(MS);
    }
    if (slides.length) {
      stage.style.setProperty('--slide-ms', MS + 'ms');
      Array.prototype.forEach.call(dots, function (d, i) { d.addEventListener('click', function () { show(i); }); });
      stage.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') { hover = true; hold(); hero.classList.add('is-hold'); } });
      stage.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') { hover = false; hero.classList.remove('is-hold'); schedule(remaining); } });
      stage.addEventListener('focusin', function () { hover = true; hold(); hero.classList.add('is-hold'); });
      stage.addEventListener('focusout', function (e) { if (!stage.contains(e.relatedTarget)) { hover = false; hero.classList.remove('is-hold'); schedule(remaining); } });
      show(0);
      if (RM) hero.classList.add('is-paused');
    }

    /* the hero button drives the page-wide motion switch, so it also stops the ribbons, the globe and every other loop (WCAG 2.2.2) */
    var toggle = hero.querySelector('[data-rib-toggle]');
    if (toggle) toggle.addEventListener('click', function () { R.setPaused(!R.isPaused()); });
    document.addEventListener('bl:motion', function (e) {
      var p = !!e.detail.paused;
      hero.classList.toggle('is-paused', p || RM);
      if (toggle) {
        toggle.setAttribute('aria-pressed', String(p));
        toggle.setAttribute('aria-label', toggle.getAttribute(p ? 'data-label-play' : 'data-label-pause'));
      }
      if (p) hold(); else schedule(remaining);
    });
  });
})();
