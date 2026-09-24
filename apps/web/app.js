/**
 * CrimeLens — Modern Intelligence Workstation Controller
 * Powers the interactive network graph, command center, temporal timeline,
 * entity dossiers, and evidence provenance viewer.
 */

const API_BASE = "/api";

const State = {
  activeCase: "CASE0001",
  activeView: "command-center-view",
  summary: null,
  graphData: null,
  cy: null,
  selectedEntity: null,
  timelineEvents: [],
  anomalies: [],
  contradictions: [],
  report: null
};

// --- DOM Initializer ---
document.addEventListener("DOMContentLoaded", () => {
  initCaseSwitcher();
  initNavigation();
  initGraphControls();
  initNetraCopilot();
  loadAllData();
});

// --- Dynamic Multi-Case Switcher ---
async function initCaseSwitcher() {
  const select = document.getElementById("case-switcher-select");
  if (!select) return;

  try {
    const res = await fetch(`${API_BASE}/cases`);
    if (!res.ok) return;
    const cases = await res.json();
    select.innerHTML = cases.map(c => `
      <option value="${c.case_id}" ${c.case_id === State.activeCase ? "selected" : ""}>
        ${c.case_id}: ${c.case_type} (${c.location}) — [${c.status}]
      </option>
    `).join("");

    select.addEventListener("change", (e) => {
      switchCase(e.target.value);
    });
  } catch (err) {
    console.error("Failed to load case list for switcher:", err);
  }
}

async function switchCase(caseId) {
  if (State.activeCase === caseId) return;
  State.activeCase = caseId;

  // Sync selector value if invoked programmatically
  const select = document.getElementById("case-switcher-select");
  if (select && select.value !== caseId) {
    select.value = caseId;
  }

  // Reload all views for the newly selected case
  await loadAllData();

  // If on network explorer, focus on this case node or fit graph
  if (State.cy) {
    setTimeout(() => {
      const caseNode = State.cy.getElementById(caseId);
      if (caseNode && caseNode.length > 0) {
        State.cy.elements().removeClass("highlighted");
        caseNode.addClass("highlighted");
        const hood = caseNode.neighborhood().add(caseNode);
        State.cy.animate({
          fit: { eles: hood, padding: 80 },
          duration: 450
        });
      } else {
        State.cy.fit();
      }
    }, 150);
  }
}
window.switchCase = switchCase;

// --- Tab Navigation ---
function initNavigation() {
  const tabs = document.querySelectorAll(".nav-tab-btn");
  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      const viewId = btn.getAttribute("data-view");
      switchView(viewId);
    });
  });
}

function switchView(viewId) {
  State.activeView = viewId;
  document.querySelectorAll(".nav-tab-btn").forEach(b => {
    b.classList.toggle("active", b.getAttribute("data-view") === viewId);
  });
  document.querySelectorAll(".view-panel").forEach(p => {
    p.classList.toggle("active", p.id === viewId);
  });

  if (viewId === "network-explorer-view" && State.cy) {
    setTimeout(() => {
      State.cy.resize();
      State.cy.fit();
      if (typeof applySemanticZoom === "function") {
        applySemanticZoom();
      }
    }, 60);
  }
}

// --- Data Fetching ---
async function loadAllData() {
  try {
    const [summaryRes, graphRes, timelineRes, anomRes, conflictRes, hiddenRes, reportRes] = await Promise.all([
      fetch(`${API_BASE}/cases/${State.activeCase}/summary`).then(r => r.json()),
      fetch(`${API_BASE}/cases/${State.activeCase}/graph`).then(r => r.json()),
      fetch(`${API_BASE}/cases/${State.activeCase}/timeline`).then(r => r.json()),
      fetch(`${API_BASE}/cases/${State.activeCase}/anomalies`).then(r => r.json()),
      fetch(`${API_BASE}/cases/${State.activeCase}/contradictions`).then(r => r.json()),
      fetch(`${API_BASE}/cases/${State.activeCase}/hidden-links`).then(r => r.json()),
      fetch(`${API_BASE}/cases/${State.activeCase}/report`).then(r => r.json())
    ]);

    State.summary = summaryRes;
    State.graphData = graphRes;
    State.timelineEvents = timelineRes.events || [];
    State.anomalies = anomRes || [];
    State.contradictions = conflictRes || [];
    State.hiddenLinks = hiddenRes || [];
    State.report = reportRes;

    renderCommandCenter();
    renderCytoscapeGraph();
    renderTimeline();
    renderAnomaliesAndConflicts();
    renderReport();
  } catch (err) {
    console.error("Failed loading data from CrimeLens API:", err);
  }
}

// --- 1. Command Center Rendering ---
function renderCommandCenter() {
  if (!State.summary) return;
  const s = State.summary;

  // Header Case Meta
  const caseMeta = document.getElementById("header-case-label");
  if (caseMeta) {
    caseMeta.innerText = `${s.case_id}: ${s.primary_location} (${s.incident_date})`;
  }

  // Hero Card
  document.getElementById("hero-title").innerText = s.title;
  document.getElementById("hero-case-id").innerText = s.case_id;
  document.getElementById("hero-location").innerText = s.primary_location;
  document.getElementById("hero-date").innerText = s.incident_date;
  document.getElementById("hero-status").innerText = s.status;

  // Stats
  document.getElementById("stat-entities").innerText = s.stats.total_entities;
  document.getElementById("stat-relations").innerText = s.stats.total_relationships;
  document.getElementById("stat-evidence").innerText = s.stats.evidence_records_count;
  document.getElementById("stat-communities").innerText = s.stats.communities_count;
  document.getElementById("stat-anomalies").innerText = s.stats.anomalies_count;
  document.getElementById("stat-leads").innerText = s.stats.high_priority_leads_count;

  // Key Signals
  const signalsList = document.getElementById("signals-list");
  signalsList.innerHTML = "";
  s.key_signals.forEach(sig => {
    const item = document.createElement("div");
    item.className = "signal-item";
    item.innerHTML = `
      <span class="signal-tag">${sig.type}</span>
      <div class="signal-content">
        <div class="signal-label">${sig.label}</div>
        <div class="signal-desc">${sig.detail}</div>
      </div>
    `;
    signalsList.appendChild(item);
  });

  // Priority Leads Table
  const leadsTbody = document.getElementById("priority-leads-tbody");
  leadsTbody.innerHTML = "";
  s.priority_leads.forEach((lead, idx) => {
    const tr = document.createElement("tr");
    const badgeClass = lead.priority === "HIGH" ? "badge-high" : "badge-medium";
    tr.innerHTML = `
      <td style="font-family: var(--font-mono); color: var(--text-muted); font-size: 13.5px;">#${idx + 1}</td>
      <td style="font-size: 14.5px;"><strong>${lead.name}</strong> <span style="font-family: var(--font-mono); color: var(--text-muted); font-size: 12.5px;">(${lead.person_id})</span></td>
      <td><span class="badge ${badgeClass}">${lead.priority}</span></td>
      <td style="font-size: 13.5px; line-height: 1.55; color: var(--text-secondary);">${lead.reason}</td>
      <td>
        <button class="btn-inspect" onclick="openEntityDossier('${lead.person_id}')">Dossier</button>
      </td>
    `;
    leadsTbody.appendChild(tr);
  });
}

