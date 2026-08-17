/* AHADU · Pangenome Visual Explorer Engine */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initTopologyGraph();
  initSalienceSimulator();
  initEpidemiologyRadar();
  initMemoryScaffold();
  initControlPlane();
  initChatSocket();
});

// --------------------------------------------------------------------------
// Navigation & Tab Switching
// --------------------------------------------------------------------------
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');
  const panes = document.querySelectorAll('.tab-pane');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panes.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const targetPane = document.getElementById(`tab-${tab.dataset.tab}`);
      if (targetPane) targetPane.classList.add('active');
    });
  });
}

// --------------------------------------------------------------------------
// Tab 1: Topology Canvas & Manifest Inspector
// --------------------------------------------------------------------------
function initTopologyGraph() {
  const canvas = document.getElementById('topology-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const nodes = [
    { id: 'chromosome', name: 'Chromosome Root', type: 'root', x: 400, y: 210, r: 24, color: '#a855f7', state: 'TRUSTED' },
    { id: 'p1', name: 'mcp-server-github', type: 'mcp', x: 260, y: 120, r: 14, color: '#38bdf8', state: 'LYSOGENIC', origin: 'registry.modelcontextprotocol.io' },
    { id: 'p2', name: 'mcp-server-sqlite', type: 'mcp', x: 540, y: 120, r: 14, color: '#38bdf8', state: 'LYSOGENIC', origin: 'registry.modelcontextprotocol.io' },
    { id: 'p3', name: 'skill-optics-buffer', type: 'skill', x: 230, y: 300, r: 14, color: '#22c55e', state: 'LYTIC', origin: 'scaffold-tier-3' },
    { id: 'p4', name: 'skill-crispr-screening', type: 'skill', x: 570, y: 300, r: 14, color: '#38bdf8', state: 'LYSOGENIC', origin: 'scaffold-tier-3' },
    { id: 'p5', name: 'mcp-server-fetch', type: 'mcp', x: 140, y: 210, r: 12, color: '#ef4444', state: 'LYTIC', origin: 'registry.modelcontextprotocol.io' },
    { id: 'p6', name: 'skill-swanson-abc', type: 'skill', x: 660, y: 210, r: 12, color: '#38bdf8', state: 'LYSOGENIC', origin: 'scaffold-tier-2' }
  ];

  const links = [
    { source: 'chromosome', target: 'p1' },
    { source: 'chromosome', target: 'p2' },
    { source: 'chromosome', target: 'p3' },
    { source: 'chromosome', target: 'p4' },
    { source: 'p1', target: 'p5' },
    { source: 'p4', target: 'p6' }
  ];

  let selectedNode = nodes[0];
  let angleOffset = 0;

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    angleOffset += 0.005;

    // Draw grid background
    ctx.strokeStyle = '#152035';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 40) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }

    // Draw Links
    links.forEach(l => {
      const s = nodes.find(n => n.id === l.source);
      const t = nodes.find(n => n.id === l.target);
      if (s && t) {
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.strokeStyle = '#233454';
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // Draw Nodes
    nodes.forEach(n => {
      // Gentle orbital wobble
      if (n.id !== 'chromosome') {
        n.x += Math.sin(angleOffset + n.r) * 0.2;
        n.y += Math.cos(angleOffset + n.r) * 0.2;
      }

      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r + (n === selectedNode ? 6 : 0), 0, Math.PI * 2);
      ctx.fillStyle = n.color;
      ctx.shadowColor = n.color;
      ctx.shadowBlur = n === selectedNode ? 18 : 8;
      ctx.fill();
      ctx.shadowBlur = 0;

      if (n === selectedNode) {
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Label
      ctx.fillStyle = '#f1f5f9';
      ctx.font = '11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(n.name, n.x, n.y + n.r + 14);
    });

    requestAnimationFrame(render);
  }

  render();

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
    const my = (e.clientY - rect.top) * (canvas.height / rect.height);

    const clicked = nodes.find(n => Math.hypot(n.x - mx, n.y - my) <= n.r + 6);
    if (clicked) {
      selectedNode = clicked;
      updateNodeDetails(clicked);
    }
  });

  function updateNodeDetails(node) {
    document.getElementById('m-id').textContent = node.name;
    document.getElementById('node-type-badge').textContent = node.type.toUpperCase();
    if (node.id === 'chromosome') {
      document.getElementById('m-steward').textContent = 'Samuel Ghedamu';
      document.getElementById('m-pubkey').textContent = 'ed25519:7a8b...4f91';
      document.getElementById('m-constitution').textContent = 'VERIFIED (SHA-256)';
    } else {
      document.getElementById('m-steward').textContent = node.origin || 'Extracted Locus';
      document.getElementById('m-pubkey').textContent = `pid:${node.id.repeat(4).slice(0, 16)}`;
      document.getElementById('m-constitution').textContent = `State: ${node.state}`;
    }
  }
}

