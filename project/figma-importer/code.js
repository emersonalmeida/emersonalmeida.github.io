// code.js - minimal plugin main (fonte carregada corretamente antes de escrever characters)
figma.showUI(__html__, { width: 420, height: 360 });

// cache simples
const loadedFonts = new Map();
async function loadFontIfNeeded(family = "Inter", style = "Regular") {
  const key = `${family}::${style}`;
  if (loadedFonts.has(key)) return;
  try {
    await figma.loadFontAsync({ family, style });
    loadedFonts.set(key, true);
  } catch (err) {
    // fallback para Roboto (algo presente no Figma)
    if (family !== "Roboto") {
      await loadFontIfNeeded("Roboto", style);
    } else {
      // se Roboto falhar, rethrow
      throw err;
    }
  }
}

async function createSimpleFrame(item) {
  const padding = 12;
  const w = 360;
  const titleSize = 16;
  const subSize = 12;
  const bodySize = 12;

  const frame = figma.createFrame();
  frame.name = item.title || "Item";
  frame.resize(w, 140);
  frame.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  frame.strokeWeight = 0;
  frame.cornerRadius = 8;

  // --- Title (garantir fonte antes de escrever)
  await loadFontIfNeeded("Inter", "Bold").catch(() => loadFontIfNeeded("Roboto", "Bold"));
  const title = figma.createText();
  title.fontName = { family: "Inter", style: "Bold" };
  title.fontSize = titleSize;
  // escreve characters SÓ APÓS loadFontAsync
  title.characters = item.title || "—";
  title.x = padding;
  title.y = padding;
  title.resize(w - padding * 2, 24);

  // --- Subtitle
  await loadFontIfNeeded("Inter", "Regular").catch(() => loadFontIfNeeded("Roboto", "Regular"));
  const sub = figma.createText();
  sub.fontName = { family: "Inter", style: "Regular" };
  sub.fontSize = subSize;
  sub.characters = item.subtitle || "";
  sub.x = padding;
  sub.y = title.y + title.height + 6;
  sub.resize(w - padding * 2, 20);
  sub.fills = [{ type: "SOLID", color: { r: 0.35, g: 0.35, b: 0.4 } }];

  // --- Body/description
  const body = figma.createText();
  body.fontName = { family: "Inter", style: "Regular" };
  body.fontSize = bodySize;
  body.characters = (item.description && item.description.slice(0, 400)) || "";
  body.x = padding;
  body.y = sub.y + sub.height + 8;
  body.resize(w - padding * 2, 60);

  frame.appendChild(title);
  frame.appendChild(sub);
  frame.appendChild(body);

  return frame;
}

figma.ui.onmessage = async (msg) => {
  if (msg.type === "create-frames") {
    const items = msg.items || [];
    if (!items.length) {
      figma.notify("Nada para importar");
      figma.ui.postMessage({ error: "empty" });
      return;
    }

    try {
      figma.notify(`Importando ${items.length} itens...`);
      const page = figma.currentPage;
      const container = figma.createFrame();
      container.name = `Import - ${new Date().toISOString().slice(0,19).replace("T"," ")}`;
      container.fills = [];
      container.layoutMode = "NONE";
      page.appendChild(container);

      const gapY = 20;
      let y = 0;
      for (let i = 0; i < items.length; i++) {
        figma.ui.postMessage({ status: `creating ${i+1}/${items.length}` });
        const it = items[i];
        const frame = await createSimpleFrame(it);
        frame.x = 0;
        frame.y = y;
        container.appendChild(frame);
        y += frame.height + gapY;
      }

      if (container.children.length) {
        figma.viewport.scrollAndZoomIntoView([container.children[0]]);
      }

      figma.notify(`Import completo: ${items.length}`);
      figma.ui.postMessage({ ok: true, created: items.length });
    } catch (err) {
      console.error(err);
      figma.ui.postMessage({ error: String(err) });
      figma.notify("Erro: " + String(err));
    }
  }

  // small ping handler so UI can know plugin is alive
  if (msg.type === "ping") {
    figma.ui.postMessage({ status: "plugin-pong" });
  }
};