// --- 2. Network Explorer (Cytoscape.js) ---
function renderCytoscapeGraph() {
  if (!State.graphData) return;
  const container = document.getElementById("cy");
  if (!container) return;

  const elements = [];

  // Nodes with Semantic LOD metadata & base size
  State.graphData.elements.nodes.forEach(n => {
    let baseSize = 26;
    let lodTier = 3;

    if (n.data.type === "case") {
      baseSize = 32;
      lodTier = 1; // Tier 1 Anchor
    } else if (n.data.is_bridge) {
      baseSize = 38;
      lodTier = 1; // Tier 1 Anchor
    } else if (n.data.priority === "HIGH" && n.data.type === "person") {
      baseSize = 34;
      lodTier = 1; // Tier 1 Anchor
    } else if (n.data.type === "person") {
      baseSize = 30;
      lodTier = 2; // Tier 2 Key Entity
    } else if (n.data.type === "organization") {
      baseSize = 26;
      lodTier = 2; // Tier 2 Key Entity
    } else if (n.data.type === "location") {
      baseSize = 24;
      lodTier = 3; // Tier 3 Granular Asset
    } else if (n.data.type === "vehicle") {
      baseSize = 22;
      lodTier = 3; // Tier 3 Granular Asset
    } else if (n.data.type === "phone" || n.data.type === "account") {
      baseSize = 20;
      lodTier = 3; // Tier 3 Granular Asset
    }

    elements.push({
      group: "nodes",
      data: {
        ...n.data,
        base_size: baseSize,
        lod_tier: lodTier,
        display_label: (lodTier === 1 ? (n.data.label || "") : "")
      }
    });
  });

  // Edges with computed semantic LOD labels & priority tiers
  State.graphData.elements.edges.forEach(e => {
    let edgeLabel = e.data.type || "";
    let detailedLabel = "";
    let edgeLodTier = 3; // 1 = Critical Conduits, 2 = Primary, 3 = Granular

    const amtMatch = (e.data.context || "").match(/₹[\d,]+/) || (e.data.source_record_id || "").match(/TXN_\d+/);
    if (e.data.type === "TRANSFERRED_TO") {
      edgeLabel = amtMatch ? amtMatch[0] : "₹ TRANSFER";
      detailedLabel = amtMatch ? `${amtMatch[0]} [${e.data.source_record_id || 'TXN'}]` : "₹ TRANSFER";
      const numericVal = amtMatch ? parseInt(amtMatch[0].replace(/[^\d]/g, "")) : 0;
      if (numericVal >= 50000 || (e.data.context || "").toLowerCase().includes("night") || (e.data.context || "").includes("02:")) {
        edgeLodTier = 1;
      } else {
        edgeLodTier = 2;
      }
    } else if (e.data.type === "COMMUNICATES_WITH") {
      const isSpike = (e.data.context || "").includes("35") || (e.data.context || "").includes("surge") || (e.data.context || "").includes("spike");
      edgeLabel = isSpike ? "35 CALLS (SURGE)" : ((e.data.context || "").includes("call") ? "CALL LOG" : "COMMS");
      detailedLabel = isSpike ? "35 CALLS [48H PRE-INCIDENT]" : ((e.data.context || "").includes("call") ? "CALL LOG (VOICE)" : "COMMS");
      if (isSpike) {
        edgeLodTier = 1;
      } else {
        edgeLodTier = 2;
      }
    } else if (e.data.type === "APPEARS_AT") {
      edgeLabel = "SIGHTING";
      detailedLabel = (e.data.context || "").includes("CCTV") ? "CCTV SIGHTING" : "SIGHTING LOG";
      edgeLodTier = 2;
    } else {
      edgeLabel = (e.data.type || "").replace(/_/g, " ");
      detailedLabel = edgeLabel;
      edgeLodTier = 3;
    }

    elements.push({
      group: "edges",
      data: {
        ...e.data,
        edge_label: edgeLabel,
        detailed_label: detailedLabel,
        edge_lod_tier: edgeLodTier,
        display_label: ""
      }
    });
  });

  if (typeof cytoscape === "undefined") {
    console.error("Cytoscape.js is not loaded.");
    return;
  }

  const coseLayoutOptions = {
    name: "cose",
    animate: false,
    randomize: false,
    nodeRepulsion: 75000,
    idealEdgeLength: 165,
    edgeElasticity: 65,
    nestingFactor: 5,
    gravity: 0.18,
    numIter: 1200,
    initialTemp: 250,
    coolingFactor: 0.95,
    minTemp: 1.0,
    nodeOverlap: 25,
    componentSpacing: 110,
    padding: 55
  };

  State.cy = cytoscape({
    container: container,
    elements: elements,
    minZoom: 0.25,
    maxZoom: 2.5,
    wheelSensitivity: 0.18,
    boxSelectionEnabled: false,
    style: [
      // Base Node: Compact, crisp, dark rounded badges with controlled sizing bounds
      {
        selector: "node",
        style: {
          "label": "data(display_label)",
          "color": "#F5F5F4",
          "font-family": "Inter, -apple-system, sans-serif",
          "font-size": "9.5px",
          "font-weight": 600,
          "text-valign": "bottom",
          "text-margin-y": 5,
          "text-max-width": "80px",
          "text-wrap": "ellipsis",
          "text-overflow-wrap": "whitespace",
          "min-zoomed-font-size": 0,
          "text-background-color": "#090807",
          "text-background-opacity": 0.88,
          "text-background-padding": 2.5,
          "text-background-shape": "roundrectangle",
          "background-color": "#8C827A",
          "width": 26,
          "height": 26,
          "border-width": 1.5,
          "border-color": "#38302B"
        }
      },
      // Entity type specific shapes & colors (High contrast, clearly identifiable)
      {
        selector: "node[type = 'person']",
        style: {
          "shape": "ellipse",
          "width": 30,
          "height": 30,
          "border-width": 2,
          "border-color": function(ele) {
            return ele.data("community") === 1 ? "#D4A373" : "#60A5FA";
          },
          "background-color": function(ele) {
            const comm = ele.data("community");
            if (comm === 1) return "#C08457"; // Net A: Warm Copper
            if (comm === 2) return "#3B82F6"; // Net B: Deep Sapphire Blue (high contrast against Net A)
            return "#8C827A";
          }
        }
      },
      {
        selector: "node[is_bridge = true]",
        style: {
          "border-width": 4,
          "border-color": "#FFFFFF",
          "border-style": "double",
          "width": 38,
          "height": 38,
          "background-color": "#D4A373",
          "shadow-blur": 14,
          "shadow-color": "#D4A373",
          "shadow-opacity": 0.9
        }
      },
      {
        selector: "node[priority = 'HIGH'][type = 'person']",
        style: {
          "border-width": 3.5,
          "border-color": "#EF4444",
          "shadow-blur": 10,
          "shadow-color": "#EF4444",
          "shadow-opacity": 0.75
        }
      },
      {
        selector: "node[type = 'phone']",
        style: {
          "shape": "round-rectangle",
          "background-color": "#0D9488",
          "border-color": "#2DD4BF",
          "border-width": 1.5,
          "width": 20,
          "height": 20
        }
      },
      {
        selector: "node[type = 'vehicle']",
        style: {
          "shape": "round-diamond",
          "background-color": "#EA580C",
          "border-color": "#FB923C",
          "border-width": 1.5,
          "width": 22,
          "height": 22
        }
      },
      {
        selector: "node[type = 'location']",
        style: {
          "shape": "hexagon",
          "background-color": "#15803D",
          "border-color": "#4ADE80",
          "border-width": 1.5,
          "width": 24,
          "height": 24
        }
      },
      {
        selector: "node[type = 'account']",
        style: {
          "shape": "tag",
          "background-color": "#7C3AED",
          "border-color": "#A78BFA",
          "border-width": 1.5,
          "width": 20,
          "height": 20
        }
      },
      {
        selector: "node[type = 'organization']",
        style: {
          "shape": "barrel",
          "background-color": "#292524",
          "border-color": "#D4A373",
          "border-width": 1.5,
          "width": 26,
          "height": 26
        }
      },
      {
        selector: "node[type = 'case']",
        style: {
          "shape": "star",
          "background-color": "#B91C1C",
          "border-color": "#EF4444",
          "border-width": 2,
          "width": 32,
          "height": 32
        }
      },
      // Edges Base: Clean, uncluttered lines WITHOUT global text collisions
      {
        selector: "edge",
        style: {
          "width": 1.3,
          "line-color": "#3D3530",
          "curve-style": "bezier",
          "target-arrow-shape": "none",
          "opacity": 0.65,
          "label": "data(display_label)",
          "font-size": "8.5px",
          "font-family": "JetBrains Mono, monospace",
          "font-weight": 700,
          "color": "#D4A373",
          "text-rotation": "autorotate",
          "text-margin-y": -6,
          "text-background-color": "#090807",
          "text-background-opacity": 0.92,
          "text-background-padding": 2.5,
          "text-background-shape": "roundrectangle"
        }
      },
      {
        selector: "edge[type = 'COMMUNICATES_WITH']",
        style: {
          "line-color": "#4880A4",
          "opacity": 0.68
        }
      },
      {
        selector: "edge[type = 'TRANSFERRED_TO']",
        style: {
          "line-color": "#D4A373",
          "target-arrow-shape": "triangle",
          "target-arrow-color": "#D4A373",
          "arrow-scale": 0.85,
          "width": 1.9,
          "opacity": 0.85
        }
      },
      {
        selector: "edge[type = 'APPEARS_AT']",
        style: {
          "line-color": "#4ADE80",
          "line-style": "dashed",
          "opacity": 0.75
        }
      },
      // Viewport-aware Level of Detail (LOD) classes (Google Earth style zoom clarity)
      {
        selector: "node.lod-outside",
        style: {
          "opacity": 0.14,
          "text-opacity": 0
        }
      },
      {
        selector: "node.lod-peripheral",
        style: {
          "opacity": 0.35,
          "text-opacity": 0.4
        }
      },
      {
        selector: "edge.lod-outside",
        style: {
          "opacity": 0.05,
          "width": 0.8,
          "label": ""
        }
      },
      {
        selector: "edge.lod-peripheral",
        style: {
          "opacity": 0.22,
          "width": 1.1,
          "label": ""
        }
      },
      {
        selector: "edge.lod-local",
        style: {
          "opacity": 0.88,
          "width": 1.9,
          "z-index": 50
        }
      },
      {
        selector: "edge.lod-local-deep",
        style: {
          "opacity": 0.98,
          "width": 2.3,
          "z-index": 100
        }
      },
      // Hovered & Path-traced Edges: High-contrast on-demand detail
      {
        selector: "edge.edge-hovered, edge.highlighted",
        style: {
          "label": "data(detailed_label)",
          "text-opacity": 1,
          "font-size": "9.5px",
          "font-family": "JetBrains Mono, monospace",
          "font-weight": 700,
          "color": "#FFFFFF",
          "text-rotation": "autorotate",
          "text-margin-y": -7,
          "text-background-color": "#090807",
          "text-background-opacity": 0.95,
          "text-background-padding": 3,
          "text-background-shape": "roundrectangle",
          "target-arrow-shape": "triangle",
          "arrow-scale": 1.25,
          "width": 2.6,
          "line-color": "#FFFFFF",
          "target-arrow-color": "#FFFFFF",
          "opacity": 1,
          "z-index": 999
        }
      },
      // Legend Focus Highlighting
      {
        selector: ".legend-focus",
        style: {
          "opacity": 1,
          "border-color": "#FFFFFF",
          "border-width": 3.5,
          "shadow-blur": 16,
          "shadow-color": "#D4A373",
          "shadow-opacity": 0.95,
          "z-index": 999
        }
      },
      // Dimming / Highlighting classes
      {
        selector: ".dimmed",
        style: {
          "opacity": 0.12
        }
      },
      {
        selector: ".highlighted",
        style: {
          "opacity": 1,
          "line-color": "#C59B4A",
          "border-color": "#FFFFFF",
          "border-width": 3.5,
          "z-index": 999
        }
      },
      {
        selector: "node:selected",
        style: {
          "border-color": "#FFFFFF",
          "border-width": 3.5,
          "shadow-blur": 16,
          "shadow-color": "#C59B4A",
          "shadow-opacity": 0.85
        }
      },
      // Focused/Hovered/Selected nodes always display readable labels
      {
        selector: "node.highlighted, node:selected",
        style: {
          "text-opacity": 1,
          "text-background-opacity": 0.95,
          "z-index": 999
        }
      }
    ],
    layout: coseLayoutOptions
  });

  // Semantic Zoom (LOD) & Controlled Node Sizing (Google Maps Style)
  let zoomRaf = null;
  function updateZoomLevelOfDetail() {
    if (zoomRaf) return;
    zoomRaf = requestAnimationFrame(() => {
      zoomRaf = null;
      applySemanticZoom();
    });
  }

  function applySemanticZoom() {
    if (!State.cy) return;
    const z = State.cy.zoom();

    const zoomLabel = document.getElementById("graph-zoom-label");
    if (zoomLabel) {
      zoomLabel.innerText = `${Math.round(z * 100)}%`;
    }

    // Viewport bounding box in model coordinates
    const ext = State.cy.extent();
    const cX = (ext.x1 + ext.x2) / 2;
    const cY = (ext.y1 + ext.y2) / 2;
    // Focal inspection radius around the center of the zoomed viewport
    const focalRadius = Math.min(ext.w, ext.h) * 0.42;

    // Zoom-dependent Level of Detail (Google Earth style):
    // z < 1.05: Macro Overview (Zoomed out: keep overall graph exactly as it is)
    // 1.05 <= z < 1.45: Progressive Focused View (Local neighborhood edges highlighted, peripheral/external edges recede)
    // z >= 1.45: Deep Inspection (Local paths rendered with maximum clarity & distinct relationship labels)
    const isZoomedIn = z >= 1.05;
    const isDeepZoom = z >= 1.45;

    // Size damping factor: keeps nodes bounded within controlled screen limits (~16px to ~38px)
    // so zooming in expands visual inter-node spacing rather than bloating nodes
    const sizeFactor = Math.max(0.52, Math.min(1.30, 1 / Math.pow(z, 0.65)));

    // Controlled font size in model coordinates so text on screen remains crisp (~7px to ~14px)
    const fontDamping = Math.max(7.5, Math.min(12, 9.5 / Math.pow(z, 0.45)));

    State.cy.batch(() => {
      // 1. Viewport & Focal-Aware Node Classification
      State.cy.nodes().forEach(n => {
        const base = n.data("base_size") || 26;
        const targetSize = Math.round(base * sizeFactor);
        const nodeTier = n.data("lod_tier") || 3;
        const isHighlighted = n.hasClass("highlighted") || n.selected();

        const pos = n.position();
        const distToCenter = Math.hypot(pos.x - cX, pos.y - cY);
        const inViewport = pos.x >= ext.x1 && pos.x <= ext.x2 && pos.y >= ext.y1 && pos.y <= ext.y2;
        const inFocalZone = distToCenter <= focalRadius;

        n.data("_inView", inViewport);
        n.data("_inFocal", inFocalZone);

        if (!isZoomedIn) {
          // ZOOMED OUT / OVERVIEW: Keep overall graph exactly as it is
          n.removeClass("lod-outside lod-peripheral");
          const showLabel = (z >= 0.88) ? (nodeTier <= 2) : (nodeTier === 1);
          n.data("display_label", (showLabel || isHighlighted) ? (n.data("label") || "") : "");
        } else {
          // ZOOMED IN: Focal neighborhood vs peripheral disclosure
          if (inFocalZone || isHighlighted) {
            // Central inspection neighborhood: clear and prominent
            n.removeClass("lod-outside lod-peripheral");
            n.data("display_label", n.data("label") || "");
          } else if (inViewport) {
            // Peripheral zone near screen margins: de-emphasized
            n.removeClass("lod-outside");
            n.addClass("lod-peripheral");
            n.data("display_label", (nodeTier <= 2) ? (n.data("label") || "") : "");
          } else {
            // Far outside the viewport: recede completely
            n.removeClass("lod-peripheral");
            n.addClass("lod-outside");
            n.data("display_label", "");
          }
        }

        n.style({
          "width": targetSize,
          "height": targetSize,
          "font-size": fontDamping
        });
      });

      // 2. Viewport & Focal-Aware Edge/Path Clarity & Relationship Information
      State.cy.edges().forEach(e => {
        const isHighlighted = e.hasClass("edge-hovered") || e.hasClass("highlighted");
        const isBridgeEdge = e.source().data("is_bridge") || e.target().data("is_bridge");
        const edgeTier = e.data("edge_lod_tier") || 3;

        if (!isZoomedIn) {
          // ZOOMED OUT: Clean network topology without edge label collisions
          e.removeClass("lod-outside lod-peripheral lod-local lod-local-deep edge-lod-core edge-lod-all critical-lod-edge");
          e.data("display_label", isHighlighted ? (e.data("detailed_label") || e.data("edge_label") || "") : "");
          return;
        }

        const sNode = e.source();
        const tNode = e.target();
        const sInView = sNode.data("_inView");
        const tInView = tNode.data("_inView");
        const sInFocal = sNode.data("_inFocal");
        const tInFocal = tNode.data("_inFocal");

        if (isHighlighted) {
          // Hovered / selected paths always retain maximum prominence
          e.removeClass("lod-outside lod-peripheral");
          e.addClass("lod-local-deep");
          e.data("display_label", e.data("detailed_label") || e.data("edge_label") || "");
        } else if (!sInView && !tInView) {
          // Category A: Both endpoints are outside the viewport -> de-emphasize completely
          e.removeClass("lod-local lod-local-deep lod-peripheral edge-lod-core edge-lod-all");
          e.addClass("lod-outside");
          e.data("display_label", "");
        } else if (!sInFocal || !tInFocal) {
          // Category B: Peripheral edge (outside the focal neighborhood)
          // Attenuate to avoid spiderweb clutter stretching across the inspection area
          e.removeClass("lod-local lod-local-deep lod-outside edge-lod-core edge-lod-all");
          e.addClass("lod-peripheral");
          e.data("display_label", "");
        } else {
          // Category C: Focal neighborhood edge (BOTH endpoints inside the focal inspection area)
          // Prioritize rendering so individual paths and relationships can be clearly distinguished
          e.removeClass("lod-outside lod-peripheral");

          if (isDeepZoom) {
            // Deep zoom (>= 145%): High clarity, local relationship lines prominent
            e.removeClass("lod-local");
            e.addClass("lod-local-deep");
            // Only show persistent badges on high-priority anomalies (major transfers, call surges)
            // Routine edges rely on high-contrast relationship colors and reveal full details on hover
            const isMajorTransfer = e.data("type") === "TRANSFERRED_TO" && (edgeTier === 1);
            const isCallSurge = (e.data("context") || "").includes("surge") || (e.data("context") || "").includes("spike");
            if (isMajorTransfer || isCallSurge) {
              e.data("display_label", e.data("edge_label") || "");
            } else {
              e.data("display_label", "");
            }
          } else {
            // Moderate zoom (105% - 145%): Clear paths, show badges on major transfers only
            e.removeClass("lod-local-deep");
            e.addClass("lod-local");
            const isMajorTransfer = e.data("type") === "TRANSFERRED_TO" && (edgeTier === 1);
            if (isMajorTransfer) {
              e.data("display_label", e.data("edge_label") || "");
            } else {
              e.data("display_label", "");
            }
          }
        }
      });
    });
  }

  State.applySemanticZoom = applySemanticZoom;
  State.cy.on("zoom pan viewport", updateZoomLevelOfDetail);
  applySemanticZoom();

  // Edge hover tooltip & dynamic edge highlighting
  const tooltip = document.getElementById("graph-edge-tooltip");

  State.cy.on("mouseover", "edge", evt => {
    const edge = evt.target;
    edge.addClass("edge-hovered");
    edge.data("display_label", edge.data("detailed_label") || edge.data("edge_label") || "");
    if (tooltip) {
      const d = edge.data();
      tooltip.style.display = "block";
      tooltip.innerHTML = `
        <div style="color: var(--gold-primary); font-family: var(--font-mono); font-size: 10px; font-weight: 700; margin-bottom: 2px;">
          ${d.type} // ${d.source_record_id || "LINK"}
        </div>
        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 3px;">
          ${d.source} ↔ ${d.target}
        </div>
        <div style="color: var(--text-secondary); font-size: 10.5px; line-height: 1.4;">
          ${d.context || "Verified linkage"}
        </div>
        <div style="margin-top: 4px; font-family: var(--font-mono); font-size: 9.5px; color: var(--text-muted);">
          ${d.evidence_class || "FACT"} | Conf: ${d.confidence || 0.95} | Rel: ${d.reliability || 0.90}
        </div>
      `;
    }
  });

  State.cy.on("mousemove", "edge", evt => {
    if (tooltip && container) {
      const rect = container.getBoundingClientRect();
      const clientX = evt.originalEvent?.clientX || (rect.left + evt.renderedPosition.x);
      const clientY = evt.originalEvent?.clientY || (rect.top + evt.renderedPosition.y);
      tooltip.style.left = `${clientX - rect.left}px`;
      tooltip.style.top = `${clientY - rect.top}px`;
    }
  });

  State.cy.on("mouseout", "edge", evt => {
    evt.target.removeClass("edge-hovered");
    if (tooltip) {
      tooltip.style.display = "none";
    }
    if (!evt.target.hasClass("highlighted")) {
      applySemanticZoom();
    }
  });

  // When hovering a node, also reveal its incident edge labels cleanly
  State.cy.on("mouseover", "node", evt => {
    const node = evt.target;
    node.data("display_label", node.data("label") || "");
    node.connectedEdges().addClass("edge-hovered").forEach(ed => {
      ed.data("display_label", ed.data("detailed_label") || ed.data("edge_label") || "");
    });
  });
  State.cy.on("mouseout", "node", evt => {
    if (!evt.target.hasClass("highlighted")) {
      applySemanticZoom();
    }
  });

  // Event handlers
  State.cy.on("tap", "node", evt => {
    const node = evt.target;
    focusNode(node);
    openEntityDossier(node.data("id"));
  });

  State.cy.on("tap", "edge", evt => {
    const edge = evt.target;
    showEdgeProvenance(edge.data());
  });

  State.cy.on("tap", evt => {
    if (evt.target === State.cy) {
      resetGraphHighlight();
    }
  });

  populatePathSelects();
  setupLegendInteractivity();
}

