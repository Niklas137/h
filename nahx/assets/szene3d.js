/* NAHX Technologies – 3D-Szene im Aufmacher (WebGL, ohne Bibliothek).
   Raymarching einer Signed-Distance-Funktion: das NAHX-A als extrudierter Körper mit abgerundeten Kanten,
   prozeduraler Oberflächenstruktur, Hauptlicht, Fresnel-Kantenglühen in der Markenfarbe, Nebel, Vignette
   und Filmkorn. Reagiert sanft auf Mausposition und Scrollen. Rendert in reduzierter Auflösung, pausiert
   außerhalb des Bildes; bei prefers-reduced-motion nur ein Standbild. */
(function () {
  var c = document.getElementById('szene3d');
  if (!c) { return; }
  var gl = c.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false, powerPreference: 'low-power' });
  if (!gl) { c.remove(); return; }
  var ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 R;uniform float T;uniform vec2 M;uniform float S;uniform float K;uniform vec2 O;uniform float Z;',
    'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*noise(p);p*=2.1;a*=.5;}return v;}',
    // Dreieck-SDF (2D), Punkte im Uhrzeigersinn
    'float sdTri(vec2 p,vec2 a,vec2 b,vec2 c){vec2 e0=b-a,e1=c-b,e2=a-c;vec2 v0=p-a,v1=p-b,v2=p-c;',
    ' vec2 pq0=v0-e0*clamp(dot(v0,e0)/dot(e0,e0),0.,1.);vec2 pq1=v1-e1*clamp(dot(v1,e1)/dot(e1,e1),0.,1.);vec2 pq2=v2-e2*clamp(dot(v2,e2)/dot(e2,e2),0.,1.);',
    ' float s=sign(e0.x*e2.y-e0.y*e2.x);vec2 d=min(min(vec2(dot(pq0,pq0),s*(v0.x*e0.y-v0.y*e0.x)),vec2(dot(pq1,pq1),s*(v1.x*e1.y-v1.y*e1.x))),vec2(dot(pq2,pq2),s*(v2.x*e2.y-v2.y*e2.x)));return -sqrt(d.x)*sign(d.y);}',
    // Das A: äußeres Dreieck minus Loch plus Innendreieck (Maße der Wortmarke, normiert)
    'float sdA(vec2 p){float o=sdTri(p,vec2(0.,1.),vec2(1.03,-.5),vec2(-1.03,-.5));float h=sdTri(p,vec2(0.,.47),vec2(.63,-.5),vec2(-.63,-.5));float i=sdTri(p,vec2(0.,.05),vec2(.35,-.5),vec2(-.35,-.5));return min(max(o,-h),i);}',
    'float sdBody(vec3 q){float d2=sdA(q.xy);float dz=abs(q.z)-.22;vec2 w=vec2(d2,dz);return min(max(w.x,w.y),0.)+length(max(w,0.))-.045;}',
    'mat2 rot(float a){float s=sin(a),c=cos(a);return mat2(c,-s,s,c);}',
    'float map(vec3 p){p.xy-=O;p*=Z;p.yz*=rot(-.16+M.y*.16);p.xz*=rot(.42+M.x*.28+T*.06+S*.5);return sdBody(p)/Z;}',
    'vec3 nrm(vec3 p){vec2 e=vec2(.0015,0.);return normalize(vec3(map(p+e.xyy)-map(p-e.xyy),map(p+e.yxy)-map(p-e.yxy),map(p+e.yyx)-map(p-e.yyx)));}',
    'void main(){vec2 uv=(gl_FragCoord.xy-.5*R)/R.y;vec2 pix=gl_FragCoord.xy;',
    ' vec3 ro=vec3(0.,0.,3.6);vec3 rd=normalize(vec3(uv,-1.9));',
    ' vec3 bg=vec3(.02,.028,.02)+vec3(.03,.06,.04)*smoothstep(.9,-.2,length(uv-vec2(.2,.1)));',
    ' float t=0.,d=0.,dmin=9.;bool hit=false;for(int i=0;i<80;i++){d=map(ro+rd*t);dmin=min(dmin,d/max(t,.6));if(d<.0015){hit=true;break;}t+=d*.9;if(t>8.)break;}',
    ' vec3 col=bg;',
    ' vec3 glowc=vec3(.33,.62,.40);vec3 edgec=vec3(.70,.93,.79);',
    ' if(hit){vec3 p=ro+rd*t;vec3 n=nrm(p);vec3 L=normalize(vec3(.6,.9,.8));vec3 V=-rd;vec3 H=normalize(L+V);',
    '  float tex=fbm(p.xy*9.+vec2(T*.02));float cracks=smoothstep(.55,.62,fbm(p.xy*22.+3.));',
    '  vec3 alb=mix(vec3(.05,.09,.06),vec3(.10,.19,.12),tex)+cracks*vec3(.04,.08,.05);',
    '  float dif=max(dot(n,L),0.);float spe=pow(max(dot(n,H),0.),48.)*.6;float fre=pow(1.-max(dot(n,V),0.),3.);',
    '  float ao=clamp(map(p+n*.12)/.12,0.,1.);',
    '  col=alb*(0.18+dif*1.2)*ao+spe*edgec+fre*glowc*2.2+fre*fre*fre*edgec*1.6;',
    '  col=mix(col,bg,smoothstep(2.5,6.5,t));}',
    // Volumenglühen hinter dem Körper (Abstand entlang des Strahls nähert sich dem Körper)
    ' float g=0.;float tt=1.0;for(int i=0;i<16;i++){float dd=map(ro+rd*tt);g+=exp(-dd*7.)*.016;tt+=.22;}col+=g*glowc*(1.05+.35*sin(T*.4));',
    ' if(!hit){col+=edgec*exp(-dmin*55.)*.9+glowc*exp(-dmin*14.)*.35;}',
    ' col*=1.-.55*pow(length(uv*vec2(.8,1.)),2.2);',
    ' float grain=(hash(pix+fract(T)*100.)-.5)*K;col+=grain;',
    ' col=col/(1.+col);col=pow(col,vec3(.92));',
    ' gl_FragColor=vec4(col,1.);}'
  ].join('\n');
  function sh(type, src) { var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { console.error(gl.getShaderInfoLog(s)); return null; } return s; }
  var vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
  if (!vs || !fs) { c.remove(); return; }
  var pr = gl.createProgram(); gl.attachShader(pr, vs); gl.attachShader(pr, fs); gl.linkProgram(pr); gl.useProgram(pr);
  var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  var uO = gl.getUniformLocation(pr, 'O'), uZ = gl.getUniformLocation(pr, 'Z'), uR = gl.getUniformLocation(pr, 'R'), uT = gl.getUniformLocation(pr, 'T'), uM = gl.getUniformLocation(pr, 'M'), uS = gl.getUniformLocation(pr, 'S'), uK = gl.getUniformLocation(pr, 'K');
  var skala = (window.innerWidth < 900) ? 0.6 : 0.8, W = 0, H = 0;
  function size() {
    var r = c.getBoundingClientRect(); W = Math.max(2, Math.round(r.width * skala)); H = Math.max(2, Math.round(r.height * skala));
    if (c.width !== W || c.height !== H) { c.width = W; c.height = H; gl.viewport(0, 0, W, H); }
  }
  var mx = 0, my = 0, tx = 0, ty = 0, sichtbar = true, start = performance.now();
  window.addEventListener('pointermove', function (e) { tx = (e.clientX / window.innerWidth - .5) * 2; ty = (e.clientY / window.innerHeight - .5) * 2; }, { passive: true });
  if ('IntersectionObserver' in window) { new IntersectionObserver(function (es) { sichtbar = es[0].isIntersecting; if (sichtbar && !ruhig) { requestAnimationFrame(frame); } }).observe(c); }
  function frame(now) {
    size();
    mx += (tx - mx) * .05; my += (ty - my) * .05;
    gl.uniform2f(uR, W, H); gl.uniform1f(uT, (now - start) / 1000); gl.uniform2f(uM, mx, my);
    gl.uniform1f(uS, Math.min(1, window.scrollY / 900)); gl.uniform1f(uK, ruhig ? 0.0 : 0.04);
    var breit = W / H > 1.15; gl.uniform2f(uO, breit ? 1.25 : 0.3, breit ? 0.05 : -0.42); gl.uniform1f(uZ, breit ? 1.45 : 1.9);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if (!ruhig && sichtbar && !document.hidden) { requestAnimationFrame(frame); }
  }
  window.addEventListener('resize', function () { size(); if (ruhig) { frame(performance.now()); } });
  document.addEventListener('visibilitychange', function () { if (!document.hidden && !ruhig) { requestAnimationFrame(frame); } });
  if (ruhig) { frame(start); window.addEventListener('scroll', function () { frame(performance.now()); }, { passive: true }); } else { requestAnimationFrame(frame); }
})();
