import * as THREE from 'three';
import { TrackballControls } from 'three/examples/jsm/controls/TrackballControls.js';
import { PDBLoader } from 'three/examples/jsm/loaders/PDBLoader.js';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';

const loader = new PDBLoader();

const PDB_PATH = 'models/pdb/caffeine.pdb'; // Ensure this path is correct

let camera, scene, renderer, labelRenderer;
let controls;
let root;

init();

function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050505);

    camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 5000);
    camera.position.z = 1000;
    scene.add(camera);

    const light1 = new THREE.DirectionalLight(0xffffff, 2.5);
    light1.position.set(1, 1, 1);
    scene.add(light1);

    const light2 = new THREE.DirectionalLight(0xffffff, 1.5);
    light2.position.set(-1, -1, 1);
    scene.add(light2);

    root = new THREE.Group();
    scene.add(root);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    labelRenderer = new CSS2DRenderer();
    labelRenderer.setSize(window.innerWidth, window.innerHeight);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0px';
    labelRenderer.domElement.style.pointerEvents = 'none';
    document.body.appendChild(labelRenderer.domElement);

    controls = new TrackballControls(camera, renderer.domElement);
    controls.minDistance = 500;
    controls.maxDistance = 2000;

    loadMolecule(PDB_PATH); // Automatically load caffeine.pdb

    window.addEventListener('resize', onWindowResize);

    animate();
}

function loadMolecule(url) {
    while (root.children.length > 0) {
        const object = root.children[0];
        object.parent.remove(object);
    }

    loader.load(
        url,
        function (pdb) {
            const geometryAtoms = pdb.geometryAtoms;
            const geometryBonds = pdb.geometryBonds;
            const json = pdb.json;

            const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
            const sphereGeometry = new THREE.IcosahedronGeometry(1, 3);

            const offset = new THREE.Vector3();
            geometryAtoms.computeBoundingBox();
            geometryAtoms.boundingBox.getCenter(offset).negate();

            geometryAtoms.translate(offset.x, offset.y, offset.z);
            geometryBonds.translate(offset.x, offset.y, offset.z);

            const positions = geometryAtoms.getAttribute('position');
            const colors = geometryAtoms.getAttribute('color');

            const position = new THREE.Vector3();
            const color = new THREE.Color();

            for (let i = 0; i < positions.count; i++) {
                position.x = positions.getX(i);
                position.y = positions.getY(i);
                position.z = positions.getZ(i);

                color.r = colors.getX(i);
                color.g = colors.getY(i);
                color.b = colors.getZ(i);

                const material = new THREE.MeshPhongMaterial({ color: color });
                const object = new THREE.Mesh(sphereGeometry, material);
                object.position.copy(position);
                object.position.multiplyScalar(75);
                object.scale.multiplyScalar(25);
                root.add(object);

                const atom = json.atoms[i];
                const text = document.createElement('div');
                text.className = 'label';
                text.style.color = `rgb(${atom[3][0]}, ${atom[3][1]}, ${atom[3][2]})`;
                text.textContent = atom[4];

                const label = new CSS2DObject(text);
                label.position.copy(object.position);
                root.add(label);
            }

            const bondPositions = geometryBonds.getAttribute('position');
            const start = new THREE.Vector3();
            const end = new THREE.Vector3();

            for (let i = 0; i < bondPositions.count; i += 2) {
                start.x = bondPositions.getX(i);
                start.y = bondPositions.getY(i);
                start.z = bondPositions.getZ(i);

                end.x = bondPositions.getX(i + 1);
                end.y = bondPositions.getY(i + 1);
                end.z = bondPositions.getZ(i + 1);

                start.multiplyScalar(75);
                end.multiplyScalar(75);

                const object = new THREE.Mesh(boxGeometry, new THREE.MeshPhongMaterial({ color: 0xffffff }));
                object.position.copy(start);
                object.position.lerp(end, 0.5);
                object.scale.set(5, 5, start.distanceTo(end));
                object.lookAt(end);
                root.add(object);
            }
        },
        function (xhr) {
            console.log((xhr.loaded / xhr.total * 100) + '% loaded');
        },
        function (error) {
            console.log('An error happened', error);
        }
    );
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    labelRenderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    controls.update();
    const time = Date.now() * 0.0004;

    root.rotation.x = time;
    root.rotation.y = time * 0.7;

    render();
}

function render() {
    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
}