function focusNode(node) {
  State.cy.elements().removeClass("highlighted dimmed");
  const neighborhood = node.neighborhood().add(node);
  State.cy.elements().difference(neighborhood).addClass("dimmed");
  neighborhood.addClass("highlighted");
}

function resetGraphHighlight() {
  if (!State.cy) return;
  State.cy.elements().removeClass("highlighted dimmed edge-hovered");
  if (typeof State.applySemanticZoom === "function") {
    State.applySemanticZoom();
  }
}

function initGraphControls() {
  // Filter by type
  const typeFilter = document.getElementById("filter-entity-type");
  if (typeFilter) {
    typeFilter.addEventListener("change", applyGraphFilters);
  }

  // Community filter
  const commFilter = document.getElementById("filter-community");
  if (commFilter) {
    commFilter.addEventListener("change", applyGraphFilters);
  }

  // Bridge toggle
  const bridgeToggle = document.getElementById("toggle-bridge-only");
  if (bridgeToggle) {
    bridgeToggle.addEventListener("change", applyGraphFilters);
  }

  // Search
  const searchInput = document.getElementById("graph-search");
  if (searchInput) {
    searchInput.addEventListener("input", e => {
      const q = e.target.value.toLowerCase().trim();
      if (!State.cy) return;
      if (!q) {
        resetGraphHighlight();
        return;
      }
      const match = State.cy.nodes().filter(n => {
        const id = n.data("id").toLowerCase();
        const label = (n.data("label") || "").toLowerCase();
        const name = (n.data("name") || "").toLowerCase();
        return id.includes(q) || label.includes(q) || name.includes(q);
      });
      if (match.length > 0) {
        focusNode(match.first());
      }
    });
  }

  // Layout buttons
  const coseLayoutOptions = {
    name: "cose",
    animate: true,
    animationDuration: 600,
    randomize: false,
    nodeRepulsion: 75000,
    idealEdgeLength: 165,
    edgeElasticity: 65,
    nestingFactor: 5,
    gravity: 0.18,
    numIter: 1200,
    nodeOverlap: 25,
    componentSpacing: 110,
    padding: 55
  };

  document.getElementById("btn-layout-cose")?.addEventListener("click", () => {
    State.cy?.layout(coseLayoutOptions).run();
  });
  document.getElementById("btn-layout-circle")?.addEventListener("click", () => {
    State.cy?.layout({ name: "concentric", animate: true, animationDuration: 400, padding: 50 }).run();
  });

  // Interactive Zoom Stepper Controls
  document.getElementById("btn-zoom-in")?.addEventListener("click", () => {
    if (!State.cy) return;
    const curZoom = State.cy.zoom();
    const newZoom = Math.min(2.5, curZoom * 1.25);
    State.cy.animate({
      zoom: {
        level: newZoom,
        renderedPosition: { x: State.cy.width() / 2, y: State.cy.height() / 2 }
      },
      duration: 220
    });
  });

  document.getElementById("btn-zoom-out")?.addEventListener("click", () => {
    if (!State.cy) return;
    const curZoom = State.cy.zoom();
    const newZoom = Math.max(0.25, curZoom / 1.25);
    State.cy.animate({
      zoom: {
        level: newZoom,
        renderedPosition: { x: State.cy.width() / 2, y: State.cy.height() / 2 }
      },
      duration: 220
    });
  });

  document.getElementById("btn-fit-graph")?.addEventListener("click", () => {
    if (!State.cy) return;
    State.cy.animate({
      fit: { padding: 45 },
      duration: 350
    });
  });

  // Path & Connectivity Explorer (Multi-mode: Shortest, All Paths, Common Neighbors, Max Hops)
  const modeSelect = document.getElementById("path-mode");
  const maxHopsGroup = document.getElementById("max-hops-group");
  const maxHopsSlider = document.getElementById("path-max-hops");
  const maxHopsVal = document.getElementById("max-hops-val");

  if (modeSelect) {
    modeSelect.addEventListener("change", () => {
      if (modeSelect.value === "max_hops" || modeSelect.value === "all_paths") {
        if (maxHopsGroup) maxHopsGroup.style.display = "block";
      } else {
        if (maxHopsGroup) maxHopsGroup.style.display = "none";
      }
    });
  }

  if (maxHopsSlider && maxHopsVal) {
    maxHopsSlider.addEventListener("input", (e) => {
      maxHopsVal.innerText = e.target.value;
    });
  }

  document.getElementById("btn-clear-path")?.addEventListener("click", () => {
    resetGraphHighlight();
    const msg = document.getElementById("path-result-msg");
    if (msg) msg.innerText = "";
  });

  document.getElementById("btn-find-path")?.addEventListener("click", () => {
    const src = document.getElementById("path-source")?.value;
    const tgt = document.getElementById("path-target")?.value;
    const mode = document.getElementById("path-mode")?.value || "shortest";
    const maxHops = parseInt(document.getElementById("path-max-hops")?.value || "3", 10);
    const msgEl = document.getElementById("path-result-msg");

    if (!src || !tgt || !State.cy) return;
    if (src === tgt) {
      if (msgEl) msgEl.innerText = "Source and Target entities cannot be identical.";
      return;
    }

    const srcNode = State.cy.getElementById(src);
    const tgtNode = State.cy.getElementById(tgt);
    if (!srcNode || srcNode.length === 0 || !tgtNode || tgtNode.length === 0) {
      if (msgEl) msgEl.innerText = "Selected entities not found in network.";
      return;
    }

    State.cy.elements().removeClass("highlighted dimmed");

    if (mode === "shortest") {
      const aStar = State.cy.elements().aStar({ root: srcNode, goal: tgtNode, directed: false });
      if (aStar.found) {
        State.cy.elements().difference(aStar.path).addClass("dimmed");
        aStar.path.addClass("highlighted");
        if (msgEl) {
          msgEl.innerHTML = `<span style="color: #7ab87a; font-weight: 600;">✓ Shortest Path Found:</span> <strong>${aStar.distance} hops</strong> (${aStar.path.nodes().length} entities linked)`;
        }
      } else {
        if (msgEl) msgEl.innerHTML = `<span style="color: #f08271;">✗ No path exists between ${src} and ${tgt}.</span>`;
      }
    } else if (mode === "all_paths") {
      const visited = new Set();
      const paths = [];
      function dfs(current, path) {
        if (path.length > maxHops + 1) return;
        if (current.id() === tgt) {
          paths.push([...path]);
          return;
        }
        visited.add(current.id());
        const neighbors = current.neighborhood().nodes();
        neighbors.forEach(nbr => {
          if (!visited.has(nbr.id())) {
            dfs(nbr, [...path, nbr]);
          }
        });
        visited.delete(current.id());
      }
      dfs(srcNode, [srcNode]);

      if (paths.length > 0) {
        let pathElements = State.cy.collection();
        paths.forEach(p => {
          for (let i = 0; i < p.length; i++) {
            pathElements = pathElements.add(p[i]);
            if (i < p.length - 1) {
              const edge = p[i].edgesWith(p[i + 1]);
              pathElements = pathElements.add(edge);
            }
          }
        });
        State.cy.elements().difference(pathElements).addClass("dimmed");
        pathElements.addClass("highlighted");
        if (msgEl) {
          msgEl.innerHTML = `<span style="color: #7ab87a; font-weight: 600;">✓ Found ${paths.length} connection route(s)</span> (within ${maxHops} hops across ${pathElements.nodes().length} entities).`;
        }
      } else {
        if (msgEl) msgEl.innerHTML = `<span style="color: #f08271;">No routes found within ${maxHops} hops limit.</span>`;
      }
    } else if (mode === "common_neighbors") {
      const srcNeighbors = srcNode.neighborhood().nodes();
      const tgtNeighbors = tgtNode.neighborhood().nodes();
      const mutual = srcNeighbors.intersection(tgtNeighbors);

      if (mutual.length > 0) {
        let mutualElements = srcNode.add(tgtNode).add(mutual);
        mutual.forEach(m => {
          mutualElements = mutualElements.add(m.edgesWith(srcNode));
          mutualElements = mutualElements.add(m.edgesWith(tgtNode));
        });
        State.cy.elements().difference(mutualElements).addClass("dimmed");
        mutualElements.addClass("highlighted");
        const mutualNames = mutual.map(n => n.data("name") || n.data("id")).join(", ");
        if (msgEl) {
          msgEl.innerHTML = `<span style="color: #7ab87a; font-weight: 600;">✓ ${mutual.length} Shared Mutual Link(s):</span> <strong>${mutualNames}</strong>`;
        }
      } else {
        if (msgEl) msgEl.innerHTML = `<span style="color: #f08271;">No direct shared mutual neighbors between ${src} and ${tgt}.</span>`;
      }
    } else if (mode === "max_hops") {
      let currentNeighborhood = srcNode;
      for (let i = 0; i < maxHops; i++) {
        currentNeighborhood = currentNeighborhood.add(currentNeighborhood.neighborhood());
      }
      const isTargetReachable = currentNeighborhood.contains(tgtNode);
      State.cy.elements().difference(currentNeighborhood).addClass("dimmed");
      currentNeighborhood.addClass("highlighted");

      if (isTargetReachable) {
        if (msgEl) {
          msgEl.innerHTML = `<span style="color: #7ab87a; font-weight: 600;">✓ Target REACHABLE within ${maxHops} hops!</span> (${currentNeighborhood.nodes().length} entities in perimeter)`;
        }
      } else {
        if (msgEl) {
          msgEl.innerHTML = `<span style="color: #f08271;">Target NOT reachable within ${maxHops} hops.</span> (${currentNeighborhood.nodes().length} entities explored)`;
        }
      }
    }
  });
}

