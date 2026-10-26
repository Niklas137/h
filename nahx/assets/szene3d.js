/* NAHX Technologies – 3D-Szene im Aufmacher (WebGL 1, ohne Bibliothek).
   Raymarching: das NAHX-A als extrudierter Körper aus dunklem Glas-Stein mit Mikrostruktur und leuchtenden
   Rissen, Hauptlicht + Gegenlicht + prozedurale Umgebung (GGX-Glanz), weiche Schatten, Umgebungsverschattung,
   spiegelnder Boden mit Reflexion, Staub im Licht, Lichtnebel, Hintergrund-A in Tiefenunschärfe, Bloom,
   Farbsaum, Vignette, Filmkorn. Zweiter Durchgang mischt das Bild zeitlich (Glättung, feiner Motion-Blur).
   Reagiert sanft auf Maus und Scrollen, reduzierte Auflösung, pausiert außerhalb des Bildes; bei
   prefers-reduced-motion ein Standbild. */
(function () {
  var c = document.getElementById('szene3d');
  if (!c) { return; }
  var gl = c.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false, powerPreference: 'high-performance', preserveDrawingBuffer: false });
  if (!gl) { c.remove(); return; }
  var ruhig = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var VS = 'attribute vec2 p;varying vec2 v;void main(){v=p*.5+.5;gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;varying vec2 v;',
    'uniform vec2 R;uniform float T;uniform vec2 M;uniform float S;uniform vec2 O;uniform float Z;uniform float J;',
    'const vec3 GLOW=vec3(.09,.55,.78);const vec3 EDGE=vec3(.45,.86,.98);const vec3 BG0=vec3(.012,.016,.026);',
    'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float hash3(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}',
    'float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*noise(p);p=p*2.07+vec2(1.7,9.2);a*=.5;}return v;}',
    'float sdTri(vec2 p,vec2 a,vec2 b,vec2 c){vec2 e0=b-a,e1=c-b,e2=a-c;vec2 v0=p-a,v1=p-b,v2=p-c;',
    ' vec2 pq0=v0-e0*clamp(dot(v0,e0)/dot(e0,e0),0.,1.);vec2 pq1=v1-e1*clamp(dot(v1,e1)/dot(e1,e1),0.,1.);vec2 pq2=v2-e2*clamp(dot(v2,e2)/dot(e2,e2),0.,1.);',
    ' float s=sign(e0.x*e2.y-e0.y*e2.x);vec2 d=min(min(vec2(dot(pq0,pq0),s*(v0.x*e0.y-v0.y*e0.x)),vec2(dot(pq1,pq1),s*(v1.x*e1.y-v1.y*e1.x))),vec2(dot(pq2,pq2),s*(v2.x*e2.y-v2.y*e2.x)));return -sqrt(d.x)*sign(d.y);}',
    'float sdA(vec2 p){float o=sdTri(p,vec2(0.,1.),vec2(1.03,-.5),vec2(-1.03,-.5));float h=sdTri(p,vec2(0.,.47),vec2(.63,-.5),vec2(-.63,-.5));float i=sdTri(p,vec2(0.,.05),vec2(.35,-.5),vec2(-.35,-.5));return min(max(o,-h),i);}',
    'float sdBody(vec3 q){float d2=sdA(q.xy);float dz=abs(q.z)-.22;vec2 w=vec2(d2,dz);return min(max(w.x,w.y),0.)+length(max(w,0.))-.05;}',
    'mat2 rot(float a){float s=sin(a),c=cos(a);return mat2(c,-s,s,c);}',
    'const float FLOOR=-1.45;',
    'vec3 xf(vec3 p){p.xy-=O;p*=Z;p.yz*=rot(-.14+M.y*.14);p.xz*=rot(.42+M.x*.26+T*.05+S*.5);return p;}',
    'float mapA(vec3 p){return sdBody(xf(p))/Z;}',
    // Hintergrund-A: weit hinten, größer, anders gedreht
    'float mapB(vec3 p){p-=vec3(-1.6,.9,-5.5);p*=.55;p.xz*=rot(-.9+T*.03);p.yz*=rot(.3);return sdBody(p)/.55;}',
    'vec2 map(vec3 p){float a=mapA(p);float f=p.y-FLOOR;float b=mapB(p);float d=min(a,min(f,b));return vec2(d,d==a?1.:(d==f?2.:3.));}',
    'vec3 nrm(vec3 p){vec2 e=vec2(.0012,0.);return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x,map(p+e.yxy).x-map(p-e.yxy).x,map(p+e.yyx).x-map(p-e.yyx).x));}',
    'float shadow(vec3 ro,vec3 rd){float r=1.,t=.03;for(int i=0;i<28;i++){float h=min(mapA(ro+rd*t),mapB(ro+rd*t));r=min(r,10.*h/t);if(h<.001||t>6.)break;t+=clamp(h,.02,.3);}return clamp(r,0.,1.);}',
    'float ao(vec3 p,vec3 n){float o=0.,s=1.;for(int i=1;i<=5;i++){float h=.04*float(i);o+=(h-map(p+n*h).x)*s;s*=.6;}return clamp(1.-2.2*o,0.,1.);}',
    // Prozedurale Umgebung für Reflexionen: dunkler Raum, grüne Lichtbahn oben rechts, kaltes Gegenlicht links
    'vec3 env(vec3 d){float up=d.y*.5+.5;vec3 e=mix(BG0*1.5,vec3(.04,.06,.045),up);e+=GLOW*1.4*pow(max(dot(d,normalize(vec3(.6,.8,.3))),0.),14.);e+=vec3(.25,.3,.3)*pow(max(dot(d,normalize(vec3(-.8,.2,-.4))),0.),20.);return e;}',
    'float ggx(vec3 n,vec3 v,vec3 l,float r){vec3 h=normalize(v+l);float nh=max(dot(n,h),0.),a=r*r,a2=a*a;float d=nh*nh*(a2-1.)+1.;return a2/(3.1416*d*d+1e-4);}',
    // Material des A: dunkles Glas-Gestein mit Mikrostruktur, Rissen (emissiv), leichter Kantenabrieb
    'void matA(vec3 p,inout vec3 n,out vec3 alb,out float rough,out vec3 emis){vec3 q=xf(p);vec2 uv=q.xy*4.+q.z*.7;',
    ' float micro=fbm(uv*6.);float crk=fbm(uv*2.3+7.1);float cracks=smoothstep(.50,.53,crk)*(1.-smoothstep(.53,.56,crk));',
    ' float veins=smoothstep(.62,.7,fbm(uv*1.4+3.3));',
    ' vec2 e=vec2(.02,0.);float dx=fbm((uv+e.xy)*6.)-micro,dy=fbm((uv+e.yx)*6.)-micro;n=normalize(n+vec3(dx,dy,0.)*.9+vec3(cracks)*.3);',
    ' alb=mix(vec3(.03,.04,.06),vec3(.08,.11,.15),micro)+veins*vec3(.04,.07,.10);rough=mix(.18,.45,micro);',
    ' emis=GLOW*cracks*1.4+EDGE*cracks*cracks*.8;}',
    'vec3 shadeHit(vec3 p,vec3 rd,float id,out float refl){vec3 n=nrm(p);vec3 V=-rd;vec3 L1=normalize(vec3(.6,.9,.6));vec3 L2=normalize(vec3(-.9,.3,-.2));',
    ' vec3 alb;float rough;vec3 emis=vec3(0.);refl=0.;',
    ' if(id==2.){float g=fbm(p.xz*1.5);alb=vec3(.010,.013,.020)*(0.8+.4*g);rough=.08+.1*g;n=normalize(n+vec3(fbm(p.xz*9.)-.5,0.,fbm(p.zx*9.+2.)-.5)*.02);refl=.55;}',
    ' else if(id==3.){alb=vec3(.04,.05,.07);rough=.5;}',
    ' else {matA(p,n,alb,rough,emis);refl=.35;}',
    ' float sh=shadow(p+n*.02,L1);float occ=ao(p,n);',
    ' float d1=max(dot(n,L1),0.)*sh,d2=max(dot(n,L2),0.);',
    ' vec3 col=alb*(vec3(.06,.08,.07)*occ+d1*vec3(1.1,1.2,1.1)*.9+d2*vec3(.2,.24,.26));',
    ' col+=ggx(n,V,L1,rough)*sh*EDGE*.22+ggx(n,V,L2,rough+.1)*vec3(.3,.36,.38)*.12;',
    ' float fre=pow(1.-max(dot(n,V),0.),4.);vec3 Rv=reflect(rd,n);col+=env(Rv)*mix(.08,.7,fre)*refl*.8;',
    ' col+=fre*GLOW*.9*occ;col+=emis*(.8+.4*sin(T*.7+p.y*3.));return col;}',
    'vec3 render(vec2 uv,vec3 ro,vec3 rd,out float depth){float t=.0,dmin=9.;float id=0.;bool hit=false;',
    ' for(int i=0;i<84;i++){vec2 m=map(ro+rd*t);dmin=min(dmin,m.x/max(t,.6));if(m.x<.0012){hit=true;id=m.y;break;}t+=m.x*.85;if(t>14.)break;}',
    ' depth=t;vec3 col=env(rd)*.35+BG0;',
    ' if(hit){vec3 p=ro+rd*t;float rf;col=shadeHit(p,rd,id,rf);',
    '  if(id==2.){vec3 n=nrm(p);vec3 rr=reflect(rd,n);rr.y+=fbm(p.xz*4.)*.08;rr=normalize(rr);float tt=.05;bool h2=false;float id2=0.;',
    '   for(int k=0;k<36;k++){vec3 q=p+rr*tt;float a=mapA(q),b=mapB(q);float d=min(a,b);if(d<.002){h2=true;id2=d==a?1.:3.;break;}tt+=d*.9;if(tt>9.)break;}',
    '   if(h2){float r2;vec3 rc=shadeHit(p+rr*tt,rr,id2,r2);col+=rc*.32*exp(-tt*.3);}else{col+=env(rr)*.06;}}',
    '  col=mix(col,BG0*1.2,smoothstep(3.,13.,t));',
    '  if(id==3.){col=mix(col,BG0*1.3,.8);}}',
    ' float g=0.;float tt=.8;for(int i=0;i<18;i++){vec3 q=ro+rd*tt;float dd=mapA(q);g+=exp(-dd*6.)*.008;tt+=.24;}col+=g*GLOW*(1.05+.3*sin(T*.4));',
    ' if(!hit||id!=1.){col+=EDGE*exp(-dmin*60.)*.8+GLOW*exp(-dmin*12.)*.3;}',
    ' return col;}',
    'void main(){vec2 pix=gl_FragCoord.xy+J;vec2 uv=(pix-.5*R)/R.y;',
    ' vec3 ro=vec3(0.,.1,3.9);vec3 rd=normalize(vec3(uv,-1.9));',
    ' float depth;vec3 col=render(uv,ro,rd,depth);',
    // Staub im Licht
    ' float dust=0.;for(int i=0;i<3;i++){float fi=float(i);vec2 q=uv*(3.+fi*2.)+vec2(T*.02*(fi+1.),-T*.03);vec2 ip=floor(q),fp=fract(q);float h=hash(ip+fi*17.);vec2 cp=vec2(hash(ip+1.3),hash(ip+2.7));float dd=length(fp-cp);dust+=smoothstep(.06,.0,dd)*step(.86,h)*(.5+.5*sin(T*2.+h*40.));}col+=dust*EDGE*.35;',
    ' col*=1.-.5*pow(length(uv*vec2(.8,1.)),2.4);',
    ' col=col/(1.+col);col=pow(col,vec3(.9));',
    ' gl_FragColor=vec4(col,1.);}'
  ].join('\n');
  // Zweiter Durchgang: zeitliche Mischung + Bloom + Korn
  var FS2 = [
    'precision highp float;varying vec2 v;uniform sampler2D A;uniform sampler2D B;uniform float W;uniform vec2 R;uniform float T;uniform float K;',
    'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'void main(){vec2 d=(v-.5)*.004*length(v-.5)*2.;vec3 cur=vec3(texture2D(A,v+d).r,texture2D(A,v).g,texture2D(A,v-d).b);vec3 prev=texture2D(B,v).rgb;vec3 col=mix(cur,prev,W);',
    ' vec3 bl=vec3(0.);vec2 px=1./R;for(int i=-2;i<=2;i++)for(int j=-2;j<=2;j++){vec3 s=texture2D(A,v+vec2(float(i),float(j))*px*3.).rgb;bl+=max(s-.55,0.);}bl/=25.;col+=bl*.9;',
    ' col+=(hash(gl_FragCoord.xy+fract(T)*100.)-.5)*K;gl_FragColor=vec4(col,1.);}'
  ].join('\n');
  var FSC = 'precision highp float;varying vec2 v;uniform sampler2D A;void main(){gl_FragColor=texture2D(A,v);}';
  function sh(type, src) { var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { console.error(gl.getShaderInfoLog(s)); return null; } return s; }
  function prog(fsrc) { var p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VS)); var f = sh(gl.FRAGMENT_SHADER, fsrc); if (!f) { return null; } gl.attachShader(p, f); gl.linkProgram(p); return p; }
  var P1 = prog(FS), P2 = prog(FS2), PC = prog(FSC);
  if (!P1 || !P2 || !PC) { c.remove(); return; }
  var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  function attr(p) { var l = gl.getAttribLocation(p, 'p'); gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l, 2, gl.FLOAT, false, 0, 0); }
  function U(p, n) { return gl.getUniformLocation(p, n); }
  var u1 = { R: U(P1, 'R'), T: U(P1, 'T'), M: U(P1, 'M'), S: U(P1, 'S'), O: U(P1, 'O'), Z: U(P1, 'Z'), J: U(P1, 'J') };
  var u2 = { A: U(P2, 'A'), B: U(P2, 'B'), W: U(P2, 'W'), R: U(P2, 'R'), T: U(P2, 'T'), K: U(P2, 'K') };
  var uc = { A: U(PC, 'A') };
  function tex(w, h) { var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE); return t; }
  function fbo(t) { var f = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, f); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0); return f; }
  var skala = (window.innerWidth < 900) ? 0.55 : 0.7, W = 0, H = 0, tA, fA, tH = [], fH = [], ping = 0;
  function size() {
    var r = c.getBoundingClientRect(); var w = Math.max(2, Math.round(r.width * skala)), h = Math.max(2, Math.round(r.height * skala));
    if (w === W && h === H) { return; }
    W = w; H = h; c.width = W; c.height = H;
    tA = tex(W, H); fA = fbo(tA); tH = [tex(W, H), tex(W, H)]; fH = [fbo(tH[0]), fbo(tH[1])];
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  }
  var mx = 0, my = 0, tx = 0, ty = 0, sichtbar = true, start = performance.now(), frames = 0;
  window.addEventListener('pointermove', function (e) { tx = (e.clientX / window.innerWidth - .5) * 2; ty = (e.clientY / window.innerHeight - .5) * 2; }, { passive: true });
  if ('IntersectionObserver' in window) { new IntersectionObserver(function (es) { sichtbar = es[0].isIntersecting; if (sichtbar && !ruhig) { requestAnimationFrame(frame); } }).observe(c); }
  var jit = [[.25, .25], [-.25, .25], [.25, -.25], [-.25, -.25]];
  function frame(now) {
    size();
    mx += (tx - mx) * .05; my += (ty - my) * .05;
    var breit = W / H > 1.15, j = jit[frames % 4];
    // 1) Szene in Textur A
    gl.bindFramebuffer(gl.FRAMEBUFFER, fA); gl.viewport(0, 0, W, H); gl.useProgram(P1); attr(P1);
    gl.uniform2f(u1.R, W, H); gl.uniform1f(u1.T, (now - start) / 1000); gl.uniform2f(u1.M, mx, my); gl.uniform1f(u1.S, Math.min(1, window.scrollY / 900));
    var asp = W / H; gl.uniform2f(u1.O, breit ? Math.min(1.15, asp * 0.44) : 0.25, breit ? 0.0 : -0.75); gl.uniform1f(u1.Z, breit ? (asp < 1.9 ? 1.7 : 1.5) : 1.8); gl.uniform1f(u1.J, j[0]);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    // 2) zeitliche Mischung mit Vorbild in Historie
    gl.bindFramebuffer(gl.FRAMEBUFFER, fH[ping]); gl.useProgram(P2); attr(P2);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tA); gl.uniform1i(u2.A, 0);
    gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, tH[1 - ping]); gl.uniform1i(u2.B, 1);
    gl.uniform1f(u2.W, frames < 2 ? 0 : 0.6); gl.uniform2f(u2.R, W, H); gl.uniform1f(u2.T, (now - start) / 1000); gl.uniform1f(u2.K, ruhig ? 0 : 0.035);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    // 3) auf den Bildschirm
    gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.useProgram(PC); attr(PC);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tH[ping]); gl.uniform1i(uc.A, 0);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    ping = 1 - ping; frames++;
    if (!ruhig && sichtbar && !document.hidden) { requestAnimationFrame(frame); }
  }
  window.addEventListener('resize', function () { size(); frames = 0; if (ruhig) { frame(performance.now()); } });
  document.addEventListener('visibilitychange', function () { if (!document.hidden && !ruhig) { requestAnimationFrame(frame); } });
  if (ruhig) { for (var k = 0; k < 4; k++) { frame(start); } window.addEventListener('scroll', function () { frame(performance.now()); }, { passive: true }); } else { requestAnimationFrame(frame); }
})();
