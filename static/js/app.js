// Network Path Optimization - Frontend JavaScript

class NetworkOptimizer {
    constructor() {
        this.networkData = null;
        this.globe = null;
        this.currentPath = null;
        this.selectedNodes = new Set();

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupRangeSliders();
        this.initializeVisualization();

        // Handle window resize
        window.addEventListener('resize', () => {
            if (this.globe) {
                const container = document.getElementById('network-canvas');
                this.globe.width(container.clientWidth);
                this.globe.height(container.clientHeight);
            }
        });
    }

    setupEventListeners() {
        document.getElementById('btn-generate').addEventListener('click', () => this.generateNetwork());
        document.getElementById('btn-optimize').addEventListener('click', () => this.optimizePath());
        document.getElementById('btn-compare').addEventListener('click', () => this.compareAlgorithms());
        document.getElementById('btn-run-tests').addEventListener('click', () => this.runTests());
    }

    setupRangeSliders() {
        // Connection probability slider
        const probSlider = document.getElementById('connection-prob');
        const probValue = document.getElementById('prob-value');
        probSlider.addEventListener('input', (e) => {
            probValue.textContent = e.target.value;
        });

        // Weight sliders
        const delaySlider = document.getElementById('weight-delay');
        const reliabilitySlider = document.getElementById('weight-reliability');
        const resourceSlider = document.getElementById('weight-resource');

        const delayValue = document.getElementById('delay-value');
        const reliabilityValue = document.getElementById('reliability-value');
        const resourceValue = document.getElementById('resource-value');
        const sumDisplay = document.getElementById('weights-sum');

        const updateWeights = () => {
            const delay = parseFloat(delaySlider.value);
            const reliability = parseFloat(reliabilitySlider.value);
            const resource = parseFloat(resourceSlider.value);

            delayValue.textContent = delay.toFixed(2);
            reliabilityValue.textContent = reliability.toFixed(2);
            resourceValue.textContent = resource.toFixed(2);

            const sum = delay + reliability + resource;
            sumDisplay.textContent = sum.toFixed(2);

            // Change color based on sum
            if (Math.abs(sum - 1.0) < 0.01) {
                sumDisplay.style.color = 'var(--accent-cyan)';
            } else {
                sumDisplay.style.color = 'var(--accent-pink)';
            }
        };

        delaySlider.addEventListener('input', updateWeights);
        reliabilitySlider.addEventListener('input', updateWeights);
        resourceSlider.addEventListener('input', updateWeights);
    }

    initializeVisualization() {
        const container = document.getElementById('network-canvas');

        this.globe = Globe()
            .globeImageUrl('/static/img/globe/earth-night.jpg')
            .bumpImageUrl('/static/img/globe/earth-topology.png')
            .backgroundImageUrl('/static/img/globe/night-sky.png')
            .width(container.clientWidth)
            .height(container.clientHeight)
            // Arc configuration
            .arcColor('color')
            .arcDashLength(0.4)
            .arcDashGap(0.2)
            .arcDashAnimateTime(0) // Disable validation animation for performance or make it very slow
            .arcStroke(0.5)
            // Point configuration
            .pointColor('color')
            .pointAltitude(0.01)
            .pointRadius(0.5)
            .pointsMerge(true)
            .pointResolution(8) // Lower resolution for better performance
            // Labels configuration
            .labelsData([])
            .labelLat('lat')
            .labelLng('lng')
            .labelText(d => '' + d.id)
            .labelSize(1.5)
            .labelDotRadius(0.0)
            .labelColor(() => '#ffcb21')
            .labelAltitude(0.05)
            .labelResolution(1) // Lowest resolution text
            // Interaction
            .onPointClick((point, event) => {
                this.toggleNodeSelection(point);
            })
            (container);

        // Provide visual feedback that globe is ready
        this.globe.controls().autoRotate = true;
        this.globe.controls().autoRotateSpeed = 0.5;
    }

    toggleNodeSelection(node) {
        if (this.selectedNodes.has(node.id)) {
            this.selectedNodes.delete(node.id);
        } else {
            this.selectedNodes.add(node.id);
        }
        this.updateLabels();
    }

    updateLabels() {
        if (!this.networkData) return;
        const visibleLabels = this.networkData.nodes.filter(n => this.selectedNodes.has(n.id));
        this.globe.labelsData(visibleLabels);
    }

