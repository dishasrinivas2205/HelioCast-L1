/**
 * AETHER — Deep Field Solar Observatory Engine (HelioCast-L1)
 * Lenis Smooth Scroll + GSAP ScrollTrigger + Three.js 3D Sun + Dynamic Telemetry
 */

(function () {
  'use strict';

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ══════════════════════════════════════════════════════════
     1. PRELOADER COUNTDOWN
     ══════════════════════════════════════════════════════════ */
  var preloader = $('#preloader');
  var preCount = $('#preCount');
  var preStatus = $('#preStatus');
  var preArc = $('.pre-arc-fill');
  var CIRC = 2 * Math.PI * 92;

  if (preArc) {
    preArc.style.strokeDasharray = CIRC;
    preArc.style.strokeDashoffset = CIRC;
  }

  var statuses = [
    'ESTABLISHING TELEMETRY LINK',
    'SYNCHRONIZING SOLEXS & HEL1OS ARRAYS',
    'ALIGNING SUN-EARTH L1 HALO FRAME',
    'NEUPERT COUPLING VERIFIED',
    'HELIOCAST-L1 OBSERVATORY READY'
  ];

  var progress = 0;
  var preInterval = setInterval(function () {
    progress += Math.floor(Math.random() * 8) + 4;
    if (progress > 100) progress = 100;

    if (preCount) preCount.textContent = progress;
    if (preArc) preArc.style.strokeDashoffset = CIRC * (1 - progress / 100);

    var sIdx = Math.min(Math.floor((progress / 100) * statuses.length), statuses.length - 1);
    if (preStatus) preStatus.textContent = statuses[sIdx];

    if (progress >= 100) {
      clearInterval(preInterval);
      setTimeout(function () {
        if (preloader) {
          preloader.style.transition = 'opacity 0.8s cubic-bezier(0.22, 0.61, 0.36, 1), transform 0.8s ease';
          preloader.style.opacity = '0';
          preloader.style.transform = 'translateY(-20px)';
          setTimeout(function () { preloader.style.display = 'none'; }, 800);
        }
        document.body.classList.remove('is-loading');
      }, 500);
    }
  }, 45);

  /* ══════════════════════════════════════════════════════════
     2. LENIS SMOOTH SCROLL & HUD RAIL TRACKER
     ══════════════════════════════════════════════════════════ */
  var lenis = null;
  if (typeof Lenis !== 'undefined') {
    lenis = new Lenis({
      duration: 1.2,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      smoothWheel: true,
      touchMultiplier: 1.5,
    });

    lenis.on('scroll', function (e) {
      updateScrollHUD();
    });

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
  } else {
    window.addEventListener('scroll', updateScrollHUD);
  }

  function updateScrollHUD() {
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var current = window.scrollY || (lenis ? lenis.scroll : 0);
    var pct = max > 0 ? Math.min(100, Math.max(0, Math.round((current / max) * 100))) : 0;

    var railFill = $('#railFill');
    var railPct = $('#railPct');
    if (railFill) railFill.style.transform = 'scaleY(' + (pct / 100) + ')';
    if (railPct) railPct.textContent = (pct < 10 ? '00' : pct < 100 ? '0' : '') + pct;

    // Update section active dots & index counter
    var acts = $$('section.act');
    var scrollMid = current + window.innerHeight * 0.35;
    acts.forEach(function (act) {
      var top = act.offsetTop;
      var height = act.offsetHeight;
      if (scrollMid >= top && scrollMid < top + height) {
        var idx = act.getAttribute('data-index');
        var hudIndex = $('#hudIndex');
        if (hudIndex && idx) hudIndex.textContent = idx;

        var dots = $$('.hud-dots a');
        dots.forEach(function (d) {
          if (d.getAttribute('href') === '#' + act.id) {
            d.classList.add('is-on');
          } else {
            d.classList.remove('is-on');
          }
        });
      }
    });

    // Fade out fixed bottom cycle info when approaching footer
    var cycleEl = $('.hud-cycle');
    if (cycleEl) {
      var nearBottom = (window.innerHeight + current) >= (document.documentElement.scrollHeight - 380);
      cycleEl.style.opacity = nearBottom ? '0' : '0.75';
      cycleEl.style.transition = 'opacity 0.4s ease';
      cycleEl.style.pointerEvents = 'none';
    }

    // Benchmark bar animations when Act 06 is in view
    var act06 = $('#act-06');
    if (act06 && current + window.innerHeight * 0.7 > act06.offsetTop) {
      $$('.cmp-cell .bar b').forEach(function (b) {
        b.style.transform = 'scaleX(1)';
      });
    }
  }

  /* ══════════════════════════════════════════════════════════
     3. UTC CLOCK TICKER
     ══════════════════════════════════════════════════════════ */
  var clockEl = $('#hudClock');
  var footClockEl = $('#footClock');
  var footDateEl = $('#footDate');

  function updateClock() {
    var now = new Date();
    var h = String(now.getUTCHours()).padStart(2, '0');
    var m = String(now.getUTCMinutes()).padStart(2, '0');
    var s = String(now.getUTCSeconds()).padStart(2, '0');
    var timeStr = h + ':' + m + ':' + s;
    if (clockEl) clockEl.textContent = timeStr + ' UTC';
    if (footClockEl) footClockEl.textContent = timeStr;
    if (footDateEl) footDateEl.textContent = now.getUTCFullYear() + '-' + String(now.getUTCMonth() + 1).padStart(2, '0') + '-' + String(now.getUTCDate()).padStart(2, '0');
  }
  setInterval(updateClock, 1000);
  updateClock();

  /* Scroll hint retirement after user begins scrolling */
  var hint = $('#hint');
  if (hint) {
    var retireHint = function () {
      if (typeof gsap !== 'undefined') {
        gsap.to(hint, {
          opacity: 0,
          y: 16,
          duration: 0.6,
          ease: 'power2.out',
          onComplete: function () {
            hint.style.display = 'none';
          }
        });
      } else {
        hint.style.opacity = '0';
        setTimeout(function () { hint.style.display = 'none'; }, 600);
      }
      window.removeEventListener('wheel', retireHint);
      window.removeEventListener('touchmove', retireHint);
      window.removeEventListener('scroll', onScrollOnce);
    };
    var onScrollOnce = function () { if (window.scrollY > 25) retireHint(); };
    window.addEventListener('wheel', retireHint, { passive: true, once: true });
    window.addEventListener('touchmove', retireHint, { passive: true, once: true });
    window.addEventListener('scroll', onScrollOnce, { passive: true });
  }

  /* ══════════════════════════════════════════════════════════
     4. CUSTOM MAGNETIC TRAILING CURSOR
     ══════════════════════════════════════════════════════════ */
  var cursor = $('#cursor');
  var dot = $('.cursor-dot');
  var ring = $('.cursor-ring');
  var curLabel = $('.cursor-label');

  if (cursor && dot && ring) {
    var mx = -100, my = -100;
    var rx = -100, ry = -100;

    window.addEventListener('mousemove', function (e) {
      mx = e.clientX;
      my = e.clientY;
      cursor.style.opacity = '1';
    });

    function renderCursor() {
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;

      dot.style.transform = 'translate(' + mx + 'px, ' + my + 'px)';
      ring.style.transform = 'translate(' + rx + 'px, ' + ry + 'px)';
      requestAnimationFrame(renderCursor);
    }
    requestAnimationFrame(renderCursor);

    // Hover triggers
    $$('[data-cursor]').forEach(function (el) {
      el.addEventListener('mouseenter', function () {
        var label = el.getAttribute('data-cursor');
        ring.classList.add('is-big');
        if (curLabel && label) curLabel.textContent = label;
      });
      el.addEventListener('mouseleave', function () {
        ring.classList.remove('is-big');
        if (curLabel) curLabel.textContent = '';
      });
    });
  }

  /* ══════════════════════════════════════════════════════════
     5. BACKGROUND STARFIELD CANVAS
     ══════════════════════════════════════════════════════════ */
  var starCanvas = $('#stars');
  if (starCanvas) {
    var ctx = starCanvas.getContext('2d');
    var stars = [];
    var count = 180;

    function resizeStars() {
      starCanvas.width = window.innerWidth;
      starCanvas.height = window.innerHeight;
      stars = [];
      for (var i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * starCanvas.width,
          y: Math.random() * starCanvas.height,
          r: Math.random() * 1.4 + 0.3,
          alpha: Math.random() * 0.8 + 0.2,
          speed: Math.random() * 0.015 + 0.005,
          color: Math.random() > 0.85 ? '#7FFFD4' : Math.random() > 0.7 ? '#FF8A3D' : '#ffffff'
        });
      }
    }
    window.addEventListener('resize', resizeStars);
    resizeStars();

    function animateStars() {
      ctx.clearRect(0, 0, starCanvas.width, starCanvas.height);
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        s.alpha += Math.sin(Date.now() * s.speed) * 0.01;
        s.alpha = Math.max(0.1, Math.min(0.9, s.alpha));

        ctx.fillStyle = s.color;
        ctx.globalAlpha = s.alpha;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1.0;
      requestAnimationFrame(animateStars);
    }
    requestAnimationFrame(animateStars);
  }

  /* ══════════════════════════════════════════════════════════
     6. THREE.JS 3D SUN CANVAS WITH PASSBANDS
     ══════════════════════════════════════════════════════════ */
  var canvas = $('#sunCanvas');
  var sunMesh = null;
  var coronaMesh = null;
  var sunUniforms = null;
  var rotSpeed = 0.6;

  if (canvas && typeof THREE !== 'undefined') {
    var width = canvas.parentElement.clientWidth;
    var height = canvas.parentElement.clientHeight;

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.z = 3.2;

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Custom Simplex-like Procedural Solar Shader
    sunUniforms = {
      uTime: { value: 0 },
      uColor1: { value: new THREE.Color(0xff8a3d) }, // Deep plasma amber
      uColor2: { value: new THREE.Color(0xffb703) }, // Hot solar gold
      uColor3: { value: new THREE.Color(0xfff3b0) }, // Core white-gold
      uMode: { value: 0.0 }, // 0: COMPOSITE, 1: SOFT_XRAY, 2: HARD_XRAY, 3: MAGNETOGRAM
    };

    var vertShader = [
      'varying vec2 vUv;',
      'varying vec3 vNormal;',
      'varying vec3 vPosition;',
      'void main() {',
      '  vUv = uv;',
      '  vNormal = normalize(normalMatrix * normal);',
      '  vPosition = position;',
      '  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);',
      '}'
    ].join('\n');

    var fragShader = [
      'uniform float uTime;',
      'uniform vec3 uColor1;',
      'uniform vec3 uColor2;',
      'uniform vec3 uColor3;',
      'uniform float uMode;',
      'varying vec2 vUv;',
      'varying vec3 vNormal;',
      'varying vec3 vPosition;',
      '',
      'float noise(vec3 p) {',
      '  return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);',
      '}',
      '',
      'void main() {',
      '  vec3 p = vPosition * 4.0;',
      '  float t = uTime * 0.4;',
      '  float n = sin(p.x + t) * sin(p.y - t * 0.5) * sin(p.z + t * 0.8);',
      '  n += 0.5 * sin(p.x * 2.0 - t) * sin(p.y * 2.0 + t);',
      '  n = n * 0.5 + 0.5;',
      '',
      '  // Active Region 13664 sunspot cluster',
      '  float spotDist = distance(vUv, vec2(0.42, 0.48));',
      '  float spot = smoothstep(0.09, 0.02, spotDist) * 0.85;',
      '',
      '  vec3 color = mix(uColor1, uColor2, n);',
      '  color = mix(color, uColor3, pow(n, 2.5));',
      '  color = mix(color, vec3(0.03, 0.01, 0.0), spot);',
      '',
      '  // Atmospheric limb darkening',
      '  float limb = clamp(dot(vNormal, vec3(0.0, 0.0, 1.0)), 0.0, 1.0);',
      '  color *= (0.35 + 0.65 * pow(limb, 0.6));',
      '',
      '  // Passband modifications',
      '  if (uMode == 1.0) { // SOFT X-RAY (SoLEXS)',
      '    color = vec3(color.r * 1.1, color.g * 0.6, color.b * 0.1);',
      '  } else if (uMode == 2.0) { // HARD X-RAY (HEL1OS)',
      '    color = vec3(color.r * 0.2, color.g * 0.8, color.b * 1.2);',
      '  } else if (uMode == 3.0) { // MAGNETOGRAM',
      '    color = vec3(mix(0.1, 0.9, n));',
      '  }',
      '',
      '  gl_FragColor = vec4(color, 1.0);',
      '}'
    ].join('\n');

    var sunGeo = new THREE.SphereGeometry(1.0, 64, 64);
    var sunMat = new THREE.ShaderMaterial({
      vertexShader: vertShader,
      fragmentShader: fragShader,
      uniforms: sunUniforms
    });

    sunMesh = new THREE.Mesh(sunGeo, sunMat);
    scene.add(sunMesh);

    // Glowing Coronal Halo
    var coronaGeo = new THREE.SphereGeometry(1.18, 48, 48);
    var coronaMat = new THREE.ShaderMaterial({
      vertexShader: [
        'varying vec3 vNormal;',
        'void main() {',
        '  vNormal = normalize(normalMatrix * normal);',
        '  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);',
        '}'
      ].join('\n'),
      fragmentShader: [
        'uniform vec3 uGlowColor;',
        'varying vec3 vNormal;',
        'void main() {',
        '  float intensity = pow(0.68 - dot(vNormal, vec3(0, 0, 1.0)), 2.2);',
        '  gl_FragColor = vec4(uGlowColor, intensity * 0.85);',
        '}'
      ].join('\n'),
      uniforms: {
        uGlowColor: { value: new THREE.Color(0xff8a3d) }
      },
      side: THREE.BackSide,
      blending: THREE.AdditiveBlending,
      transparent: true
    });
    coronaMesh = new THREE.Mesh(coronaGeo, coronaMat);
    scene.add(coronaMesh);

    // Magnetic loops (arcades)
    var loopsGroup = new THREE.Group();
    for (var l = 0; l < 5; l++) {
      var loopCurve = new THREE.EllipseCurve(0, 0, 0.25 + l * 0.04, 0.18 + l * 0.03, 0, Math.PI, false, 0);
      var points = loopCurve.getPoints(30);
      var loopGeo = new THREE.BufferGeometry().setFromPoints(points);
      var loopMat = new THREE.LineBasicMaterial({ color: 0x7fffd4, transparent: true, opacity: 0.65 });
      var loopLine = new THREE.Line(loopGeo, loopMat);
      loopLine.position.set(0.72, 0.18, 0.5);
      loopLine.rotation.set(0.5, l * 0.2, -0.4);
      loopsGroup.add(loopLine);
    }
    scene.add(loopsGroup);

    function animateSun() {
      requestAnimationFrame(animateSun);
      if (sunMesh) {
        sunMesh.rotation.y += 0.0025 * rotSpeed;
        sunUniforms.uTime.value += 0.018 * rotSpeed;
      }
      if (loopsGroup) {
        loopsGroup.rotation.y += 0.0025 * rotSpeed;
      }
      renderer.render(scene, camera);
    }
    animateSun();

    window.addEventListener('resize', function () {
      var w = canvas.parentElement.clientWidth;
      var h = canvas.parentElement.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });

    var speedInput = $('#speedSlider');
    if (speedInput) {
      speedInput.addEventListener('input', function (e) {
        rotSpeed = parseFloat(e.target.value);
      });
    }
  }

  window.setPassband = function (band) {
    if (!sunUniforms) return;
    var btns = $$('.stage-controls .pill');
    btns.forEach(function (b) { b.classList.remove('pill--active'); });

    if (band === 'COMPOSITE') {
      sunUniforms.uMode.value = 0.0;
      sunUniforms.uColor1.value.setHex(0xff8a3d);
      sunUniforms.uColor2.value.setHex(0xffb703);
      $('#btnBandComp').classList.add('pill--active');
    } else if (band === 'SOFT_XRAY') {
      sunUniforms.uMode.value = 1.0;
      sunUniforms.uColor1.value.setHex(0xffaa00);
      sunUniforms.uColor2.value.setHex(0xff5500);
      $('#btnBandSXR').classList.add('pill--active');
    } else if (band === 'HARD_XRAY') {
      sunUniforms.uMode.value = 2.0;
      sunUniforms.uColor1.value.setHex(0x00c8e0);
      sunUniforms.uColor2.value.setHex(0x7fffd4);
      $('#btnBandHXR').classList.add('pill--active');
    } else if (band === 'MAGNETOGRAM') {
      sunUniforms.uMode.value = 3.0;
      sunUniforms.uColor1.value.setHex(0x111111);
      sunUniforms.uColor2.value.setHex(0xeeeeee);
      $('#btnBandMag').classList.add('pill--active');
    }
  };

  /* ══════════════════════════════════════════════════════════
     7. FLIGHT OPS SIMULATION PLAYBACK ENGINE
     ══════════════════════════════════════════════════════════ */
  var simPlaying = false;
  var simStep = 0;
  var simTimer = null;
  var maxSteps = 2160;

  window.togglePlayback = function () {
    simPlaying = !simPlaying;
    var label = $('#playLabel');
    if (simPlaying) {
      if (label) label.textContent = 'PAUSE SIMULATION';
      simTimer = setInterval(function () {
        simStep += 3;
        if (simStep > maxSteps) simStep = 0;
        updateSimState(simStep);
      }, 50);
    } else {
      if (label) label.textContent = 'RESUME SIMULATION';
      clearInterval(simTimer);
    }
  };

  window.stepForward = function () {
    simStep = Math.min(maxSteps, simStep + 10);
    updateSimState(simStep);
  };

  window.resetSim = function () {
    simStep = 0;
    if (simPlaying) togglePlayback();
    updateSimState(0);
  };

  window.onScrubChange = function (val) {
    simStep = parseInt(val, 10);
    updateSimState(simStep);
  };

  function updateSimState(step) {
    var scrubber = $('#simScrubber');
    if (scrubber) scrubber.value = step;

    // Time calculations
    var secs = step * 10;
    var hh = String(Math.floor(secs / 3600)).padStart(2, '0');
    var mm = String(Math.floor((secs % 3600) / 60)).padStart(2, '0');
    var ss = String(secs % 60).padStart(2, '0');
    var timeStr = 'T+' + hh + ':' + mm + ':' + ss;

    var scrubText = $('#scrubValText');
    if (scrubText) scrubText.textContent = 'PROGRESS: ' + timeStr;

    var timeReadout = $('#simTimeReadout');
    if (timeReadout) timeReadout.textContent = hh + ':' + mm + ':' + ss;

    // Realistic flare profile simulation
    // Event 1 occurs near step 990 (T+02:45:00, C4.8 flare)
    var distToPeak1 = Math.abs(step - 990);
    // Event 2 occurs near step 1810 (T+05:01:40, M2.5 flare)
    var distToPeak2 = Math.abs(step - 1810);

    var prob = 4.2;
    var alertBadge = $('#simAlertBadge');
    var probText = $('#simProbText');
    var eventName = $('#simEventName');
    var subtext = $('#simStatusSubtext');
    var leadReadout = $('#simLeadReadout');

    if (distToPeak1 < 170) { // C-Class Precursor & Peak
      var leadMin = Math.max(0, (170 - (170 - (990 - step))) * 10 / 60).toFixed(1);
      prob = Math.min(94.2, Math.max(12.0, 95.0 - distToPeak1 * 0.5));
      if (eventName) eventName.textContent = 'Event 1: C4.8 Solar Flare Window';
      if (probText) {
        probText.textContent = 'P(C-Class) = ' + prob.toFixed(1) + '%';
        probText.style.color = '#ffb703';
      }
      if (alertBadge) {
        alertBadge.textContent = step < 990 ? 'PRECURSOR WATCH' : 'FLARE PEAK';
        alertBadge.style.color = '#ffb703';
      }
      if (leadReadout) leadReadout.innerHTML = (step < 990 ? ((990 - step) * 10 / 60).toFixed(1) : '0.0') + ' <em>min</em>';
      if (subtext) subtext.textContent = 'SoLEXS Soft X-Ray thermal flux rising. Neupert coupling derivative confirmed.';
    } else if (distToPeak2 < 200) { // M-Class Precursor & Peak
      prob = Math.min(98.8, Math.max(18.0, 99.0 - distToPeak2 * 0.4));
      if (eventName) eventName.textContent = 'Event 2: M2.5 Precursor In Progress';
      if (probText) {
        probText.textContent = 'P(M/X-Class) = ' + prob.toFixed(1) + '%';
        probText.style.color = '#ff8a3d';
      }
      if (alertBadge) {
        alertBadge.textContent = step < 1810 ? '🚨 PRECURSOR WARNING' : 'M2.5 FLARE PEAK';
        alertBadge.style.color = '#ff8a3d';
      }
      if (leadReadout) leadReadout.innerHTML = (step < 1810 ? ((1810 - step) * 10 / 60).toFixed(1) : '0.0') + ' <em>min</em>';
      if (subtext) subtext.textContent = 'HEL1OS non-thermal electron burst active. Significant coronal mass ejection risk.';
    } else {
      if (eventName) eventName.textContent = 'Nominal Solar Background';
      if (probText) {
        probText.textContent = 'P(Flare) = 4.2%';
        probText.style.color = 'var(--mint)';
      }
      if (alertBadge) {
        alertBadge.textContent = 'NOMINAL';
        alertBadge.style.color = 'var(--mint)';
      }
      if (leadReadout) leadReadout.innerHTML = '28.4 <em>min</em>';
      if (subtext) subtext.textContent = 'Quiet-Sun emission measure stable. No magnetic reconnection triggers detected.';
    }
  }

  /* ══════════════════════════════════════════════════════════
     8. DUAL-BAND LIGHT CURVE CANVAS GRAPH
     ══════════════════════════════════════════════════════════ */
  var lcCanvas = $('#lightCurveCanvas');
  if (lcCanvas) {
    var lcCtx = lcCanvas.getContext('2d');
    function renderLightCurves() {
      var w = lcCanvas.parentElement.clientWidth - 48;
      var h = 320;
      lcCanvas.width = w;
      lcCanvas.height = h;

      lcCtx.clearRect(0, 0, w, h);

      // Grid Lines
      lcCtx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
      lcCtx.lineWidth = 1;
      for (var y = 40; y < h - 20; y += 50) {
        lcCtx.beginPath();
        lcCtx.moveTo(40, y);
        lcCtx.lineTo(w, y);
        lcCtx.stroke();
      }

      var points = 120;
      var sxrPts = [];
      var hxrPts = [];
      var neupertPts = [];

      // Generate realistic curves with 2 events
      for (var i = 0; i < points; i++) {
        var x = 40 + (i / points) * (w - 50);

        // Event 1 peak at 45, Event 2 peak at 85
        var e1 = Math.exp(-Math.pow(i - 45, 2) / 40);
        var e2 = Math.exp(-Math.pow(i - 85, 2) / 60);

        // SoLEXS (gradual decay)
        var decay1 = (i > 45) ? Math.exp(-(i - 45) / 25) * 0.8 : 0;
        var decay2 = (i > 85) ? Math.exp(-(i - 85) / 35) * 0.9 : 0;
        var sxrY = (h - 40) - (e1 * 130 + decay1 * 90 + e2 * 190 + decay2 * 140 + 20);

        // HEL1OS (impulsive narrow bursts)
        var hxrY = (h - 40) - (e1 * 150 + e2 * 230 + 10);

        // Neupert derivative dF/dt (peaks at same time as HXR)
        var neupertY = (h - 40) - (e1 * 140 + e2 * 215 + 15);

        sxrPts.push({ x: x, y: sxrY });
        hxrPts.push({ x: x, y: hxrY });
        neupertPts.push({ x: x, y: neupertY });
      }

      // Draw SoLEXS (Cyan)
      lcCtx.strokeStyle = '#00f0ff';
      lcCtx.lineWidth = 2.2;
      lcCtx.beginPath();
      for (var j = 0; j < sxrPts.length; j++) {
        if (j === 0) lcCtx.moveTo(sxrPts[j].x, sxrPts[j].y);
        else lcCtx.lineTo(sxrPts[j].x, sxrPts[j].y);
      }
      lcCtx.stroke();

      // Draw HEL1OS (Amber)
      lcCtx.strokeStyle = '#ff8a3d';
      lcCtx.lineWidth = 2.0;
      lcCtx.beginPath();
      for (var k = 0; k < hxrPts.length; k++) {
        if (k === 0) lcCtx.moveTo(hxrPts[k].x, hxrPts[k].y);
        else lcCtx.lineTo(hxrPts[k].x, hxrPts[k].y);
      }
      lcCtx.stroke();

      // Draw Neupert Derivative (Dotted Mint)
      lcCtx.strokeStyle = '#7fffd4';
      lcCtx.lineWidth = 1.8;
      lcCtx.setLineDash([4, 4]);
      lcCtx.beginPath();
      for (var m = 0; m < neupertPts.length; m++) {
        if (m === 0) lcCtx.moveTo(neupertPts[m].x, neupertPts[m].y);
        else lcCtx.lineTo(neupertPts[m].x, neupertPts[m].y);
      }
      lcCtx.stroke();
      lcCtx.setLineDash([]);
    }
    renderLightCurves();
    window.addEventListener('resize', renderLightCurves);
  }

  /* ══════════════════════════════════════════════════════════
     9. MASTER FLARE CATALOGUE DYNAMIC SEARCH & FILTER
     ══════════════════════════════════════════════════════════ */
  var CATALOG_EVENTS = [
    { id: 'FL-20240510-01', start: '02:18:20 UTC', peak: '02:46:40 UTC', class: 'C4.8', flux: '4.82e-6', neupert: true, ar: '13664' },
    { id: 'FL-20240510-02', start: '04:36:10 UTC', peak: '05:04:30 UTC', class: 'M2.5', flux: '2.54e-5', neupert: true, ar: '13664' },
    { id: 'FL-20240511-01', start: '08:12:00 UTC', peak: '08:38:10 UTC', class: 'M1.2', flux: '1.20e-5', neupert: true, ar: '13663' },
    { id: 'FL-20240511-02', start: '14:20:40 UTC', peak: '14:52:00 UTC', class: 'X1.1', flux: '1.14e-4', neupert: true, ar: '13664' },
    { id: 'FL-20240512-01', start: '18:05:10 UTC', peak: '18:22:40 UTC', class: 'C2.1', flux: '2.10e-6', neupert: false, ar: '13668' },
    { id: 'FL-20240513-01', start: '22:40:00 UTC', peak: '23:14:20 UTC', class: 'X2.8', flux: '2.85e-4', neupert: true, ar: '13664' }
  ];

  var activeFilter = 'ALL';

  window.setCatalogFilter = function (filter, btn) {
    activeFilter = filter;
    $$('.fb-chips .chip').forEach(function (c) { c.classList.remove('is-on'); });
    if (btn) btn.classList.add('is-on');
    renderCatalog();
  };

  window.filterCatalog = function () {
    renderCatalog();
  };

  function renderCatalog() {
    var table = $('#catalogTable');
    if (!table) return;

    var searchVal = ($('#catalogSearch') ? $('#catalogSearch').value.toLowerCase() : '');
    var filtered = CATALOG_EVENTS.filter(function (e) {
      var matchesFilter = (activeFilter === 'ALL') ||
                          (activeFilter === 'X' && e.class.startsWith('X')) ||
                          (activeFilter === 'M' && e.class.startsWith('M')) ||
                          (activeFilter === 'C' && e.class.startsWith('C')) ||
                          (activeFilter === 'NEUPERT' && e.neupert);
      var matchesSearch = e.id.toLowerCase().includes(searchVal) ||
                          e.class.toLowerCase().includes(searchVal) ||
                          e.ar.toLowerCase().includes(searchVal);
      return matchesFilter && matchesSearch;
    });

    var countEl = $('#catalogCount');
    if (countEl) countEl.textContent = filtered.length;

    // Remove existing rows except header
    var rows = $$('#catalogTable .cmp-row:not(.cmp-row--head)');
    rows.forEach(function (r) { r.remove(); });

    filtered.forEach(function (item) {
      var row = document.createElement('div');
      row.className = 'cmp-row';
      row.innerHTML = [
        '<span class="cmp-name"><b>&bull;</b> ' + item.id + ' <span style="font-size:0.75em; color:var(--ink-faint);">(AR ' + item.ar + ')</span></span>',
        '<span class="cmp-cell" style="font-size:0.95rem;">' + item.start + ' &rarr; ' + item.peak + '</span>',
        '<span class="cmp-cell" style="font-weight:600; color:' + (item.class.startsWith('X') ? 'var(--a-rust)' : item.class.startsWith('M') ? 'var(--a-gas)' : 'var(--mint)') + ';">' + item.class + '</span>',
        '<span class="cmp-cell">' + item.flux + ' <i>W m⁻²</i></span>',
        '<span class="cmp-cell" style="color:' + (item.neupert ? 'var(--mint)' : 'var(--ink-faint)') + ';">' + (item.neupert ? 'VERIFIED (r &ge; 0.60)' : 'UNCONFIRMED') + '</span>'
      ].join('');
      table.appendChild(row);
    });
  }
  renderCatalog();

  /* ══════════════════════════════════════════════════════════
     10. KATEX FORMULA RENDERING & SPLITTYPE
     ══════════════════════════════════════════════════════════ */
  if (typeof renderMathInElement !== 'undefined') {
    try {
      renderMathInElement(document.body, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false }
        ],
        throwOnError: false
      });
    } catch (e) {
      console.warn('KaTeX render note:', e);
    }
  }

  if (typeof SplitType !== 'undefined') {
    try {
      new SplitType('.display', { types: 'chars, words', tagName: 'span' });
    } catch (e) {
      console.warn('SplitType note:', e);
    }
  }

})();

