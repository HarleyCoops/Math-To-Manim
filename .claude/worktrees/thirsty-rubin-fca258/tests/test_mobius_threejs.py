#!/usr/bin/env python3
"""
Test ThreeJS animation pipeline with Mobius Homotopy visualization.
Converts the Manim Mobius strip homotopy proof to an interactive 3D WebGL visualization.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_mobius_threejs():
    """Generate a ThreeJS visualization for Mobius strip homotopy equivalence."""
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobius Strip Homotopy Equivalence</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a1a;
            overflow: hidden;
            font-family: 'Segoe UI', sans-serif;
        }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #e0e0e0;
            z-index: 100;
            background: rgba(0,0,0,0.8);
            padding: 20px;
            border-radius: 12px;
            max-width: 420px;
            border: 1px solid #333;
        }
        #info h1 {
            color: #60a5fa;
            font-size: 1.3em;
            margin-bottom: 12px;
        }
        #info .equation {
            background: #1e1e3a;
            padding: 15px;
            border-radius: 8px;
            margin: 12px 0;
            font-family: 'Times New Roman', serif;
            font-size: 1.1em;
            color: #fbbf24;
            text-align: center;
            border: 1px solid #4a4a6a;
        }
        #info .description {
            font-size: 0.9em;
            color: #9ca3af;
            line-height: 1.5;
        }
        #controls {
            position: absolute;
            bottom: 20px;
            left: 20px;
            color: #e0e0e0;
            z-index: 100;
            background: rgba(0,0,0,0.8);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #333;
        }
        #controls label { display: block; margin: 10px 0; }
        #controls input[type="range"] { 
            width: 220px; 
            accent-color: #60a5fa;
        }
        #controls .value {
            color: #60a5fa;
            font-weight: bold;
            min-width: 60px;
            display: inline-block;
        }
        #status {
            position: absolute;
            top: 20px;
            right: 20px;
            color: #e0e0e0;
            z-index: 100;
            background: rgba(0,0,0,0.8);
            padding: 15px 20px;
            border-radius: 12px;
            border: 1px solid #333;
            text-align: center;
        }
        #status .label {
            font-size: 0.85em;
            color: #9ca3af;
            margin-bottom: 5px;
        }
        #status .state {
            font-size: 1.4em;
            font-weight: bold;
        }
        #status .state.strip { color: #3b82f6; }
        #status .state.circle { color: #ef4444; }
        button {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
            font-weight: bold;
            color: white;
            transition: all 0.2s;
        }
        button:hover { 
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            transform: translateY(-1px);
        }
        button.active {
            background: linear-gradient(135deg, #ef4444, #dc2626);
        }
        .legend {
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: #e0e0e0;
            z-index: 100;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #333;
            font-size: 0.85em;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        .legend-color {
            width: 20px;
            height: 4px;
            margin-right: 10px;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <div id="info">
        <h1>Homotopy Equivalence: Mobius Band ~ S1</h1>
        <div class="equation">
            f_t(x, y) = ((1/2 - x)t + x, y)
        </div>
        <p class="description">
            This visualization demonstrates the <strong>deformation retraction</strong> proving 
            that a Mobius band is homotopy equivalent to a circle (S1). 
            Watch as the strip continuously contracts to its central circle.
        </p>
    </div>

    <div id="controls">
        <label>
            Retraction Progress: <span class="value" id="tVal">0%</span>
            <br><input type="range" id="tSlider" min="0" max="100" step="1" value="0">
        </label>
        <label>
            Strip Width: <span class="value" id="wVal">0.70</span>
            <br><input type="range" id="wSlider" min="0.1" max="1.0" step="0.05" value="0.7">
        </label>
        <div style="margin-top: 15px;">
            <button id="playBtn">Play Retraction</button>
            <button id="resetBtn">Reset</button>
        </div>
        <div style="margin-top: 10px;">
            <button id="reverseBtn">Reverse</button>
        </div>
    </div>

    <div id="status">
        <div class="label">Current State</div>
        <div class="state strip" id="stateText">Mobius Strip</div>
    </div>

    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(90deg, #3b82f6, #1e40af);"></div>
            <span>Mobius Surface</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ef4444;"></div>
            <span>Central Circle (S1)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #f97316;"></div>
            <span>Fiber Lines</span>
        </div>
    </div>

    <script type="importmap">
    {
        "imports": {
            "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
            "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
        }
    }
    </script>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0a1a);

        const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(6, 4, 6);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        document.body.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.5;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404060, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(5, 10, 5);
        scene.add(directionalLight);

        const pointLight1 = new THREE.PointLight(0x3b82f6, 0.8, 50);
        pointLight1.position.set(-5, 5, -5);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0xef4444, 0.5, 50);
        pointLight2.position.set(5, -3, 5);
        scene.add(pointLight2);

        // Parameters
        const R = 3.0; // Central radius
        let widthMultiplier = 0.7; // Strip half-width
        let retractionT = 0; // 0 = full strip, 1 = collapsed to circle

        // Mobius strip parametric function
        function mobiusPoint(u, v, width) {
            const effectiveWidth = width * (1 - retractionT);
            const x = (R + effectiveWidth * v * Math.cos(u / 2)) * Math.cos(u);
            const y = (R + effectiveWidth * v * Math.cos(u / 2)) * Math.sin(u);
            const z = effectiveWidth * v * Math.sin(u / 2);
            return new THREE.Vector3(x, z, y); // Swap y,z for better view
        }

        // Create Mobius strip geometry
        function createMobiusGeometry(width) {
            const uSegments = 80;
            const vSegments = 20;
            const geometry = new THREE.BufferGeometry();
            const vertices = [];
            const indices = [];
            const colors = [];
            const uvs = [];

            for (let i = 0; i <= uSegments; i++) {
                for (let j = 0; j <= vSegments; j++) {
                    const u = (i / uSegments) * 2 * Math.PI;
                    const v = (j / vSegments) * 2 - 1; // -1 to 1
                    const point = mobiusPoint(u, v * width, 1);
                    vertices.push(point.x, point.y, point.z);

                    // Color gradient based on v (width position)
                    const hue = 0.6 - Math.abs(v) * 0.15;
                    const color = new THREE.Color().setHSL(hue, 0.7, 0.5);
                    colors.push(color.r, color.g, color.b);

                    uvs.push(i / uSegments, j / vSegments);
                }
            }

            // Create triangles
            for (let i = 0; i < uSegments; i++) {
                for (let j = 0; j < vSegments; j++) {
                    const a = i * (vSegments + 1) + j;
                    const b = a + 1;
                    const c = a + (vSegments + 1);
                    const d = c + 1;

                    indices.push(a, b, c);
                    indices.push(b, d, c);
                }
            }

            geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
            geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
            geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
            geometry.setIndex(indices);
            geometry.computeVertexNormals();

            return geometry;
        }

        // Create central circle (S1)
        function createCentralCircle() {
            const points = [];
            const segments = 100;
            for (let i = 0; i <= segments; i++) {
                const u = (i / segments) * 2 * Math.PI;
                points.push(new THREE.Vector3(
                    R * Math.cos(u),
                    0,
                    R * Math.sin(u)
                ));
            }
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({ 
                color: 0xef4444,
                linewidth: 3
            });
            return new THREE.Line(geometry, material);
        }

        // Create fiber lines
        function createFibers(width) {
            const fibers = new THREE.Group();
            const numFibers = 8;
            
            for (let i = 0; i < numFibers; i++) {
                const u = (i / numFibers) * 2 * Math.PI;
                const points = [];
                const fiberSegments = 10;
                
                for (let j = 0; j <= fiberSegments; j++) {
                    const v = (j / fiberSegments) * 2 - 1;
                    const point = mobiusPoint(u, v * width, 1);
                    points.push(point);
                }
                
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const material = new THREE.LineBasicMaterial({ 
                    color: 0xf97316,
                    linewidth: 2,
                    transparent: true,
                    opacity: 0.8
                });
                fibers.add(new THREE.Line(geometry, material));
            }
            
            return fibers;
        }

        // Mobius strip mesh
        let mobiusMesh;
        let fiberLines;
        const centralCircle = createCentralCircle();
        scene.add(centralCircle);

        function updateMobius() {
            if (mobiusMesh) scene.remove(mobiusMesh);
            if (fiberLines) scene.remove(fiberLines);

            const geometry = createMobiusGeometry(widthMultiplier);
            const material = new THREE.MeshPhongMaterial({
                vertexColors: true,
                side: THREE.DoubleSide,
                shininess: 60,
                transparent: true,
                opacity: 0.85
            });

            mobiusMesh = new THREE.Mesh(geometry, material);
            scene.add(mobiusMesh);

            // Add wireframe overlay
            const wireframe = new THREE.LineSegments(
                new THREE.WireframeGeometry(geometry),
                new THREE.LineBasicMaterial({ 
                    color: 0x60a5fa, 
                    transparent: true, 
                    opacity: 0.15 
                })
            );
            mobiusMesh.add(wireframe);

            // Update fibers
            fiberLines = createFibers(widthMultiplier);
            scene.add(fiberLines);

            // Update status text
            const stateText = document.getElementById('stateText');
            if (retractionT > 0.9) {
                stateText.textContent = 'Circle (S1)';
                stateText.className = 'state circle';
            } else if (retractionT > 0.5) {
                stateText.textContent = 'Retracting...';
                stateText.className = 'state';
                stateText.style.color = '#fbbf24';
            } else {
                stateText.textContent = 'Mobius Strip';
                stateText.className = 'state strip';
            }
        }

        updateMobius();

        // Event listeners
        document.getElementById('tSlider').addEventListener('input', (e) => {
            retractionT = parseFloat(e.target.value) / 100;
            document.getElementById('tVal').textContent = e.target.value + '%';
            updateMobius();
        });

        document.getElementById('wSlider').addEventListener('input', (e) => {
            widthMultiplier = parseFloat(e.target.value);
            document.getElementById('wVal').textContent = widthMultiplier.toFixed(2);
            updateMobius();
        });

        // Animation state
        let animating = false;
        let animDirection = 1;

        document.getElementById('playBtn').addEventListener('click', (e) => {
            animating = !animating;
            e.target.textContent = animating ? 'Pause' : 'Play Retraction';
            e.target.classList.toggle('active', animating);
        });

        document.getElementById('reverseBtn').addEventListener('click', () => {
            animDirection *= -1;
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            retractionT = 0;
            widthMultiplier = 0.7;
            document.getElementById('tSlider').value = 0;
            document.getElementById('wSlider').value = 0.7;
            document.getElementById('tVal').textContent = '0%';
            document.getElementById('wVal').textContent = '0.70';
            animating = false;
            animDirection = 1;
            document.getElementById('playBtn').textContent = 'Play Retraction';
            document.getElementById('playBtn').classList.remove('active');
            updateMobius();
        });

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);

            if (animating) {
                retractionT += 0.003 * animDirection;
                
                if (retractionT >= 1) {
                    retractionT = 1;
                    animating = false;
                    document.getElementById('playBtn').textContent = 'Play Retraction';
                    document.getElementById('playBtn').classList.remove('active');
                } else if (retractionT <= 0) {
                    retractionT = 0;
                    animating = false;
                    document.getElementById('playBtn').textContent = 'Play Retraction';
                    document.getElementById('playBtn').classList.remove('active');
                }

                document.getElementById('tSlider').value = retractionT * 100;
                document.getElementById('tVal').textContent = Math.round(retractionT * 100) + '%';
                updateMobius();
            }

            controls.update();
            renderer.render(scene, camera);
        }

        animate();

        // Handle resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>'''

    # Write the HTML file
    output_path = os.path.join("output", "Mobius_Homotopy_threejs.html")
    os.makedirs("output", exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path

if __name__ == "__main__":
    print("Generating Mobius Homotopy ThreeJS visualization...")
    output_file = generate_mobius_threejs()
    print(f"Generated: {output_file}")
    print(f"File size: {os.path.getsize(output_file):,} bytes")
    
    # Open in browser
    import webbrowser
    abs_path = os.path.abspath(output_file)
    print(f"Opening in browser: {abs_path}")
    webbrowser.open(f"file:///{abs_path}")