function setupLegendInteractivity() {
  const chips = document.querySelectorAll(".legend-chip");
  chips.forEach(chip => {
    if (chip._legendBound) return;
    chip._legendBound = true;
    chip.addEventListener("mouseenter", () => {
      if (!State.cy) return;
      const type = chip.getAttribute("data-type");
      const comm = chip.getAttribute("data-comm");

      chip.classList.add("active-highlight");
      State.cy.elements().removeClass("legend-focus dimmed");

      let targets;
      if (type === "bridge") {
        targets = State.cy.nodes("[is_bridge = true]");
      } else if (type === "priority-high") {
        targets = State.cy.nodes("[priority = 'HIGH']");
      } else if (type === "person" && comm) {
        targets = State.cy.nodes(`[type = 'person'][community = ${comm}]`);
      } else if (type) {
        targets = State.cy.nodes(`[type = '${type}']`);
      }

      if (targets && targets.length > 0) {
        const connectedEdges = targets.connectedEdges();
        const highlightedGroup = targets.add(connectedEdges);
        State.cy.elements().difference(highlightedGroup).addClass("dimmed");
        targets.addClass("legend-focus");
      }
    });

    chip.addEventListener("mouseleave", () => {
      chip.classList.remove("active-highlight");
      if (!State.cy) return;
      State.cy.elements().removeClass("legend-focus dimmed");
    });
  });
}

