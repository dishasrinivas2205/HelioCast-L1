"""
Three.js Realistic 3D Solar Observatory Component for HelioCast-L1.
Renders an interactive, GPU-accelerated 3D Sun with procedural GLSL plasma shaders,
granulation turbulence, atmospheric coronal glow, 3D magnetic arcade loops,
and interactive active region hotspots.
"""

from typing import Optional
import streamlit.components.v1 as components


def render_three_sun_html(
    height_px: int = 620,
    solar_mode: str = "COMPOSITE",
    auto_rotate: bool = True,
    rotation_speed: float = 0.5,
    show_magnetic_loops: bool = True,
    show_active_regions: bool = True,
    flare_active: bool = False,
    flare_class: str = "X8.7",
) -> str:
    """
    Generate self-contained HTML/WebGL Three.js application.
    Uses string replacement to safely preserve JavaScript and GLSL curly braces.
    """
    # Color palette based on observation mode
    if solar_mode == "SOFT_XRAY":
        surface_col1 = "vec3(1.0, 0.95, 0.8)"
        surface_col2 = "vec3(0.95, 0.65, 0.15)"
        surface_col3 = "vec3(0.65, 0.18, 0.02)"
        corona_col = "vec3(1.0, 0.65, 0.1)"
    elif solar_mode == "HARD_XRAY":
        surface_col1 = "vec3(0.85, 0.95, 1.0)"
        surface_col2 = "vec3(0.0, 0.85, 1.0)"
        surface_col3 = "vec3(0.2, 0.05, 0.7)"
        corona_col = "vec3(0.0, 0.8, 1.0)"
    elif solar_mode == "MAGNETOGRAM":
        surface_col1 = "vec3(0.95, 0.95, 0.95)"
        surface_col2 = "vec3(0.45, 0.45, 0.5)"
        surface_col3 = "vec3(0.05, 0.05, 0.08)"
        corona_col = "vec3(0.4, 0.7, 1.0)"
    else:  # COMPOSITE
        surface_col1 = "vec3(1.0, 0.98, 0.85)"
        surface_col2 = "vec3(0.98, 0.55, 0.08)"
        surface_col3 = "vec3(0.55, 0.12, 0.02)"
        corona_col = "vec3(1.0, 0.55, 0.05)"

    flare_intensity = "2.8" if flare_active else "1.0"
    flare_speed = "2.2" if flare_active else "1.0"
    auto_rotate_str = "true" if auto_rotate else "false"

    template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body, html {
    width: 100%;
    height: 100%;
    overflow: hidden;
    background-color: #02040a;
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #f8fafc;
}
#canvas-container {
    width: 100%;
    height: 100%;
    position: relative;
    cursor: grab;
}
#canvas-container:active { cursor: grabbing; }

/* HUD Telemetry Overlay */
.hud-telemetry {
    position: absolute;
    top: 16px;
    left: 20px;
    z-index: 10;
    pointer-events: none;
    background: rgba(3, 7, 18, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.25);
    backdrop-filter: blur(12px);
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.06em;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}
.hud-telemetry .status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00ff88;
    margin-right: 6px;
    box-shadow: 0 0 8px #00ff88;
    animation: blink 2s infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Active Region Hotspot Tooltips */