// --------------------------------------------------------------------------
// Tab 2: Salience Attention Field Simulator
// --------------------------------------------------------------------------
function initSalienceSimulator() {
  const profileSelect = document.getElementById('salience-profile-select');
  const tableBody = document.querySelector('#salience-table tbody');
  const taskResult = document.getElementById('sim-task-result');
  const noticedResult = document.getElementById('sim-noticed-result');
  if (!profileSelect || !tableBody) return;

  const dataset = {
    GENERALIST: [
      { locus: 'deodorant-fresh-spray', cat: 'deodorant', score: 0.88, surprise: '0.12', verdict: 'TASK_ANSWER' },
      { locus: 'deodorant-rollon-dry', cat: 'deodorant', score: 0.85, surprise: '0.08', verdict: 'TASK_ANSWER' },
      { locus: 'deodorant-stick-sport', cat: 'deodorant', score: 0.84, surprise: '0.05', verdict: 'TASK_ANSWER' },
      { locus: 'sunglasses-aviator-uv400', cat: 'eyewear', score: 0.32, surprise: '-0.45', verdict: 'IGNORE' },
      { locus: 'cotton-shirt-oxford', cat: 'apparel', score: 0.28, surprise: '-0.52', verdict: 'IGNORE' }
    ],
    OPTICIAN: [
      { locus: 'deodorant-fresh-spray', cat: 'deodorant', score: 0.88, surprise: '0.12', verdict: 'TASK_ANSWER' },
      { locus: 'deodorant-rollon-dry', cat: 'deodorant', score: 0.85, surprise: '0.08', verdict: 'TASK_ANSWER' },
      { locus: 'deodorant-stick-sport', cat: 'deodorant', score: 0.84, surprise: '0.05', verdict: 'TASK_ANSWER' },
      { locus: 'sunglasses-designer-clearance', cat: 'eyewear', score: 0.931, surprise: '+3.14 (Off-Price)', verdict: 'INTERRUPT' },
      { locus: 'polarised-clip-on-lens', cat: 'eyewear', score: 0.920, surprise: '+2.98 (Off-Price)', verdict: 'INVESTIGATE' },
      { locus: 'sunglasses-aviator-uv400', cat: 'eyewear', score: 0.685, surprise: '+1.42', verdict: 'REMEMBER' }
    ],
    TAILOR: [
      { locus: 'deodorant-fresh-spray', cat: 'deodorant', score: 0.88, surprise: '0.12', verdict: 'TASK_ANSWER' },
      { locus: 'deodorant-rollon-dry', cat: 'deodorant', score: 0.85, surprise: '0.08', verdict: 'TASK_ANSWER' },
      { locus: 'deodorant-stick-sport', cat: 'deodorant', score: 0.84, surprise: '0.05', verdict: 'TASK_ANSWER' },
      { locus: 'cotton-shirt-oxford', cat: 'apparel', score: 0.681, surprise: '+1.85', verdict: 'INVESTIGATE' },
      { locus: 'wool-blend-coat', cat: 'apparel', score: 0.669, surprise: '+1.72', verdict: 'INVESTIGATE' },
      { locus: 'linen-trousers', cat: 'apparel', score: 0.658, surprise: '+1.64', verdict: 'REMEMBER' }
    ]
  };

  function updateSimulator(profileKey) {
    const rows = dataset[profileKey] || dataset.OPTICIAN;
    tableBody.innerHTML = '';

    rows.forEach(r => {
      const tr = document.createElement('tr');
      const verdictClass = r.verdict === 'INTERRUPT' ? 'text-danger' :
                           r.verdict === 'INVESTIGATE' ? 'text-accent' :
                           r.verdict === 'TASK_ANSWER' ? 'text-primary' : 'text-muted';
      tr.innerHTML = `
        <td class="code">${r.locus}</td>
        <td>${r.cat}</td>
        <td><strong>${r.score}</strong></td>
        <td class="${r.surprise.includes('Off-Price') ? 'text-success' : ''}">${r.surprise}</td>
        <td><span class="${verdictClass}">${r.verdict}</span></td>
      `;
      tableBody.appendChild(tr);
    });

    if (profileKey === 'OPTICIAN') {
      taskResult.textContent = '3 Deodorant items ($4.50, $5.00, $5.20)';
      noticedResult.textContent = 'sunglasses-designer-clearance ($11.00 - 0.931 surprise)';
    } else if (profileKey === 'TAILOR') {
      taskResult.textContent = '3 Deodorant items ($4.50, $5.00, $5.20)';
      noticedResult.textContent = 'cotton-shirt-oxford ($24.00 - 0.681 graph activation)';
    } else {
      taskResult.textContent = '3 Deodorant items ($4.50, $5.00, $5.20)';
      noticedResult.textContent = 'Nothing above threshold (Unprimed Generalist)';
    }
  }

  profileSelect.addEventListener('change', (e) => updateSimulator(e.target.value));
  updateSimulator('OPTICIAN');
}