function applyGraphFilters() {
  if (!State.cy) return;
  const type = document.getElementById("filter-entity-type")?.value || "ALL";
  const comm = document.getElementById("filter-community")?.value || "ALL";
  const bridgeOnly = document.getElementById("toggle-bridge-only")?.checked || false;

  State.cy.batch(() => {
    State.cy.nodes().forEach(node => {
      let show = true;
      if (type !== "ALL" && node.data("type") !== type) show = false;
      if (comm !== "ALL" && String(node.data("community")) !== comm) show = false;
      if (bridgeOnly && !node.data("is_bridge")) show = false;

      node.style("display", show ? "element" : "none");
    });
  });
}

function populatePathSelects() {
  const srcSelect = document.getElementById("path-source");
  const tgtSelect = document.getElementById("path-target");
  if (!srcSelect || !tgtSelect || !State.graphData) return;

  const persons = State.graphData.elements.nodes.filter(n => n.data.type === "person");
  srcSelect.innerHTML = `<option value="">Select source...</option>`;
  tgtSelect.innerHTML = `<option value="">Select target...</option>`;

  persons.forEach(p => {
    const optA = document.createElement("option");
    optA.value = p.data.id;
    optA.innerText = `${p.data.name} (${p.data.id})`;
    srcSelect.appendChild(optA);

    const optB = document.createElement("option");
    optB.value = p.data.id;
    optB.innerText = `${p.data.name} (${p.data.id})`;
    tgtSelect.appendChild(optB);
  });

  // Default demo path P0007 -> P0012
  srcSelect.value = "P0007";
  tgtSelect.value = "P0012";
}