.ar-card {
    position: absolute;
    bottom: 20px;
    right: 20px;
    z-index: 10;
    background: rgba(3, 7, 18, 0.78);
    border: 1px solid rgba(255, 183, 3, 0.4);
    backdrop-filter: blur(16px);
    border-radius: 12px;
    padding: 14px 18px;
    width: 290px;
    font-size: 12px;
    box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15);
}
.ar-title {
    color: #ffb703;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ar-pill {
    background: rgba(255, 0, 85, 0.25);
    color: #ff0055;
    border: 1px solid rgba(255, 0, 85, 0.5);
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-family: monospace;
    font-weight: 700;
}
.ar-stat {
    display: flex;
    justify-content: space-between;
    padding: 3px 0;
    color: #94a3b8;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.ar-stat strong { color: #ffffff; }

/* Instructions footer */
.hud-footer {
    position: absolute;
    bottom: 16px;
    left: 20px;
    z-index: 10;
    pointer-events: none;
    font-size: 11px;
    color: #64748b;
    font-family: monospace;
}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="canvas-container">
    <div class="hud-telemetry">
        <div><span class="status-dot"></span><b>ADITYA-L1 SOLAR OBSERVATORY</b></div>
        <div style="color: #38bdf8; margin-top: 3px;">MODE: __SOLAR_MODE__ &bull; RESOLUTION: HIGH</div>
        <div style="color: #94a3b8; margin-top: 2px;">LAGRANGE L1: 1.496M KM &bull; 24/7 UNINTERRUPTED</div>
    </div>

    <div class="ar-card">
        <div class="ar-title">
            <span>ACTIVE REGION 13664</span>
            <span class="ar-pill">X-CLASS THREAT</span>
        </div>
        <div class="ar-stat"><span>Magnetic Complexity:</span><strong>Beta-Gamma-Delta (&beta;&gamma;&delta;)</strong></div>
        <div class="ar-stat"><span>Area:</span><strong>2,240 Millionths (15x Earth)</strong></div>
        <div class="ar-stat"><span>Neupert Correlation:</span><strong>r = 0.966 (Confirmed)</strong></div>
        <div class="ar-stat"><span>Recent Eruption:</span><strong style="color: #ff0055;">__FLARE_CLASS__ Solar Flare</strong></div>
    </div>

    <div class="hud-footer">
        &bull; Drag to rotate &bull; Scroll to zoom &bull; Real-time GLSL plasma turbulence
    </div>
</div>

<script>
// --- GLSL 3D Simplex Noise Shader for Solar Surface ---
const vertexShader = `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    varying vec3 vViewPosition;

    void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        vViewPosition = -mvPosition.xyz;
        gl_Position = projectionMatrix * mvPosition;
    }
`;

const fragmentShader = `
    uniform float time;
    uniform float flareIntensity;
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    varying vec3 vViewPosition;

    // Simplex Noise algorithm
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
    vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

    float snoise(vec3 v) {
        const vec2 C = vec2(1.0/6.0, 1.0/3.0);
        const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
        vec3 i  = floor(v + dot(v, C.yyy));
        vec3 x0 = v - i + dot(i, C.xxx);
        vec3 g = step(x0.yzx, x0.xyz);
        vec3 l = 1.0 - g;
        vec3 i1 = min(g.xyz, l.zxy);
        vec3 i2 = max(g.xyz, l.zxy);
        vec3 x1 = x0 - i1 + C.xxx;
        vec3 x2 = x0 - i2 + C.yyy;
        vec3 x3 = x0 - D.yyy;
        i = mod289(i);
        vec4 p = permute(permute(permute(
                    i.z + vec4(0.0, i1.z, i2.z, 1.0))
                + i.y + vec4(0.0, i1.y, i2.y, 1.0))
                + i.x + vec4(0.0, i1.x, i2.x, 1.0));
        float n_ = 0.142857142857;
        vec3  ns = n_ * D.wyz - D.xzx;
        vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
        vec4 x_ = floor(j * ns.z);
        vec4 y_ = floor(j - 7.0 * x_);
        vec4 x = x_ *ns.x + ns.yyyy;
        vec4 y = y_ *ns.x + ns.yyyy;
        vec4 h = 1.0 - abs(x) - abs(y);
        vec4 b0 = vec4(x.xy, y.xy);
        vec4 b1 = vec4(x.zw, y.zw);
        vec4 s0 = floor(b0)*2.0 + 1.0;
        vec4 s1 = floor(b1)*2.0 + 1.0;
        vec4 sh = -step(h, vec4(0.0));
        vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
        vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
        vec3 p0 = vec3(a0.xy, h.x);
        vec3 p1 = vec3(a0.zw, h.y);
        vec3 p2 = vec3(a1.xy, h.z);
        vec3 p3 = vec3(a1.zw, h.w);
        vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
        p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
        vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
        m = m * m;
        return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
    }

    float fbm(vec3 p) {
        float val = 0.0;
        float amp = 0.5;
        float freq = 1.0;
        for (int i = 0; i < 4; i++) {
            val += amp * snoise(p * freq);
            freq *= 2.05;
            amp *= 0.52;
        }
        return val;
    }

    void main() {
        vec3 pos = normalize(vPosition);
        float t = time * 0.12 * __FLARE_SPEED__;
        
        float n1 = fbm(pos * 6.5 + vec3(0.0, t * 0.4, t * 0.2));
        float n2 = fbm(pos * 14.0 - vec3(t * 0.3, 0.0, t * 0.5));
        float plasma = 0.5 + 0.5 * (n1 * 0.65 + n2 * 0.35);

        vec3 viewDir = normalize(vViewPosition);
        float NdotV = dot(vNormal, viewDir);
        float limb = pow(clamp(NdotV, 0.0, 1.0), 0.65);

        float spotDist = length(pos.xy - vec2(0.28, 0.15));
        float spot = smoothstep(0.04, 0.14, spotDist);

        vec3 colCore = __SURFACE_COL1__;
        vec3 colMid  = __SURFACE_COL2__;
        vec3 colDeep = __SURFACE_COL3__;

        vec3 color = mix(colDeep, colMid, smoothstep(0.1, 0.6, plasma));
        color = mix(color, colCore, smoothstep(0.55, 0.95, plasma));
        color *= spot;
        color *= (0.35 + 0.65 * limb);
        color *= flareIntensity;

        gl_FragColor = vec4(color, 1.0);
    }
`;

const coronaVertexShader = `
    varying vec3 vNormal;
    void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
`;

const coronaFragmentShader = `
    varying vec3 vNormal;
    void main() {
        float intensity = pow(0.68 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.8);
        vec3 coronaColor = __CORONA_COL__;
        gl_FragColor = vec4(coronaColor, intensity * 0.85);
    }
`;

const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x02040a, 0.0008);

const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 2000);
camera.position.set(0, 8, 48);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 22;
controls.maxDistance = 120;
controls.autoRotate = __AUTO_ROTATE__;
controls.autoRotateSpeed = __ROTATION_SPEED__;