// --------------------------------------------------------------------------
// Tab 3: Epidemiological Outbreak Radar Chart
// --------------------------------------------------------------------------
function initEpidemiologyRadar() {
  const canvas = document.getElementById('epidemiology-canvas');
  const tableBody = document.querySelector('#outbreak-table tbody');
  if (!canvas || !tableBody) return;
  const ctx = canvas.getContext('2d');

  const outbreaks = [
    { locus: 'mcp/github-search', source: 'mcp_registry', r0: '1.84', lifetime_r: '0.0142', days: 5, phase: 'outbreak', fit_r2: '0.94' },
    { locus: 'mcp/sqlite-connector', source: 'mcp_registry', r0: '1.42', lifetime_r: '0.0098', days: 4, phase: 'outbreak', fit_r2: '0.91' },
    { locus: 'skill/git-bisect-helper', source: 'github_skills', r0: '1.12', lifetime_r: '0.0041', days: 3, phase: 'decelerating', fit_r2: '0.88' },
    { locus: 'mcp/memory-store', source: 'mcp_registry', r0: '—', lifetime_r: '0.0025', days: 2, phase: 'no-history', fit_r2: '—' }
  ];

  tableBody.innerHTML = outbreaks.map(o => `
    <tr>
      <td class="code">${o.locus}</td>
      <td>${o.source}</td>
      <td class="text-primary"><strong>${o.r0}</strong></td>
      <td>${o.lifetime_r}</td>
      <td>${o.days}</td>
      <td><span class="badge ${o.phase === 'outbreak' ? 'badge-success' : 'badge-primary'}">${o.phase}</span></td>
    </tr>
  `).join('');

  // Render Growth Curves
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = '#152035';
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(50, 20); ctx.lineTo(50, 220); ctx.lineTo(550, 220); ctx.stroke();

  // Axis Labels
  ctx.fillStyle = '#64748b';
  ctx.font = '10px Inter, sans-serif';
  ctx.fillText('Time (Days)', 280, 245);
  ctx.fillText('Adoption Signal', 10, 15);

  // Curve 1 (Outbreak)
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(50, 210);
  ctx.quadraticCurveTo(250, 200, 550, 40);
  ctx.stroke();

  // Curve 2 (Logistic Saturation)
  ctx.strokeStyle = '#a855f7';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(50, 215);
  ctx.bezierCurveTo(200, 210, 350, 110, 550, 110);
  ctx.stroke();
}