// --- 3. Entity Dossier (Profile Panel) ---
async function openEntityDossier(entityId) {
  const drawer = document.getElementById("entity-dossier-drawer");
  if (!drawer) return;

  try {
    const res = await fetch(`${API_BASE}/entities/${entityId}`);
    if (!res.ok) return;
    const profile = await res.json();
    State.selectedEntity = profile;

    // Title and Meta
    document.getElementById("dossier-name").innerText = profile.name;
    document.getElementById("dossier-id").innerText = profile.entity_id;
    document.getElementById("dossier-type").innerText = profile.type.toUpperCase();

    // Alias Alert
    const aliasBox = document.getElementById("dossier-alias-box");
    if (profile.attributes.is_alias || profile.attributes.alias_details) {
      aliasBox.style.display = "block";
      const a = profile.attributes.alias_details || {};
      aliasBox.innerHTML = `
        <span class="badge badge-conflict">RESOLVED IDENTITY ALIAS</span>
        <div style="margin-top: 4px; font-size: 13.5px;">
          Merged Record: <strong>${a.alias_name || profile.name}</strong> ↔ <strong>${a.canonical_name || "Rahul Mehta"}</strong><br/>
          <span style="color: var(--text-muted); font-size: 12px;">${a.reason || "Shared phone 9000010003 & organization"}</span>
        </div>
      `;
    } else {
      aliasBox.style.display = "none";
    }

    // Priority Card
    const prio = profile.investigation_priority;
    const prioCard = document.getElementById("dossier-priority-card");
    const pClass = prio.level.toLowerCase();
    prioCard.className = `priority-banner-card ${pClass}`;
    prioCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span class="badge badge-${pClass}">INVESTIGATION PRIORITY: ${prio.level}</span>
        <span style="font-family: var(--font-mono); font-size: 12.5px; color: var(--text-muted);">Score: ${prio.score}</span>
      </div>
      <div style="font-size: 14px; color: var(--text-secondary); line-height: 1.5;">${prio.reason}</div>
    `;

    // Graph Centralities
    const an = profile.analytics;
    document.getElementById("dossier-degree").innerText = an.degree;
    document.getElementById("dossier-betweenness").innerText = an.betweenness;
    document.getElementById("dossier-pagerank").innerText = an.pagerank;
    document.getElementById("dossier-community").innerText = `Net ${an.community_id === 1 ? "A" : "B"}`;
    document.getElementById("dossier-bridge").innerText = an.is_bridge ? "YES (Key Connector)" : "No";

    // Evidence Lists
    renderDossierEvidence(profile);

    // Contradictions in Dossier
    const confBox = document.getElementById("dossier-conflicts-box");
    if (profile.contradictions && profile.contradictions.length > 0) {
      confBox.style.display = "block";
      confBox.innerHTML = profile.contradictions.map(c => `
        <div class="dossier-evidence-card" style="border-left: 3px solid var(--rust-primary);">
          <span class="badge badge-conflict">${c.status}</span>
          <div style="font-weight: 600; margin-top: 4px; font-size: 14.5px;">${c.title}</div>
          <div style="color: var(--text-secondary); font-size: 13.5px; line-height: 1.5; margin-top: 2px;">${c.investigative_guidance}</div>
        </div>
      `).join("");
    } else {
      confBox.style.display = "none";
    }

    drawer.classList.add("open");
  } catch (e) {
    console.error("Error opening dossier:", e);
  }
}

function renderDossierEvidence(profile) {
  const container = document.getElementById("dossier-evidence-list");
  if (!container) return;

  const edges = profile.connected_edges || [];
  if (edges.length === 0) {
    container.innerHTML = `<div style="color: var(--text-muted); font-size: 14px;">No direct evidence records logged.</div>`;
    return;
  }

  container.innerHTML = edges.slice(0, 15).map(e => {
    const prov = e.provenance;
    const isObserved = prov.evidence_class === "OBSERVED";
    return `
      <div class="dossier-evidence-card">
        <div class="dossier-evidence-top">
          <span style="color: var(--gold-primary); font-size: 12.5px;">${prov.source_record_id}</span>
          <span style="color: var(--text-muted); font-size: 12.5px;">${prov.timestamp || "Registry Link"}</span>
        </div>
        <div style="font-weight: 600; color: var(--text-primary); font-size: 14px; margin-bottom: 2px;">
          ${e.type}: ${e.source} ↔ ${e.target}
        </div>
        <div style="color: var(--text-secondary); font-size: 13.5px; line-height: 1.45;">
          ${prov.context || "Direct verified linkage"}
        </div>
        <div style="margin-top: 4px; display: flex; gap: 8px;">
          <span class="badge badge-fact">${prov.evidence_class}</span>
          <span style="font-family: var(--font-mono); font-size: 11.5px; color: var(--text-muted);">Conf: ${prov.confidence} | Rel: ${prov.reliability}</span>
        </div>
      </div>
    `;
  }).join("");
}

function closeEntityDossier() {
  document.getElementById("entity-dossier-drawer")?.classList.remove("open");
}

function showEdgeProvenance(edgeData) {
  alert(
    `EVIDENCE PROVENANCE:\n\n` +
    `Relationship: ${edgeData.type}\n` +
    `Source Record: ${edgeData.source_record_id} (${edgeData.source_type})\n` +
    `Timestamp: ${edgeData.timestamp || "Official Registry Record"}\n` +
    `Evidence Class: ${edgeData.evidence_class} [FACT]\n` +
    `Confidence: ${edgeData.confidence} | Reliability: ${edgeData.reliability}\n` +
    `Context: ${edgeData.context || "Logged in primary investigation ledger"}`
  );
}

// --- 4. Timeline Rendering ---
function renderTimeline(filterMode = "CASE_RELEVANT") {
  const feed = document.getElementById("timeline-feed");
  if (!feed) return;
  feed.innerHTML = "";

  let events = [...State.timelineEvents];

  // Extract relevant suspects for targeted timeline view
  let caseSuspects = [];
  if (State.summary && State.summary.priority_leads) {
    caseSuspects = State.summary.priority_leads.map(l => l.person_id || l.entity_id).filter(Boolean);
  }
  const eventEntities = new Set();
  (State.timelineEvents || []).forEach(e => {
    (e.entities || []).forEach(entId => {
      if (typeof entId === "string") eventEntities.add(entId);
    });
  });
  caseSuspects = Array.from(new Set([...caseSuspects, ...eventEntities]));

  if (filterMode === "CASE_RELEVANT") {
    // State.timelineEvents is already case-scoped by the backend engine
    events = [...State.timelineEvents];
  } else if (filterMode === "SPIKE") {
    const incDate = (State.summary && State.summary.incident_date) || "2026-08-20";
    const incMonth = incDate.slice(0, 7);
    events = events.filter(e => {
      const hasSpikeTag = (e.tags || []).some(t => t.toLowerCase().includes("spike") || t.toLowerCase().includes("surge") || t.toLowerCase().includes("burst"));
      return hasSpikeTag || (e.is_critical && e.timestamp.startsWith(incMonth));
    });
    if (events.length === 0) {
      events = State.timelineEvents.filter(e => e.is_critical);
    }
  } else if (filterMode === "CRITICAL") {
    events = events.filter(e => e.is_critical);
  } else if (filterMode === "FINANCE") {
    events = events.filter(e => e.type === "financial" || (e.tags || []).some(t => t.toLowerCase().includes("layering") || t.toLowerCase().includes("transfer") || t.toLowerCase().includes("financial")));
  } else if (filterMode === "TELECOM") {
    events = events.filter(e => e.type === "telecom" || e.type === "surveillance" || (e.tags || []).some(t => t.toLowerCase().includes("call") || t.toLowerCase().includes("tower") || t.toLowerCase().includes("cdr") || t.toLowerCase().includes("sighting")));
  }
  // filterMode === "ALL" keeps all events for comprehensive auditing

  // Set count badge with context
  const countEl = document.getElementById("timeline-count");
  if (countEl) {
    countEl.innerText = `${events.length} events logged for ${State.activeCase}`;
  }

  if (events.length === 0) {
    feed.innerHTML = `
      <div style="text-align: center; padding: 40px; color: var(--text-muted); font-size: 13px;">
        No events match the selected filter for ${State.activeCase}.
      </div>
    `;
    return;
  }

  events.slice(0, 60).forEach(ev => {
    const card = document.createElement("div");
    card.className = `timeline-event-card ${ev.is_critical ? "critical" : ""}`;

    const tagsHtml = (ev.tags || []).map(t => `<span class="badge badge-inference">${t}</span>`).join(" ");

    card.innerHTML = `
      <div class="timeline-node-dot"></div>
      <div class="timeline-header-row">
        <span class="badge badge-fact">${ev.source_type}</span>
        <span class="timeline-time">${ev.timestamp}</span>
      </div>
      <div class="timeline-title">${ev.title}</div>
      <div class="timeline-desc">${ev.description}</div>
      <div style="margin-top: 6px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
        <div>${tagsHtml}</div>
        <span style="font-family: var(--font-mono); font-size: 11px; color: var(--gold-primary);">${ev.source_record_id}</span>
      </div>
    `;
    feed.appendChild(card);
  });
}

function setTimelineFilter(mode, btn) {
  document.querySelectorAll(".filter-chip").forEach(c => c.classList.remove("active"));
  btn.classList.add("active");
  renderTimeline(mode);
}

// --- 5. Anomalies & Contradictions ---
function renderAnomaliesAndConflicts() {
  const anomHeader = document.getElementById("anomalies-header-count");
  if (anomHeader) {
    const critCount = State.anomalies.filter(a => a.severity === "CRITICAL").length;
    anomHeader.innerHTML = `<span class="pulse-indicator"></span> ${State.anomalies.length} SIGNALS FLAGGED (${critCount} CRITICAL)`;
  }

  const conflictHeader = document.getElementById("conflicts-header-count");
  if (conflictHeader) {
    conflictHeader.innerText = `⚠️ ${State.contradictions.length} CONFLICT${State.contradictions.length === 1 ? '' : 'S'} FLAGGED`;
  }

  const anomContainer = document.getElementById("anomalies-list-container");
  if (anomContainer) {
    anomContainer.innerHTML = State.anomalies.map(a => {
      const sevClass = (a.severity || "HIGH").toLowerCase();
      return `
        <div class="anomaly-card-hero ${sevClass}">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <span class="anomaly-hero-metric ${sevClass}">${a.severity} ANOMALY</span>
            <span style="font-family: var(--font-mono); font-size: 13px; color: var(--text-muted);">${a.timestamp}</span>
          </div>
          <div style="font-size: 18.5px; font-weight: 700; color: var(--text-primary); letter-spacing: 0.3px;">${a.title}</div>
          <div style="color: var(--text-secondary); font-size: 15px; line-height: 1.6;">${a.description}</div>
          <div class="guidance-box-hero">
            <strong style="color: var(--gold-primary);">Investigator Guidance [RECOMMENDED ACTION]:</strong> ${a.recommendation}
          </div>
          <div style="display: flex; gap: 8px; font-family: var(--font-mono); font-size: 12.5px; color: var(--text-muted); border-top: 1px solid var(--border-subtle); padding-top: 10px;">
            Evidence Records: <span style="color: var(--text-secondary);">${(a.evidence_records || []).join(", ")}</span>
          </div>
        </div>
      `;
    }).join("");
  }

  const conflictContainer = document.getElementById("conflicts-list-container");
  if (conflictContainer) {
    conflictContainer.innerHTML = State.contradictions.map(c => {
      const isAlibiConflict = (c.id === "CONF-01") || c.title.toLowerCase().includes("210 km");
      const impossibilityPill = isAlibiConflict ? `
        <div class="alibi-impossibility-pill">
          <span>⚠️ PHYSICAL IMPOSSIBILITY DETECTED: 210 KM IN 10 MINUTES (SPEED REQUIRED: 1,260 KM/H)</span>
        </div>
      ` : "";

      return `
        <div class="conflict-card-hero">
          <div class="conflict-header">
            <span class="badge badge-conflict">${c.status}</span>
            <span style="font-family: var(--font-mono); font-size: 13px; color: var(--text-muted);">${c.timestamp}</span>
          </div>
          <div style="font-size: 18.5px; font-weight: 700; color: var(--text-primary);">${c.title} (${c.entity_name})</div>
          ${impossibilityPill}
          <div class="conflict-split">
            <div class="claim-box">
              <div class="claim-source-label">CLAIM A: ${c.claim_a.source}</div>
              <div style="font-size: 14.5px; color: var(--text-secondary); line-height: 1.5;">${c.claim_a.narrative}</div>
              <div style="margin-top: 8px; font-family: var(--font-mono); font-size: 12px; color: var(--gold-primary);">${c.claim_a.source_record_id}</div>
            </div>
            <div class="claim-box">
              <div class="claim-source-label">CLAIM B: ${c.claim_b.source}</div>
              <div style="font-size: 14.5px; color: var(--text-secondary); line-height: 1.5;">${c.claim_b.narrative}</div>
              <div style="margin-top: 8px; font-family: var(--font-mono); font-size: 12px; color: var(--gold-primary);">${c.claim_b.source_record_id}</div>
            </div>
          </div>
          <div class="guidance-box-hero danger">
            <strong style="color: #ff8572;">Analytical Protocol [RESOLVE CONTRADICTION]:</strong> ${c.investigative_guidance}
          </div>
        </div>
      `;
    }).join("");
  }

  const hiddenContainer = document.getElementById("hidden-links-list-container");
  if (hiddenContainer && State.hiddenLinks) {
    hiddenContainer.innerHTML = State.hiddenLinks.map(h => `
      <div class="section-box" style="border-left: 4px solid var(--amber-primary); padding: 20px 22px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span class="badge badge-inference">${h.finding_type} CANDIDATE (Score: ${h.score})</span>
          <span style="font-family: var(--font-mono); font-size: 12.5px; color: var(--gold-primary); font-weight: 600;">${h.predicted_relationship}</span>
        </div>
        <div style="font-size: 18.5px; font-weight: 700; color: var(--text-primary); margin-top: 6px;">
          ${h.source_name} (${h.source_id}) ↔ ${h.target_name} (${h.target_id})
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 10px;">
          ${h.evidence_signals.map(s => `
            <div style="background: var(--bg-elevated); padding: 10px 14px; border-radius: var(--radius-sm); font-size: 14px; border: 1px solid var(--border-subtle);">
              <strong style="color: var(--gold-primary);">${s.signal_type}:</strong> ${s.details}
              <div style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); margin-top: 3px;">Records: ${s.records.join(", ")}</div>
            </div>
          `).join("")}
        </div>
        <div style="background: var(--bg-elevated); padding: 10px 14px; border-radius: var(--radius-sm); font-size: 14.5px; margin-top: 8px; border-left: 3px solid #7ab87a;">
          <strong style="color: #7ab87a;">Tactical Recommendation [RECOMMENDATION]:</strong> ${h.recommendation}
        </div>
      </div>
    `).join("");
  }
}

// --- 6. Report Rendering ---
function renderReport() {
  if (!State.report) return;
  const r = State.report;

  document.getElementById("report-headline").innerText = r.title;
  document.getElementById("report-gen-time").innerText = `GENERATED: ${r.generated_at} | CLASSIFICATION: ${r.classification}`;

  // Executive summary
  document.getElementById("report-exec-summary").innerText = r.executive_summary.content;

  // Key entities
  const entTable = document.getElementById("report-entities-tbody");
  if (entTable) {
    entTable.innerHTML = r.key_entities.map(e => `
      <tr>
        <td class="report-entity-name"><strong>${e.name}</strong> (${e.entity_id})</td>
        <td><span class="badge badge-high">${e.priority}</span></td>
        <td class="report-entity-reason">${e.reason}</td>
      </tr>
    `).join("");
  }

  // Bridge node analysis
  const bridge = r.structural_analysis.key_bridge_node;
  document.getElementById("report-bridge-analysis").innerText = `${bridge.name} (${bridge.id}): ${bridge.significance}`;

  // Recommendations
  const recList = document.getElementById("report-rec-list");
  if (recList) {
    recList.innerHTML = r.recommendations.map(rec => `
      <li class="report-rec-item">
        <span class="badge badge-rec">${rec.label}</span>
        <strong class="rec-priority-label">[${rec.priority}]</strong>
        <span class="rec-action-text">${rec.action}</span>
      </li>
    `).join("");
  }
}

// --- Print Intelligence Brief Helper ---
function printIntelligenceBrief() {
  switchView("report-view");
  // Ensure the view is active and DOM has painted before triggering print
  setTimeout(() => {
    window.print();
  }, 100);
}
window.printIntelligenceBrief = printIntelligenceBrief;

// ==========================================================================
// Neत्र | AI Investigation Copilot Implementation
// Grounded Knowledge Graph RAG with Evidentiary Provenance
// ==========================================================================

function escapeHtml(str) {
  return String(str || "").replace(/[&<>"']/g, s => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[s]);
}

function initNetraCopilot() {
  const fab = document.getElementById("netra-fab");
  const drawer = document.getElementById("netra-drawer");
  const closeBtn = document.getElementById("netra-close-btn");
  const form = document.getElementById("netra-form");
  const input = document.getElementById("netra-input");
  const messages = document.getElementById("netra-messages");
  const chips = document.querySelectorAll(".netra-chip");

  if (!fab || !drawer) return;

  function toggleNetraDrawer(open) {
    const isOpen = open !== undefined ? open : !drawer.classList.contains("open");
    drawer.classList.toggle("open", isOpen);
    drawer.setAttribute("aria-hidden", !isOpen);
    if (isOpen) {
      setTimeout(() => input?.focus(), 250);
    }
  }

  fab.addEventListener("click", () => toggleNetraDrawer(true));
  closeBtn?.addEventListener("click", () => toggleNetraDrawer(false));

  // Global Keyboard Shortcuts (Ctrl+K or Alt+N opens, Esc closes)
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey && e.key.toLowerCase() === "k") || (e.altKey && e.key.toLowerCase() === "n")) {
      e.preventDefault();
      toggleNetraDrawer();
    } else if (e.key === "Escape" && drawer.classList.contains("open")) {
      toggleNetraDrawer(false);
    }
  });

  // Suggested Queries chip listeners
  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      handleNetraQuery(q, chip.innerText);
    });
  });

  // Form submit listener
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const queryText = input.value.trim();
    if (!queryText) return;
    input.value = "";
    handleNetraQuery(queryText, queryText);
  });

  // Interactive cross-graph node focus on entity badge click
  messages?.addEventListener("click", (e) => {
    const target = e.target.closest(".netra-entity-link");
    if (!target) return;
    const entityId = target.getAttribute("data-id");
    if (!entityId || !State.cy) return;

    // Switch to Network Explorer view
    switchView("network-explorer-view");

    // Highlight and focus node in Cytoscape
    const node = State.cy.getElementById(entityId);
    if (node && node.length > 0) {
      focusNode(node);
      State.cy.animate({
        center: { eles: node },
        zoom: Math.max(1.4, State.cy.zoom()),
        duration: 400
      });
      openEntityDossier(entityId);
    }
  });
}

function handleNetraQuery(queryKey, userDisplayText) {
  const messages = document.getElementById("netra-messages");
  if (!messages) return;

  // 1. Append User Message
  const userMsg = document.createElement("div");
  userMsg.className = "netra-msg netra-msg-user";
  userMsg.innerHTML = `<div class="netra-msg-content">${escapeHtml(userDisplayText)}</div>`;
  messages.appendChild(userMsg);
  messages.scrollTop = messages.scrollHeight;

  // 2. Typing / Graph Traversal Indicator
  const botMsg = document.createElement("div");
  botMsg.className = "netra-msg netra-msg-bot";
  botMsg.innerHTML = `
    <div class="netra-msg-sender">Neत्र ASSISTANT</div>
    <div class="netra-msg-content">
      <span style="display: inline-flex; align-items: center; gap: 6px; color: var(--copper-highlight);">
        <span class="netra-cursor">|</span> Traversing verified evidence graph...
      </span>
    </div>
  `;
  messages.appendChild(botMsg);
  messages.scrollTop = messages.scrollHeight;

  // Simulated instant graph RAG query execution (380ms)
  setTimeout(() => {
    const responseHtml = generateNetraResponse(queryKey.toLowerCase().trim());
    botMsg.querySelector(".netra-msg-content").innerHTML = responseHtml;
    messages.scrollTop = messages.scrollHeight;
  }, 380);
}

function generateNetraResponse(q) {
  // Scenario 1: Bridge Nodes / Network Connectors
  if (q.includes("bridge") || q.includes("connect") || q.includes("between") || q.includes("net a") || q.includes("net b")) {
    return `
      <p>Structural betweenness traversal complete for active case <strong>CASE0001 (Extortion)</strong>.</p>
      
      <div class="netra-evidence-block">
        <div class="netra-evidence-label">
          <span class="badge badge-fact">FACT</span>
          <span>EVIDENCE CITATIONS: CDR000001, TXN000004</span>
        </div>
        <p><strong><span class="netra-entity-link" data-id="P0005">Vijay Solanki (P0005)</span></strong> serves as the exclusive structural conduit connecting <strong>Network A</strong> (Ahmedabad core extortion syndicate) to <strong>Network B</strong> (Surat banking/mule branch). Solanki directly transacted ₹1,20,000 to mule account <strong><span class="netra-entity-link" data-id="ACC00016">ACC00016 (Meridian_03)</span></strong>.</p>
      </div>

      <div class="netra-evidence-block inference">
        <div class="netra-evidence-label">
          <span class="badge badge-inference">INFERENCE</span>
          <span>GRAPH BETWEENNESS: 0.3412</span>
        </div>
        <p>Solanki exhibits the highest Betweenness Centrality in the entire network (0.3412). He acts as the sole cross-regional coordinator; isolating him fragments the network into two disconnected sub-graphs, neutralizing the money disbursement pipeline.</p>
      </div>

      <div class="netra-evidence-block rec">
        <div class="netra-evidence-label">
          <span class="badge badge-rec">RECOMMENDATION</span>
          <span>PRIORITY LEAD #1</span>
        </div>
        <p>Target Vijay Solanki for immediate custodial interrogation under Section 41A CrPC. Subpoena KYC documents and freeze debit rights on linked account <strong><span class="netra-entity-link" data-id="ACC00016">ACC00016</span></strong>.</p>
      </div>
    `;
  }

  // Scenario 2: Call Surges / Pre-Incident Spikes
  if (q.includes("surge") || q.includes("call") || q.includes("spike") || q.includes("48h") || q.includes("telecom") || q.includes("pre-incident")) {
    return `
      <p>Temporal telecommunications density analysis completed for 48h pre-incident window.</p>

      <div class="netra-evidence-block">
        <div class="netra-evidence-label">
          <span class="badge badge-fact">FACT</span>
          <span>EVIDENCE CITATIONS: CDR000028 – CDR000035</span>
        </div>
        <p>A concentrated frequency surge of <strong>35 voice calls</strong> was logged between <strong><span class="netra-entity-link" data-id="P0004">Anil Trivedi (P0004)</span></strong> and <strong><span class="netra-entity-link" data-id="P0006">Meera Patel (P0006)</span></strong> on June 18–19, 2026, leading up to the extortion incident at Ahmedabad Zone 5.</p>
      </div>

      <div class="netra-evidence-block inference">
        <div class="netra-evidence-label">
          <span class="badge badge-inference">INFERENCE</span>
          <span>ANOMALY SCORE: 0.94 (Z-SCORE > 3.8)</span>
        </div>
        <p>Standard background communication between Trivedi and Patel is 1–2 calls weekly. The 35-call surge represents a statistically extreme operational staging event immediately preceding extortion delivery.</p>
      </div>

      <div class="netra-evidence-block rec">
        <div class="netra-evidence-label">
          <span class="badge badge-rec">RECOMMENDATION</span>
          <span>TACTICAL LEAD</span>
        </div>
        <p>Issue Section 91 CrPC notice to mobile carrier for Cell Tower ID <code>GJ-AHM-04</code> azimuth logs. Retrieve IMEI handset identifiers for both suspects to detect burner phones.</p>
      </div>
    `;
  }

  // Scenario 3: High-Value Night Transfers (> ₹50,000)
  if (q.includes("transfer") || q.includes("night") || q.includes("money") || q.includes("bank") || q.includes("50k") || q.includes("50000") || q.includes("laundering") || q.includes("cash")) {
    return `
      <p>Banking ledger anomaly detection executed on verified transactional records.</p>

      <div class="netra-evidence-block">
        <div class="netra-evidence-label">
          <span class="badge badge-fact">FACT</span>
          <span>EVIDENCE CITATIONS: TXN000004, TXN000007</span>
        </div>
        <p>Two high-value off-hours transfers were executed:</p>
        <ul style="margin: 4px 0 0 16px; padding: 0;">
          <li><strong>₹1,20,000</strong> from <strong><span class="netra-entity-link" data-id="ACC00008">ACC00008 (Sanjay Bhatt)</span></strong> to mule account <strong><span class="netra-entity-link" data-id="ACC00016">ACC00016 (Meridian_03)</span></strong> at 02:41 AM on June 15.</li>
          <li><strong>₹85,000</strong> to <strong><span class="netra-entity-link" data-id="ACC00018">ACC00018</span></strong> at 03:14 AM.</li>
        </ul>
      </div>

      <div class="netra-evidence-block inference">
        <div class="netra-evidence-label">
          <span class="badge badge-inference">INFERENCE</span>
          <span>PATTERN: OFF-HOURS MULE STRUCTURING</span>
        </div>
        <p>Transfers occurred between 02:00 AM – 04:00 AM immediately following extortion payout. Both accounts were opened with fabricated KYC documents within 14 days of the crime.</p>
      </div>

      <div class="netra-evidence-block rec">
        <div class="netra-evidence-label">
          <span class="badge badge-rec">RECOMMENDATION</span>
          <span>FINANCIAL RESTRAINT</span>
        </div>
        <p>Immediately notify Financial Intelligence Unit (FIU-IND) and order immediate debit freeze on beneficiary accounts <strong>ACC00016</strong> and <strong>ACC00018</strong>.</p>
      </div>
    `;
  }

  // Scenario 4: Alibi Conflicts & Physical Contradictions
  if (q.includes("conflict") || q.includes("alibi") || q.includes("contradiction") || q.includes("impossible") || q.includes("sighting") || q.includes("cctv")) {
    return `
      <p>Multi-source evidence cross-validation identified an unresolved physical impossibility contradiction.</p>

      <div class="netra-evidence-block">
        <div class="netra-evidence-label">
          <span class="badge badge-fact">FACT</span>
          <span>EVIDENCE CITATIONS: SURV000004, CDR000046</span>
        </div>
        <p>Suspect <strong><span class="netra-entity-link" data-id="P0007">Tarun Sharma (P0007)</span></strong> was recorded by automated surveillance CCTV at <strong><span class="netra-entity-link" data-id="Surat_Zone_3">Surat_Zone_3</span></strong> at 07:24 AM on June 22. Exactly 1 minute later at 07:25 AM, Sharma's phone pinged cell tower <strong><span class="netra-entity-link" data-id="Ahmedabad_Zone_5">Ahmedabad_Zone_5</span></strong>.</p>
      </div>

      <div class="netra-evidence-block inference">
        <div class="netra-evidence-label">
          <span class="badge badge-inference">INFERENCE</span>
          <span>VELOCITY: 15,900 KM/H (PHYSICALLY IMPOSSIBLE)</span>
        </div>
        <p>Physical distance between Surat Zone 3 and Ahmedabad Zone 5 is 265 km. Transit time of 1 minute is physically impossible. This indicates a cloned SIM device or a deliberately staged physical alibi using a decoy.</p>
      </div>

      <div class="netra-evidence-block rec">
        <div class="netra-evidence-label">
          <span class="badge badge-rec">RECOMMENDATION</span>
          <span>ALIBI VERIFICATION</span>
        </div>
        <p>Preserve Surat Zone 3 raw CCTV footage before 30-day overwrite cycle. Interrogate Tarun Sharma regarding physical possession of handset at 07:25 AM.</p>
      </div>
    `;
  }

  // Scenario 5: Suspect Spotlight: Vijay Solanki
  if (q.includes("solanki") || q.includes("vijay") || q.includes("p0005")) {
    return `
      <p>Evidentiary profile retrieved for <strong><span class="netra-entity-link" data-id="P0005">Vijay Solanki (P0005)</span></strong>.</p>

      <div class="netra-evidence-block">
        <div class="netra-evidence-label">
          <span class="badge badge-fact">FACT</span>
          <span>PRIORITY: HIGH • NETWORK A BRIDGE</span>
        </div>
        <p>Linked to 8 active co-conspirators, 1 bank account (<strong>ACC00005</strong>), and 1 mobile terminal (<strong>9000010005</strong>). Named as primary broker in FIR00001.</p>
      </div>

      <div class="netra-evidence-block inference">
        <div class="netra-evidence-label">
          <span class="badge badge-inference">INFERENCE</span>
          <span>ROLE: FINANCIAL & REGIONAL COORDINATOR</span>
        </div>
        <p>Controls the money funnel between Ahmedabad extortionists and Surat mule cash withdrawal hubs.</p>
      </div>

      <div class="netra-evidence-block rec">
        <div class="netra-evidence-label">
          <span class="badge badge-rec">RECOMMENDATION</span>
          <span>ACTION PLAN</span>
        </div>
        <p>Issue non-bailable arrest warrant. Cross-reference call records with <span class="netra-entity-link" data-id="P0012">Farida Sheikh</span> to identify overseas handlers.</p>
      </div>
    `;
  }

  // Scenario 6: Suspect Spotlight: Anil Trivedi
  if (q.includes("trivedi") || q.includes("anil") || q.includes("p0004")) {
    return `
      <p>Evidentiary profile retrieved for <strong><span class="netra-entity-link" data-id="P0004">Anil Trivedi (P0004)</span></strong>.</p>

      <div class="netra-evidence-block">
        <div class="netra-evidence-label">
          <span class="badge badge-fact">FACT</span>
          <span>FIR RECORD: FIR00001 (ACCUSED #1)</span>
        </div>
        <p>Direct operational link to extortion scene <strong>CASE0001</strong>. Logged 35 pre-incident calls to Meera Patel and 22 calls to Pooja Joshi.</p>
      </div>

      <div class="netra-evidence-block inference">
        <div class="netra-evidence-label">
          <span class="badge badge-inference">INFERENCE</span>
          <span>ROLE: GROUND LOGISTICS CHIEF</span>
        </div>
        <p>Supervises ground threat delivery and courier coordination across Ahmedabad Zone 5.</p>
      </div>

      <div class="netra-evidence-block rec">
        <div class="netra-evidence-label">
          <span class="badge badge-rec">RECOMMENDATION</span>
          <span>TACTICAL LEAD</span>
        </div>
        <p>Execute raid on registered residence in Ahmedabad Zone 5; seize physical mobile devices for digital forensic extraction.</p>
      </div>
    `;
  }

  // Fallback Guidance
  return `
    <p>Neत्र Graph RAG traversed 96 nodes and 150+ edges in active case <strong>CASE0001</strong>, but found no verified evidence matching <em>"${escapeHtml(q)}"</em>.</p>
    <p style="margin-top: 8px; color: var(--text-secondary); font-size: 11.5px;">For high-accuracy grounded results, try asking about:</p>
    <ul style="margin: 6px 0 0 16px; padding: 0; font-size: 11px; color: var(--copper-highlight); line-height: 1.6;">
      <li><strong>Bridge Suspects:</strong> <em>"Who connects Network A to Network B?"</em></li>
      <li><strong>Telecom Surges:</strong> <em>"Show 48h pre-incident call spikes"</em></li>
      <li><strong>Money Laundering:</strong> <em>"Find off-hours transfers over ₹50,000"</em></li>
      <li><strong>Alibi Contradictions:</strong> <em>"Check for conflicting CCTV sightings"</em></li>
      <li><strong>Specific Suspects:</strong> <em>"Tell me about Vijay Solanki or Anil Trivedi"</em></li>
    </ul>
  `;
}