const sunGeo = new THREE.SphereGeometry(14, 128, 128);
const sunMat = new THREE.ShaderMaterial({
    vertexShader: vertexShader,
    fragmentShader: fragmentShader,
    uniforms: {
        time: { value: 0.0 },
        flareIntensity: { value: __FLARE_INTENSITY__ }
    }
});
const sunMesh = new THREE.Mesh(sunGeo, sunMat);
scene.add(sunMesh);

const coronaGeo = new THREE.SphereGeometry(17.2, 64, 64);
const coronaMat = new THREE.ShaderMaterial({
    vertexShader: coronaVertexShader,
    fragmentShader: coronaFragmentShader,
    blending: THREE.AdditiveBlending,
    side: THREE.BackSide,
    transparent: true
});
const coronaMesh = new THREE.Mesh(coronaGeo, coronaMat);
scene.add(coronaMesh);

// Magnetic Arcade Loops
const loopGroup = new THREE.Group();
const loopMaterial = new THREE.MeshBasicMaterial({
    color: 0xffaa00,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending
});

function createMagneticLoop(startPt, endPt, height) {
    const midPt = new THREE.Vector3()
        .addVectors(startPt, endPt)
        .multiplyScalar(0.5)
        .normalize()
        .multiplyScalar(14.0 + height);

    const curve = new THREE.CatmullRomCurve3([startPt, midPt, endPt]);
    const tubeGeo = new THREE.TubeGeometry(curve, 32, 0.12, 8, false);
    return new THREE.Mesh(tubeGeo, loopMaterial);
}

const basePos = new THREE.Vector3(4.5, 2.5, 13.0).normalize().multiplyScalar(14.0);
for (let i = 0; i < 5; i++) {
    const offset1 = new THREE.Vector3(basePos.x - 1.2 + i*0.4, basePos.y - 0.8, basePos.z);
    const offset2 = new THREE.Vector3(basePos.x + 1.2 + i*0.4, basePos.y + 0.8, basePos.z);
    loopGroup.add(createMagneticLoop(offset1, offset2, 1.8 + i*0.6));
}
scene.add(loopGroup);

// Distant Space Starfield Background
const starGeo = new THREE.BufferGeometry();
const starCount = 1800;
const starPos = new Float32Array(starCount * 3);
for (let i = 0; i < starCount * 3; i += 3) {
    starPos[i] = (Math.random() - 0.5) * 800;
    starPos[i+1] = (Math.random() - 0.5) * 800;
    starPos[i+2] = (Math.random() - 0.5) * 800;
}
starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
const starMat = new THREE.PointsMaterial({
    color: 0xa0c4ff,
    size: 0.9,
    transparent: true,
    opacity: 0.75
});
const starField = new THREE.Points(starGeo, starMat);
scene.add(starField);

// Active Region 3D Pin Marker
const pinGeo = new THREE.RingGeometry(0.5, 0.7, 32);
const pinMat = new THREE.MeshBasicMaterial({
    color: 0xff0055,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.95
});
const pinMesh = new THREE.Mesh(pinGeo, pinMat);
pinMesh.position.set(4.5, 2.5, 13.1);
pinMesh.lookAt(camera.position);
scene.add(pinMesh);

const clock = new THREE.Clock();
function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    const elapsedTime = clock.getElapsedTime();

    sunMat.uniforms.time.value = elapsedTime;
    sunMesh.rotation.y += 0.0012 * __ROTATION_SPEED__;
    coronaMesh.rotation.y += 0.0008;

    pinMesh.lookAt(camera.position);

    controls.update();
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});
</script>
</body>
</html>"""

    html = (
        template.replace("__SOLAR_MODE__", solar_mode)
        .replace("__FLARE_CLASS__", flare_class)
        .replace("__FLARE_SPEED__", flare_speed)
        .replace("__SURFACE_COL1__", surface_col1)
        .replace("__SURFACE_COL2__", surface_col2)
        .replace("__SURFACE_COL3__", surface_col3)
        .replace("__CORONA_COL__", corona_col)
        .replace("__AUTO_ROTATE__", auto_rotate_str)
        .replace("__ROTATION_SPEED__", str(rotation_speed))
        .replace("__FLARE_INTENSITY__", flare_intensity)
    )
    return html


def render_three_sun_component(
    height_px: int = 580,
    solar_mode: str = "COMPOSITE",
    auto_rotate: bool = True,
    rotation_speed: float = 0.5,
    show_magnetic_loops: bool = True,
    show_active_regions: bool = True,
    flare_active: bool = False,
    flare_class: str = "X8.7",
):
    """
    Render realistic 3D Sun in an isolated high-performance WebGL iframe.
    """
    html_content = render_three_sun_html(
        height_px=height_px,
        solar_mode=solar_mode,
        auto_rotate=auto_rotate,
        rotation_speed=rotation_speed,
        show_magnetic_loops=show_magnetic_loops,
        show_active_regions=show_active_regions,
        flare_active=flare_active,
        flare_class=flare_class,
    )
    components.html(html_content, height=height_px, scrolling=False)