    async generateNetwork() {
        const numNodes = parseInt(document.getElementById('num-nodes').value);
        const connectionProb = parseFloat(document.getElementById('connection-prob').value);
        const seed = document.getElementById('random-seed').value;

        const btn = document.getElementById('btn-generate');
        btn.disabled = true;
        btn.innerHTML = '<span class="loading"></span> Oluşturuluyor...';

        try {
            const response = await fetch('/api/generate_network', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    num_nodes: numNodes,
                    connection_prob: connectionProb,
                    seed: seed ? parseInt(seed) : null
                })
            });

            const data = await response.json();

            if (data.success) {
                this.networkData = data;
                this.visualizeNetwork(data);
                this.updateStatistics(data);
                this.showToast('Ağ başarıyla oluşturuldu!', 'success');

                // Update max values for source/dest inputs
                document.getElementById('source-node').max = numNodes - 1;
                document.getElementById('dest-node').max = numNodes - 1;
                document.getElementById('dest-node').value = numNodes - 1;
            } else {
                this.showToast('Hata: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Sunucu ile iletişim hatası', 'error');
            console.error(error);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '⚡ Ağ Oluştur';
        }
    }

    visualizeNetwork(data) {
        // Map nodes to ensure they have needed properties
        const nodes = data.nodes.map(node => ({
            ...node,
            label: `Düğüm ${node.id}`,
            color: this.getNodeColor(node.reliability),
            size: 0.5
        }));

        // Create a lookup map for nodes for O(1) access
        const nodeMap = new Map(nodes.map(n => [n.id, n]));

        // Limit displayed edges for performance if there are too many
        const MAX_DISPLAY_EDGES = 300;
        let displayEdges = data.edges;

        if (displayEdges.length > MAX_DISPLAY_EDGES) {
            // Randomly sample edges if too many
            displayEdges = displayEdges
                .sort(() => 0.5 - Math.random())
                .slice(0, MAX_DISPLAY_EDGES);
        }

        // Map edges to use lat/lng from source/target nodes
        const edges = displayEdges.reduce((acc, edge) => {
            const sourceNode = nodeMap.get(edge.source);
            const targetNode = nodeMap.get(edge.target);

            // Skip invalid edges where nodes might be missing
            if (!sourceNode || !targetNode) return acc;

            acc.push({
                startLat: sourceNode.lat,
                startLng: sourceNode.lng,
                endLat: targetNode.lat,
                endLng: targetNode.lng,
                color: ['rgba(102, 126, 234, 0.3)', 'rgba(102, 126, 234, 0.3)'],
                stroke: Math.sqrt(edge.bandwidth) / 100, // Reduced scale for globe
                originalData: edge
            });
            return acc;
        }, []);

        this.globe
            .pointsData(nodes)
            .arcsData(edges)
            .pointLabel(d => `
                <div style="background: rgba(0,0,0,0.8); padding: 8px; border-radius: 4px; color: white;">
                    <b>Düğüm ${d.id}</b><br/>
                    Güvenilirlik: ${d.reliability.toFixed(3)}<br/>
                    Gecikme: ${d.processing_delay.toFixed(2)} ms
                </div>
            `);

        // Reset auto-rotate on interaction
        this.globe.controls().addEventListener('start', () => {
            this.globe.controls().autoRotate = false;
        });
    }

    getNodeColor(reliability) {
        if (reliability > 0.99) return '#00f2fe';
        if (reliability > 0.97) return '#667eea';
        return '#f5576c';
    }

    async optimizePath() {
        if (!this.networkData) {
            this.showToast('Önce ağı oluşturmalısınız', 'error');
            return;
        }

        const source = parseInt(document.getElementById('source-node').value);
        const destination = parseInt(document.getElementById('dest-node').value);
        const algorithm = document.getElementById('algorithm').value;

        const weights = {
            delay: parseFloat(document.getElementById('weight-delay').value),
            reliability: parseFloat(document.getElementById('weight-reliability').value),
            resource: parseFloat(document.getElementById('weight-resource').value)
        };

        // Validate weights sum
        const sum = weights.delay + weights.reliability + weights.resource;
        if (Math.abs(sum - 1.0) > 0.01) {
            this.showToast('Ağırlıkların toplamı 1.0 olmalıdır', 'error');
            return;
        }

        const btn = document.getElementById('btn-optimize');
        btn.disabled = true;
        btn.innerHTML = '<span class="loading"></span> Optimize Ediliyor...';

        try {
            const response = await fetch('/api/optimize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source,
                    destination,
                    algorithm,
                    weights
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
                this.highlightPath(data.path);
                this.showToast('En uygun yol bulundu!', 'success');
            } else {
                this.showToast('Hata: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Sunucu ile iletişim hatası', 'error');
            console.error(error);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🚀 Yolu Optimize Et';
        }
    }

    highlightPath(path) {
        if (!this.networkData) return;

        this.currentPath = path;

        // Re-process nodes to highlight path
        const currentNodes = this.networkData.nodes.map(node => {
            const isPathNode = path.includes(node.id);
            const isSource = node.id === path[0];
            const isDest = node.id === path[path.length - 1];

            let color = this.getNodeColor(node.reliability);
            let altitude = 0.01;
            let radius = 0.5;

            if (isPathNode) {
                color = '#00f2fe'; // Cyan for path
                altitude = 0.04;
                radius = 0.8;
            }

            if (isSource) {
                color = '#4facfe'; // Source color
                radius = 1.2;
                altitude = 0.06;
            } else if (isDest) {
                color = '#f5576c'; // Dest color
                radius = 1.2;
                altitude = 0.06;
            }

            return {
                ...node,
                color,
                altitude,
                radius,
                label: `Düğüm ${node.id}`
            };
        });

        // Re-process edges to highlight path
        // Create lookup for current nodes
        const nodeMap = new Map(currentNodes.map(n => [n.id, n]));

        const currentEdges = this.networkData.edges.map(edge => {
            const sourceNode = nodeMap.get(edge.source);
            const targetNode = nodeMap.get(edge.target);

            // Check if edge is part of the path
            let isPathEdge = false;
            // Optimize path check using a Set of strings "src-dst"
            // But since path is short (usually < 100 nodes), loop is fine here.
            for (let i = 0; i < path.length - 1; i++) {
                if ((edge.source === path[i] && edge.target === path[i + 1]) ||
                    (edge.source === path[i + 1] && edge.target === path[i])) {
                    isPathEdge = true;
                    break;
                }
            }

            return {
                startLat: sourceNode.lat,
                startLng: sourceNode.lng,
                endLat: targetNode.lat,
                endLng: targetNode.lng,
                color: isPathEdge ? ['#00f2fe', '#00f2fe'] : ['rgba(102, 126, 234, 0.1)', 'rgba(102, 126, 234, 0.1)'],
                stroke: isPathEdge ? 1.5 : Math.sqrt(edge.bandwidth) / 200, // Reduced stroke for non-path
                dashLength: isPathEdge ? 1 : 0.4,
                dashGap: isPathEdge ? 0.2 : 0.2,
                dashAnimateTime: isPathEdge ? 500 : 1500, // Faster animation for path
                altitude: isPathEdge ? 0.3 : 0 // Arch higher for path
            };
        });

        this.globe
            .pointsData(currentNodes)
            .pointAltitude('altitude')
            .pointRadius('radius')
            .pointColor('color')
            .arcsData(currentEdges)
            .arcColor('color')
            .arcStroke('stroke')
            .arcDashLength('dashLength')
            .arcDashGap('dashGap')
            .arcDashAnimateTime('dashAnimateTime')
            .arcAltitude('altitude');

        // Focus on the path (calculate centroid)
        if (path.length > 0) {
            const sourceNode = currentNodes.find(n => n.id === path[0]);
            if (sourceNode) {
                this.globe.pointOfView({ lat: sourceNode.lat, lng: sourceNode.lng, altitude: 2.5 }, 1000);
            }
        }
    }

    displayResults(data) {
        document.getElementById('results-container').style.display = 'block';

        document.getElementById('result-algorithm').textContent = data.algorithm;
        document.getElementById('result-path-length').textContent = data.path_length + ' düğüm';
        document.getElementById('result-cost').textContent = data.cost.toFixed(4);
        document.getElementById('result-delay').textContent = data.metrics.total_delay.toFixed(2) + ' ms';
        document.getElementById('result-reliability').textContent = (data.metrics.total_reliability * 100).toFixed(2) + '%';
        document.getElementById('result-resource').textContent = data.metrics.resource_cost.toFixed(4);
        document.getElementById('result-time').textContent = data.execution_time.toFixed(3) + ' saniye';

        document.getElementById('stat-time').textContent = data.execution_time.toFixed(2) + 's';
    }

    async compareAlgorithms() {
        if (!this.networkData) {
            this.showToast('Önce ağı oluşturmalısınız', 'error');
            return;
        }

        const source = parseInt(document.getElementById('source-node').value);
        const destination = parseInt(document.getElementById('dest-node').value);

        const weights = {
            delay: parseFloat(document.getElementById('weight-delay').value),
            reliability: parseFloat(document.getElementById('weight-reliability').value),
            resource: parseFloat(document.getElementById('weight-resource').value)
        };

        const btn = document.getElementById('btn-compare');
        btn.disabled = true;
        btn.innerHTML = '<span class="loading"></span> Karşılaştırılıyor...';

        try {
            const response = await fetch('/api/compare_algorithms', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source,
                    destination,
                    weights
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayComparisonResults(data.results);
                this.showToast('Karşılaştırma başarıyla tamamlandı!', 'success');
            } else {
                this.showToast('Hata: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Sunucu ile iletişim hatası', 'error');
            console.error(error);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '📊 Algoritmaları Karşılaştır';
        }
    }

    displayComparisonResults(results) {
        const card = document.getElementById('comparison-card');
        card.style.display = 'block';

        const tbody = document.getElementById('comparison-results');
        tbody.innerHTML = '';

        for (const [algo, data] of Object.entries(results)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${algo}</strong></td>
                <td>${data.cost.toFixed(4)}</td>
                <td>${data.metrics.total_delay.toFixed(2)} ms</td>
                <td>${(data.metrics.total_reliability * 100).toFixed(2)}%</td>
                <td>${data.execution_time.toFixed(3)}</td>
                <td>${data.path_length} düğüm</td>
            `;
            tbody.appendChild(row);
        }

        // Scroll to comparison card
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async runTests() {
        if (!this.networkData) {
            this.showToast('Önce ağı oluşturmalısınız', 'error');
            return;
        }

        let numTests = parseInt(document.getElementById('num-tests').value);
        if (numTests > 20) numTests = 20; // Hard limit for performance

        const btn = document.getElementById('btn-run-tests');
        btn.disabled = true;
        btn.innerHTML = '<span class="loading"></span> Yürütülüyor...';

        try {
            const response = await fetch('/api/run_tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    num_tests: numTests
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayTestResults(data);
                this.showToast('Testler başarıyla tamamlandı!', 'success');
            } else {
                this.showToast('Hata: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Sunucu ile iletişim hatası', 'error');
            console.error(error);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🔬 Testleri Çalıştır';
        }
    }

    displayTestResults(data) {
        const card = document.getElementById('testing-card');
        card.style.display = 'block';

        const container = document.getElementById('testing-results');
        container.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h3 style="color: var(--accent-cyan); margin-bottom: 1rem;">
                    📊 ${data.num_tests} Test Sonuçları
                </h3>
            </div>
            
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Algoritma</th>
                        <th>Ortalama Maliyet</th>
                        <th>Standart Sapma</th>
                        <th>En Düşük Maliyet</th>
                        <th>En Yüksek Maliyet</th>
                        <th>Ortalama Süre</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(data.statistics).map(([algo, stats]) => `
                        <tr>
                            <td><strong>${algo}</strong></td>
                            <td>${stats.mean_cost.toFixed(4)}</td>
                            <td>${stats.std_cost.toFixed(4)}</td>
                            <td>${stats.min_cost.toFixed(4)}</td>
                            <td>${stats.max_cost.toFixed(4)}</td>
                            <td>${stats.mean_time.toFixed(3)}s</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            <div style="margin-top: 2rem;">
                <h3 style="color: var(--accent-cyan); margin-bottom: 1rem;">
                    📈 Sonuç Özeti
                </h3>
                
                <div class="stats-grid">
                    ${Object.entries(data.statistics).map(([algo, stats]) => `
                        <div class="stat-card">
                            <div class="stat-value">${stats.mean_reliability.toFixed(3)}</div>
                            <div class="stat-label">${algo} - Güvenilirlik</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${stats.mean_delay.toFixed(2)}</div>
                            <div class="stat-label">${algo} - Gecikme (ms)</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Scroll to testing card
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    updateStatistics(data) {
        document.getElementById('stat-nodes').textContent = data.num_nodes;
        document.getElementById('stat-edges').textContent = data.num_edges;

        const maxEdges = (data.num_nodes * (data.num_nodes - 1)) / 2;
        const density = (data.num_edges / maxEdges) * 100;
        document.getElementById('stat-density').textContent = density.toFixed(1) + '%';
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const messageEl = document.getElementById('toast-message');

        messageEl.textContent = message;
        toast.className = `toast ${type} show`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    new NetworkOptimizer();
});