// --------------------------------------------------------------------------
// Tab 4: Memory Scaffold & Ebbinghaus Decay Chart
// --------------------------------------------------------------------------
function initMemoryScaffold() {
  const canvas = document.getElementById('memory-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Ebbinghaus Curve
  ctx.strokeStyle = '#233454';
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(40, 20); ctx.lineTo(40, 200); ctx.lineTo(560, 200); ctx.stroke();

  ctx.fillStyle = '#64748b';
  ctx.font = '10px Inter, sans-serif';
  ctx.fillText('Retention %', 5, 15);
  ctx.fillText('Time (Days)', 280, 225);

  // Unrehearsed Decay Curve
  ctx.strokeStyle = '#ef4444';
  ctx.lineWidth = 2;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(40, 40);
  ctx.quadraticCurveTo(150, 170, 560, 190);
  ctx.stroke();
  ctx.setLineDash([]);

  // Rehearsed & Consolidated Curve (Scaffolded)
  ctx.strokeStyle = '#22c55e';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(40, 40);
  ctx.quadraticCurveTo(180, 70, 560, 60);
  ctx.stroke();

  ctx.fillStyle = '#22c55e';
  ctx.fillText('Consolidated Skill (Tier 3)', 380, 50);
  ctx.fillStyle = '#ef4444';
  ctx.fillText('Unrehearsed Episode Decay', 340, 180);
}

// --------------------------------------------------------------------------
// Tab 5: Owner Control Plane & Interactive Socket
// --------------------------------------------------------------------------
function initControlPlane() {
  const buttons = {
    RUN: document.getElementById('btn-ctrl-run'),
    SLEEP: document.getElementById('btn-ctrl-sleep'),
    FREEZE: document.getElementById('btn-ctrl-freeze'),
    KILL: document.getElementById('btn-ctrl-kill')
  };

  const stateVal = document.getElementById('control-state-val');
  const indicatorDot = document.querySelector('#control-status-indicator .status-dot');

  Object.keys(buttons).forEach(stateKey => {
    const btn = buttons[stateKey];
    if (!btn) return;

    btn.addEventListener('click', () => {
      Object.values(buttons).forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      if (stateVal) stateVal.textContent = stateKey;
      if (indicatorDot) {
        indicatorDot.className = 'status-dot';
        indicatorDot.classList.add(`dot-${stateKey.toLowerCase()}`);
      }

      if (stateKey === 'FREEZE' || stateKey === 'KILL') {
        alert(`Control plane set to ${stateKey}. Organism will refuse execution downstream. State preserved for audit.`);
      }
    });
  });
}

function initChatSocket() {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send-btn');
  const msgBox = document.getElementById('chat-messages');

  if (!input || !sendBtn || !msgBox) return;

  function handleSend() {
    const text = input.value.trim();
    if (!text) return;

    // User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-msg msg-user';
    userDiv.innerHTML = `<span class="msg-author">Owner</span><p>${escapeHtml(text)}</p>`;
    msgBox.appendChild(userDiv);

    input.value = '';
    msgBox.scrollTop = msgBox.scrollHeight;

    // Organism Simulated Grounded Response
    setTimeout(() => {
      const orgDiv = document.createElement('div');
      orgDiv.className = 'chat-msg msg-organism';
      const responseText = generateOrganismReply(text);
      orgDiv.innerHTML = `<span class="msg-author">Ahadu (Organism)</span><p>${responseText}</p>`;
      msgBox.appendChild(orgDiv);
      msgBox.scrollTop = msgBox.scrollHeight;
    }, 600);
  }

  sendBtn.addEventListener('click', handleSend);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  function generateOrganismReply(query) {
    const q = query.toLowerCase();
    if (q.includes('notice') || q.includes('today') || q.includes('see')) {
      return `Today during beat 3 (SENSE & PERCEIVE), I scanned 330 loci. Based on your standing interest <strong>sunglasses-export (1.0)</strong>, I noticed <code>sunglasses-designer-clearance</code> priced at $11.00 (+3.14 scene z-score surprise). Shortlisted 9 items to memory.`;
    }
    if (q.includes('skill') || q.includes('learn') || q.includes('mind')) {
      return `Scaffold summary: 378 episodes processed across 3 distinct days. Promoted 1 primary skill: <em>"Require +20% delivery buffer for optics suppliers in Q4"</em> (support: 14 episodes).`;
    }
    if (q.includes('immune') || q.includes('crispr') || q.includes('attack')) {
      return `CRISPR array holds 11 spacers. MinHash shingle matching cut 5 destructive filesystem attempts and 4 operator concealment payloads. Hostile admission rate is 0.0%.`;
    }
    return `Recorded observation for query "${escapeHtml(query)}". Evaluated against attention field (interests: 10). Memory state preserved in SQLite <code>genome/culture.db</code> under owner kill switch.`;
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
  }
}
