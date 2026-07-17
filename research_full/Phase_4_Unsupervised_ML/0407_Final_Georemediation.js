


function joinMissedAudits() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // --- CONFIGURACIÓN ---
  const SHEET_POLYGON = "polygon_audit";
  const SHEET_FULL = "full_audit";
  const SHEET_CONSOLIDATED = "ids_consolidated";
  const SHEET_OUTPUT = "joined_review_pending";

  // --- 1. OBTENER HOJAS ---
  const sheetPoly = ss.getSheetByName(SHEET_POLYGON);
  const sheetFull = ss.getSheetByName(SHEET_FULL);
  const sheetConsol = ss.getSheetByName(SHEET_CONSOLIDATED);

  if (!sheetPoly || !sheetFull) {
    Browser.msgBox("Error: No se encuentran las hojas 'polygon_audit' o 'full_audit'.");
    return;
  }

  // --- 2. OBTENER HEADERS (FILA 1) ---
  // Obtenemos la primera fila completa de ambas hojas para crear el encabezado maestro
  const headersPoly = sheetPoly.getRange(1, 1, 1, sheetPoly.getLastColumn()).getValues()[0];
  const headersFull = sheetFull.getRange(1, 1, 1, sheetFull.getLastColumn()).getValues()[0];
  
  // Header Combinado: [Headers Polygon] + [Headers Full]
  const masterHeaders = headersPoly.concat(headersFull);

  // Inicializamos el array de resultados CON los headers ya puestos
  let joinedRows = [masterHeaders];


  // --- 3. OBTENER DATOS (FILA 2 en adelante) ---
  const polyData = getDataValues(sheetPoly);
  const fullData = getDataValues(sheetFull);
  const consolData = sheetConsol ? getDataValues(sheetConsol) : [];

  // --- 4. MAPEAR ÍNDICES PARA BÚSQUEDA RÁPIDA ---
  // Asumiendo offer_id en col 0 y polygon_id en col 7 (ajusta si cambió)
  const IDX_OFFER_ID = 0; 
  const IDX_POLYGON_ID = 7; 

  // A. Set de IDs consolidados (O(1))
  let consolidatedSet = new Set();
  consolData.forEach(row => consolidatedSet.add(String(row[0])));

  // B. Mapa de Full Audit (O(1))
  let fullAuditMap = new Map();
  fullData.forEach(row => {
    fullAuditMap.set(String(row[0]), row);
  });

  // --- 5. LÓGICA DE FILTRADO Y JOIN ---
  let countFound = 0;

  polyData.forEach(polyRow => {
    let offerId = String(polyRow[IDX_OFFER_ID]);
    let polygonId = polyRow[IDX_POLYGON_ID];

    // CRITERIOS: polygon_id es -1 Y NO está consolidado
    if (String(polygonId) === "-1" && !consolidatedSet.has(offerId)) {
      
      let fullAuditRow = fullAuditMap.get(offerId);

      if (fullAuditRow) {
        // Unimos fila Polygon + fila Full Audit
        let newRow = polyRow.concat(fullAuditRow); 
        joinedRows.push(newRow);
        countFound++;
      }
    }
  });

  // --- 6. ESCRIBIR RESULTADOS ---
  let outputSheet = ss.getSheetByName(SHEET_OUTPUT);
  if (!outputSheet) {
    outputSheet = ss.insertSheet(SHEET_OUTPUT);
  } else {
    outputSheet.clear(); // Limpiamos todo
  }

  // Escribimos todo de golpe (Headers + Datos)
  if (joinedRows.length > 0) {
    outputSheet.getRange(1, 1, joinedRows.length, joinedRows[0].length).setValues(joinedRows);
    
    // Formato básico al header (negrita y congelar fila 1)
    outputSheet.getRange(1, 1, 1, joinedRows[0].length).setFontWeight("bold");
    outputSheet.setFrozenRows(1);
  }

  Logger.log(`Proceso terminado. Filas encontradas: ${countFound}`);
  Browser.msgBox(`Listo. Se exportaron ${countFound} registros (+ headers) a la hoja '${SHEET_OUTPUT}'.`);
}

// Función auxiliar simple para sacar datos sin headers
function getDataValues(sheet) {
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow < 2) return [];
  return sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
}




/**
 * OPUS: ITERATION 2 EXTRACTION (HIGHLANDER MODE)
 * ----------------------------------------------
 * Logic: Scans sources for 'vobo' OR 'vobodos'.
 * Priority: 'full_audit' FIRST.
 * Deduplication: If ID was found in full_audit, ignore it in joined_review_pending.
 * Result: Unique rows in iter_2. 'full_audit' wins conflicts.
 */

function runIter2Extraction() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- CONFIGURATION ---
  // EL ORDEN IMPORTA: La primera hoja es la "Dueña" de la verdad.
  const sourceSheetNames = ['full_audit', 'joined_review_pending'];
  const targetSheetName = 'iter_2';
  const targetHeaders = ['offer_id', 'new_pickup_lat', 'new_pickup_lon', 'new_dropoff_lat', 'new_dropoff_lon', 'source', 'is_repeated'];
  
  // --- SETUP TARGET ---
  let targetSheet = ss.getSheetByName(targetSheetName);
  if (!targetSheet) {
    targetSheet = ss.insertSheet(targetSheetName);
    targetSheet.appendRow(targetHeaders); 
  } else {
    // Si la hoja existe y está vacía, poner headers
    if (targetSheet.getLastRow() === 0) {
      targetSheet.appendRow(targetHeaders);
    }
    // OJO: Como vamos a re-escribir con lógica de unicidad,
    // si prefieres limpiar todo antes, descomenta la siguiente línea:
    // targetSheet.clearContents(); targetSheet.appendRow(targetHeaders);
    // Pero como pediste APPEND mode, lo dejo tal cual.
  }

  let masterList = [];
  // Set para controlar quién ya entró al club
  let processedIds = new Set();

  // --- PROCESSING LOOP ---
  sourceSheetNames.forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      console.warn(`⚠️ Warning: Sheet '${sheetName}' not found.`);
      return;
    }

    const data = sheet.getDataRange().getValues();
    if (data.length < 2) return; 

    const headers = data[0];
    const rows = data.slice(1);

    // Mapeo Dinámico
    const map = {
      id: headers.indexOf('offer_id'),
      p_vobo: headers.findIndex(h => h.trim() === 'pickup_vobo'),
      d_vobo: headers.findIndex(h => h.trim() === 'dropoff_vobo'),
      p_lat: headers.findIndex(h => h.trim() === 'new_pickup_lat'),
      p_lon: headers.findIndex(h => h.trim() === 'new_pickup_lon'),
      d_lat: headers.findIndex(h => h.trim() === 'new_dropoff_lat'),
      d_lon: headers.findIndex(h => h.trim() === 'new_dropoff_lon')
    };

    if (map.id === -1 || map.p_vobo === -1 || map.d_vobo === -1) {
      console.error(`🔴 Columnas críticas faltantes en ${sheetName}.`);
      return;
    }

    rows.forEach(row => {
      const offerId = String(row[map.id]).trim();
      
      // --- LOGIC: THE HIGHLANDER CHECK ---
      // Si el ID ya lo procesamos (de una hoja anterior o fila anterior), ADIÓS.
      if (processedIds.has(offerId)) {
        return; // Skip this row
      }

      const pVobo = String(row[map.p_vobo]).trim();
      const dVobo = String(row[map.d_vobo]).trim();
      const validTags = ['vobo', 'vobodos'];
      
      const hasPickupVobo = validTags.includes(pVobo);
      const hasDropoffVobo = validTags.includes(dVobo);

      if (hasPickupVobo || hasDropoffVobo) {
        
        const pLat = hasPickupVobo ? row[map.p_lat] : '';
        const pLon = hasPickupVobo ? row[map.p_lon] : '';
        const dLat = hasDropoffVobo ? row[map.d_lat] : '';
        const dLon = hasDropoffVobo ? row[map.d_lon] : '';

        masterList.push({
          id: offerId,
          pLat: pLat,
          pLon: pLon,
          dLat: dLat,
          dLon: dLon,
          source: sheetName // Guardamos la fuente ganadora
        });

        // Marcamos el ID como procesado para que nadie más lo use
        processedIds.add(offerId);
      }
    });
  });

  // --- FINAL WRITING ---
  if (masterList.length === 0) {
    Browser.msgBox("No se encontraron filas válidas.");
    return;
  }

  const outputRows = masterList.map(item => {
    // is_repeated siempre será false con esta lógica, 
    // pero mantenemos la columna por consistencia.
    return [
      item.id,
      item.pLat,
      item.pLon,
      item.dLat,
      item.dLon,
      item.source,
      false // is_repeated
    ];
  });

  const startRow = targetSheet.getLastRow() + 1;
  targetSheet.getRange(startRow, 1, outputRows.length, outputRows[0].length).setValues(outputRows);

  Browser.msgBox(`✅ EXTRACCIÓN LIMPIA.\n\nSe agregaron ${outputRows.length} filas únicas.\nPrioridad aplicada: full_audit > joined_review_pending.`);
}

/**
 * OPUS: VOBO BACK AUDIT
 * ---------------------
 * Purpose: Counts total occurrences of 'vobo' in pickup/dropoff columns 
 * across source sheets to verify the cleaning progress.
 */

function auditVoboCount() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheetNames = ['full_audit', 'joined_review_pending'];
  
  let totalVoboCount = 0;
  let breakdown = ""; // To show count per sheet in the message

  sourceSheetNames.forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      breakdown += `${sheetName}: (Sheet not found)\n`;
      return;
    }

    const data = sheet.getDataRange().getValues();
    if (data.length < 2) {
      breakdown += `${sheetName}: 0 (Empty)\n`;
      return; 
    }

    const headers = data[0];
    const rows = data.slice(1);

    // Dynamic Column Finding
    const pVoboIdx = headers.findIndex(h => h.trim() === 'pickup_vobo');
    const dVoboIdx = headers.findIndex(h => h.trim() === 'dropoff_vobo');

    if (pVoboIdx === -1 || dVoboIdx === -1) {
      breakdown += `${sheetName}: (Missing columns)\n`;
      return;
    }

    let sheetCount = 0;

    rows.forEach(row => {
      // Check Pickup
      if (String(row[pVoboIdx]).trim() === 'vobo') {
        sheetCount++;
      }
      // Check Dropoff
      if (String(row[dVoboIdx]).trim() === 'vobo') {
        sheetCount++;
      }
    });

    totalVoboCount += sheetCount;
    breakdown += `${sheetName}: ${sheetCount}\n`;
  });

  // Display Result
  Browser.msgBox(
    `✅ VOBO AUDIT COMPLETE`, 
    `Total Coordinates Recovered: ${totalVoboCount}\n\nBreakdown:\n${breakdown}`, 
    Browser.Buttons.OK
  );
}


/**
 * OPUS: THE GREAT RECONCILIATION
 * ------------------------------
 * Compares:
 * 1. Total 'vobo' flags in Source Sheets (Inputs).
 * 2. Total populated coordinate slots in 'iter_2' (Outputs).
 * * Success = These numbers match exactly.
 */

function runReconciliation() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- 1. COUNT SOURCE VOBOS (INPUTS) ---
  const sourceSheets = ['full_audit', 'joined_review_pending'];
  let sourceVoboCount = 0;

  sourceSheets.forEach(name => {
    const sheet = ss.getSheetByName(name);
    if (!sheet) return;
    const data = sheet.getDataRange().getValues();
    if (data.length < 2) return;
    
    const h = data[0];
    const pIdx = h.findIndex(x => x.trim() === 'pickup_vobo');
    const dIdx = h.findIndex(x => x.trim() === 'dropoff_vobo');

    // Skip sheet if cols missing
    if (pIdx === -1 || dIdx === -1) return;

    for (let i = 1; i < data.length; i++) {
      if (String(data[i][pIdx]).trim() === 'vobo') sourceVoboCount++;
      if (String(data[i][dIdx]).trim() === 'vobo') sourceVoboCount++;
    }
  });

  // --- 2. COUNT ITER_2 COORDINATES (OUTPUTS) ---
  const iterSheet = ss.getSheetByName('iter_2');
  let iterCoordCount = 0;

  if (iterSheet && iterSheet.getLastRow() > 1) {
    const iterData = iterSheet.getDataRange().getValues();
    const iterH = iterData[0];
    
    // Find lat columns in iter_2 (we count Lat as proxy for the pair)
    const pLatIdx = iterH.indexOf('new_pickup_lat');
    const dLatIdx = iterH.indexOf('new_dropoff_lat');

    for (let i = 1; i < iterData.length; i++) {
      const row = iterData[i];
      
      // If pickup lat has data, that's 1 coordinate recovered
      if (row[pLatIdx] !== "" && row[pLatIdx] != null) {
        iterCoordCount++;
      }
      
      // If dropoff lat has data, that's 1 coordinate recovered
      if (row[dLatIdx] !== "" && row[dLatIdx] != null) {
        iterCoordCount++;
      }
    }
  }

  // --- 3. THE VERDICT ---
  const diff = iterCoordCount - sourceVoboCount;
  let status = "✅ PERFECT MATCH";
  if (diff !== 0) status = "⚠️ DISCREPANCY FOUND";

  const msg = `${status}\n\n` +
              `Source 'vobos' (Input): ${sourceVoboCount}\n` +
              `iter_2 Coords (Output): ${iterCoordCount}\n` +
              `Difference: ${diff}`;

  Browser.msgBox("RECONCILIATION REPORT", msg, Browser.Buttons.OK);
}


/**
 * OPUS: PHANTOM VOBO DETECTOR
 * ---------------------------
 * Finds rows where 'vobo' is present, but the corresponding Lat/Lon columns are empty.
 */

function findPhantomVobo() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheets = ['full_audit', 'joined_review_pending'];
  
  let phantoms = [];

  sourceSheets.forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return;
    const data = sheet.getDataRange().getValues();
    if (data.length < 2) return;
    
    const h = data[0];
    
    // Find Indexes
    const map = {
      id: h.indexOf('offer_id'),
      p_vobo: h.findIndex(x => x.trim() === 'pickup_vobo'),
      d_vobo: h.findIndex(x => x.trim() === 'dropoff_vobo'),
      p_lat: h.findIndex(x => x.trim() === 'new_pickup_lat'),
      d_lat: h.findIndex(x => x.trim() === 'new_dropoff_lat')
    };

    if (map.p_vobo === -1 || map.d_vobo === -1) return;

    // Scan Rows
    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      const pVobo = String(row[map.p_vobo]).trim();
      const dVobo = String(row[map.d_vobo]).trim();
      const pLat = row[map.p_lat];
      const dLat = row[map.d_lat];

      // CHECK 1: Pickup Phantom
      if (pVobo === 'vobo' && (pLat === "" || pLat == null)) {
        phantoms.push({ sheet: sheetName, row: i + 1, type: 'PICKUP', id: row[map.id] });
      }

      // CHECK 2: Dropoff Phantom
      if (dVobo === 'vobo' && (dLat === "" || dLat == null)) {
        phantoms.push({ sheet: sheetName, row: i + 1, type: 'DROPOFF', id: row[map.id] });
      }
    }
  });

  // REPORT
  if (phantoms.length > 0) {
    let msg = `👻 FOUND ${phantoms.length} PHANTOM VOBOS (Empty Coords)!\n\n`;
    phantoms.forEach(p => {
      msg += `• ${p.sheet} | Row ${p.row} | ID: ${p.id} | Type: ${p.type}\n`;
    });
    msg += `\nFix these empty coordinates and run the Extraction script again!`;
    Browser.msgBox(msg);
  } else {
    Browser.msgBox("🤷 No empty coordinates found. This is a mystery.");
  }
}

/**
 * OPUS: THE MERGE & ARBITRATE (AUTONOMOUS JOIN V4 - WITH AUDIT FLAG)
 * ------------------------------------------------------------------
 * Logic Updates:
 * - Agrega columna 'is_new'.
 * - is_new = TRUE si el row recibió coordenadas desde 'iter_2'.
 * - is_new = FALSE si conservó las originales.
 */

function runTheJoin() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- CONFIGURATION ---
  const PATCH_SHEET_NAME = 'iter_2';
  const AUDIT_SHEET_NAME = 'full_audit';
  const JOIN_SHEET_NAME = 'iter_2_JOIN';

  // --- 1. LOAD SOURCES ---
  
  // A. Coordenadas Limpias (iter_2)
  const patchSheet = ss.getSheetByName(PATCH_SHEET_NAME);
  const patchData = patchSheet.getDataRange().getValues();
  const pH = patchData[0];
  const pIdx = {
    id: pH.indexOf('offer_id'),
    pLat: pH.indexOf('new_pickup_lat'), pLon: pH.indexOf('new_pickup_lon'),
    dLat: pH.indexOf('new_dropoff_lat'), dLon: pH.indexOf('new_dropoff_lon')
  };

  let patchMap = {};
  for (let i = 1; i < patchData.length; i++) {
    const row = patchData[i];
    const id = String(row[pIdx.id]).trim();
    if (id) patchMap[id] = { pLat: row[pIdx.pLat], pLon: row[pIdx.pLon], dLat: row[pIdx.dLat], dLon: row[pIdx.dLon] };
  }

  // B. Direcciones (full_audit)
  const auditSheet = ss.getSheetByName(AUDIT_SHEET_NAME);
  let addressMap = {};
  if (auditSheet) {
    const auditData = auditSheet.getDataRange().getValues();
    const aH = auditData[0];
    const aIdx = {
      id: aH.indexOf('offer_id'),
      pAddr: aH.indexOf('pickup_address'),
      dAddr: aH.indexOf('dropoff_address')
    };
    if (aIdx.id !== -1 && aIdx.pAddr !== -1) {
      for (let i = 1; i < auditData.length; i++) {
        const row = auditData[i];
        const id = String(row[aIdx.id]).trim();
        if (id) addressMap[id] = { pAddr: row[aIdx.pAddr], dAddr: row[aIdx.dAddr] };
      }
    }
  }

  // --- 2. PREPARE TARGET ---
  const joinSheet = ss.getSheetByName(JOIN_SHEET_NAME);
  if (!joinSheet) {
    Browser.msgBox(`🔴 Error: Sheet '${JOIN_SHEET_NAME}' not found.`);
    return;
  }
  
  const joinRange = joinSheet.getDataRange();
  let joinValues = joinRange.getValues();
  let jH = joinValues[0];

  // --- 3. AUTO-STRUCTURE CHECK (Dynamic Columns) ---
  let idxPAddr = jH.indexOf('pickup_address');
  let idxDAddr = jH.indexOf('dropoff_address');
  let idxIsNew = jH.indexOf('is_new'); // <--- NUEVA COLUMNA
  let headersModified = false;

  // Agregar Address si falta
  if (idxPAddr === -1) { jH.push('pickup_address'); idxPAddr = jH.length - 1; for (let i = 1; i < joinValues.length; i++) joinValues[i].push(""); headersModified = true; }
  if (idxDAddr === -1) { jH.push('dropoff_address'); idxDAddr = jH.length - 1; for (let i = 1; i < joinValues.length; i++) joinValues[i].push(""); headersModified = true; }
  
  // Agregar is_new si falta
  if (idxIsNew === -1) { 
    jH.push('is_new'); 
    idxIsNew = jH.length - 1; 
    for (let i = 1; i < joinValues.length; i++) joinValues[i].push(""); 
    headersModified = true; 
  }

  // Mapear índices finales
  const jIdx = {
    id: jH.indexOf('offer_id'),
    orig_pLat: jH.indexOf('pickup_lat'), orig_pLon: jH.indexOf('pickup_lon'),
    orig_dLat: jH.indexOf('dropoff_lat'), orig_dLon: jH.indexOf('dropoff_lon'),
    new_pLat: jH.indexOf('new_pickup_lat'), new_pLon: jH.indexOf('new_pickup_lon'),
    new_dLat: jH.indexOf('new_dropoff_lat'), new_dLon: jH.indexOf('new_dropoff_lon'),
    fin_pLat: jH.indexOf('final_pickup_lat'), fin_pLon: jH.indexOf('final_pickup_lon'),
    fin_dLat: jH.indexOf('final_dropoff_lat'), fin_dLon: jH.indexOf('final_dropoff_lon'),
    pAddr: idxPAddr, dAddr: idxDAddr,
    isNew: idxIsNew // <--- Index
  };

  // --- 4. PROCESSING LOOP ---
  let countNew = 0;

  for (let i = 1; i < joinValues.length; i++) {
    const row = joinValues[i];
    const id = String(row[jIdx.id]).trim();
    
    // A. Fill Addresses
    if (addressMap[id]) {
      row[jIdx.pAddr] = addressMap[id].pAddr;
      row[jIdx.dAddr] = addressMap[id].dAddr;
    }

    // B. Fill Parches & Detect New
    let new_pLat = "", new_pLon = "", new_dLat = "", new_dLon = "";
    let isRowNew = false; // Default FALSE

    if (patchMap[id]) {
      const match = patchMap[id];
      new_pLat = match.pLat; new_pLon = match.pLon;
      new_dLat = match.dLat; new_dLon = match.dLon;
      isRowNew = true; // TRUE porque vino de iter_2
      countNew++;
    }

    row[jIdx.new_pLat] = new_pLat; row[jIdx.new_pLon] = new_pLon;
    row[jIdx.new_dLat] = new_dLat; row[jIdx.new_dLon] = new_dLon;
    
    // Escribir la bandera is_new
    row[jIdx.isNew] = isRowNew;

    // C. Calculate Finals
    row[jIdx.fin_pLat] = (new_pLat !== "" && new_pLat != null) ? new_pLat : row[jIdx.orig_pLat];
    row[jIdx.fin_pLon] = (new_pLon !== "" && new_pLon != null) ? new_pLon : row[jIdx.orig_pLon];
    row[jIdx.fin_dLat] = (new_dLat !== "" && new_dLat != null) ? new_dLat : row[jIdx.orig_dLat];
    row[jIdx.fin_dLon] = (new_dLon !== "" && new_dLon != null) ? new_dLon : row[jIdx.orig_dLon];
  }

  // --- 5. WRITE BACK ---
  if (headersModified) {
    joinSheet.clearContents(); 
  }
  joinSheet.getRange(1, 1, joinValues.length, joinValues[0].length).setValues(joinValues);

  Browser.msgBox(`✅ JOIN AUDITADO.\n\n- Filas Totales: ${joinValues.length - 1}\n- Filas Modificadas (is_new=TRUE): ${countNew}`);
}



/**
 * OPUS: THE VETO FLAG
 * -------------------
 * Purpose: Prevents double work.
 * Logic: 
 * 1. Scans 'joined_review_pending' for all Offer IDs.
 * 2. Scans 'full_audit'.
 * 3. Adds column 'exterior/veto'.
 * 4. Sets TRUE if ID exists in pending sheet, else FALSE.
 */

function flagVetoRows() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- CONFIGURATION ---
  const VETO_SOURCE_SHEET = 'joined_review_pending'; // Where the IDs already exist
  const TARGET_SHEET = 'full_audit';                 // Where we are working
  const NEW_HEADER = 'exterior/veto';

  // --- 1. BUILD THE "VETO LIST" (IDs to ignore) ---
  const vetoSheet = ss.getSheetByName(VETO_SOURCE_SHEET);
  if (!vetoSheet) {
    Browser.msgBox(`🔴 Error: Source sheet '${VETO_SOURCE_SHEET}' not found.`);
    return;
  }
  
  const vetoData = vetoSheet.getDataRange().getValues();
  // Find ID column index in source
  const vetoHeaders = vetoData[0];
  const vetoIdIdx = vetoHeaders.indexOf('offer_id');

  if (vetoIdIdx === -1) {
    Browser.msgBox("🔴 Error: 'offer_id' column not found in joined_review_pending.");
    return;
  }

  // Store in a Set for instant lookup (O(1) speed)
  let vetoSet = new Set();
  for (let i = 1; i < vetoData.length; i++) {
    const id = String(vetoData[i][vetoIdIdx]).trim();
    if (id) vetoSet.add(id);
  }

  // --- 2. PROCESS TARGET SHEET ---
  const targetSheet = ss.getSheetByName(TARGET_SHEET);
  if (!targetSheet) {
    Browser.msgBox(`🔴 Error: Target sheet '${TARGET_SHEET}' not found.`);
    return;
  }

  const targetData = targetSheet.getDataRange().getValues();
  const targetHeaders = targetData[0];
  const targetIdIdx = targetHeaders.indexOf('offer_id');

  if (targetIdIdx === -1) {
    Browser.msgBox("🔴 Error: 'offer_id' column not found in full_audit.");
    return;
  }

  // Prepare Output Column
  // We create a 2D array: [[Header], [Value], [Value]...]
  let outputColumn = [[NEW_HEADER]];

  for (let i = 1; i < targetData.length; i++) {
    const id = String(targetData[i][targetIdIdx]).trim();
    
    // THE CHECK
    if (vetoSet.has(id)) {
      outputColumn.push([true]);  // Exists in pending -> VETO
    } else {
      outputColumn.push([false]); // New -> Work on it
    }
  }

  // --- 3. WRITE RESULT ---
  // Determine where to put the new column (End of sheet)
  const lastCol = targetSheet.getLastColumn();
  
  // Write the new column
  targetSheet.getRange(1, lastCol + 1, outputColumn.length, 1).setValues(outputColumn);

  Browser.msgBox(`✅ VETO FLAG APPLIED.\n\nFlagged ${outputColumn.filter(x => x[0] === true).length} rows as TRUE (Already in pending).`);
}

/**
 * OPUS: DUPLICATE ISOLATION PROTOCOL (ENRICHED CONTEXT MODE)
 * ----------------------------------------------------------
 * Objetivo: Aislar conflictos en 'iter_2' y ENRIQUECERLOS con direcciones
 * desde 'full_audit' para facilitar la decisión humana.
 */

function isolateDuplicates() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const SOURCE_ITER = 'iter_2';
  const SOURCE_CONTEXT = 'full_audit'; // Fuente de las direcciones
  const TARGET_SHEET = 'iter_2_duplicates';

  // --- 1. CARGAR CONTEXTO (DIRECCIONES) ---
  const sheetContext = ss.getSheetByName(SOURCE_CONTEXT);
  if (!sheetContext) {
    Browser.msgBox(`🔴 Error: No se encuentra '${SOURCE_CONTEXT}'.`);
    return;
  }
  
  const dataContext = sheetContext.getDataRange().getValues();
  const hContext = dataContext[0];
  
  // Mapear columnas de contexto
  const ctxIdx = {
    id: hContext.indexOf('offer_id'),
    pAddr: hContext.indexOf('pickup_address'),
    dAddr: hContext.indexOf('dropoff_address'),
    gPAddr: hContext.indexOf('google_verified_address'),
    gDAddr: hContext.indexOf('google_dropoff_addr') // Ojo con el nombre exacto
  };

  if (ctxIdx.id === -1) {
    Browser.msgBox(`🔴 Error: Falta 'offer_id' en ${SOURCE_CONTEXT}.`);
    return;
  }

  // Crear Mapa de Contexto: ID -> [Dir1, Dir2, Google1, Google2]
  let addressMap = new Map();
  for (let i = 1; i < dataContext.length; i++) {
    const row = dataContext[i];
    const id = String(row[ctxIdx.id]).trim();
    if (id) {
      addressMap.set(id, [
        (ctxIdx.pAddr > -1) ? row[ctxIdx.pAddr] : '',
        (ctxIdx.dAddr > -1) ? row[ctxIdx.dAddr] : '',
        (ctxIdx.gPAddr > -1) ? row[ctxIdx.gPAddr] : '',
        (ctxIdx.gDAddr > -1) ? row[ctxIdx.gDAddr] : ''
      ]);
    }
  }

  // --- 2. CARGAR ITER_2 (CONFLICTOS) ---
  const sheetIter = ss.getSheetByName(SOURCE_ITER);
  if (!sheetIter) {
    Browser.msgBox(`🔴 Error: No se encuentra '${SOURCE_ITER}'.`);
    return;
  }

  const dataIter = sheetIter.getDataRange().getValues();
  if (dataIter.length < 2) {
    Browser.msgBox("⚠️ iter_2 está vacía.");
    return;
  }

  const headersIter = dataIter[0];
  const rowsIter = dataIter.slice(1);

  const idx = {
    id: headersIter.indexOf('offer_id'),
    pLat: headersIter.indexOf('new_pickup_lat'),
    pLon: headersIter.indexOf('new_pickup_lon'),
    dLat: headersIter.indexOf('new_dropoff_lat'),
    dLon: headersIter.indexOf('new_dropoff_lon')
  };

  // --- 3. DETECTAR CONFLICTOS ---
  let groups = {};
  rowsIter.forEach(row => {
    const id = String(row[idx.id]).trim();
    if (!id) return;
    if (!groups[id]) groups[id] = [];
    groups[id].push(row);
  });

  let conflictRows = [];
  let ignoredCount = 0;

  for (const [id, groupRows] of Object.entries(groups)) {
    if (groupRows.length > 1) {
      // Chequeo de Identidad (Deduplicación Inteligente)
      const base = groupRows[0];
      const baseStr = `${base[idx.pLat]}|${base[idx.pLon]}|${base[idx.dLat]}|${base[idx.dLon]}`;
      let isConflict = false;

      for (let i = 1; i < groupRows.length; i++) {
        const current = groupRows[i];
        const currentStr = `${current[idx.pLat]}|${current[idx.pLon]}|${current[idx.dLat]}|${current[idx.dLon]}`;
        if (baseStr !== currentStr) {
          isConflict = true;
          break;
        }
      }

      if (isConflict) {
        // ENRIQUECER LAS FILAS ANTES DE GUARDAR
        const extraData = addressMap.get(id) || ['(No encontrado)', '', '', ''];
        
        // Añadir contexto a cada fila del grupo conflictivo
        const enrichedGroup = groupRows.map(row => row.concat(extraData));
        conflictRows.push(...enrichedGroup);
      } else {
        ignoredCount++;
      }
    }
  }

  // --- 4. EXPORTAR ---
  let targetSheet = ss.getSheetByName(TARGET_SHEET);
  if (!targetSheet) {
    targetSheet = ss.insertSheet(TARGET_SHEET);
  } else {
    targetSheet.clear(); 
  }

  // Headers Combinados
  const newHeaders = headersIter.concat([
    'pickup_address (Audit)', 
    'dropoff_address (Audit)', 
    'google_verified_p (Audit)', 
    'google_verified_d (Audit)'
  ]);

  targetSheet.appendRow(newHeaders);

  if (conflictRows.length > 0) {
    targetSheet.getRange(2, 1, conflictRows.length, conflictRows[0].length).setValues(conflictRows);
    
    // Formato
    targetSheet.getRange(1, 1, 1, newHeaders.length).setFontWeight("bold");
    targetSheet.setFrozenRows(1);
    targetSheet.getRange(2, 1, conflictRows.length, newHeaders.length).sort({column: 1, ascending: true});
    
    // Auto-resize para leer las direcciones
    targetSheet.autoResizeColumns(newHeaders.length - 3, 4);
  }

  // --- REPORTE ---
  let msg = "REPORTE ENRIQUECIDO:\n\n";
  if (conflictRows.length === 0) {
    msg += "✅ No hay conflictos reales.\n";
  } else {
    msg += `⚠️ CONFLICTOS AISLADOS: ${conflictRows.length} filas.\nSe agregaron direcciones de 'full_audit' para contexto.\n\n`;
  }
  if (ignoredCount > 0) msg += `ℹ️ Se ignoraron ${ignoredCount} grupos idénticos.`;

  Browser.msgBox(msg);
}




/**
 * OPUS: THE WINNER PATCH (PICKUP ONLY SURGERY)
 * --------------------------------------------
 * Objetivo: Leer 'iter_2_duplicates' buscando 'gana'.
 * Acción: Sobrescribir EXCLUSIVAMENTE las coordenadas de PICKUP
 * en las hojas fuente. El Dropoff NO se toca.
 */

function applyWinnersToSources() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- CONFIGURACIÓN ---
  const DUPLICATES_SHEET = 'iter_2_duplicates';
  const TRIGGER_WORD = 'gana';
  const COL_WINNER = 'who_wins'; 

  // --- 1. LEER LOS GANADORES ---
  const sheetDup = ss.getSheetByName(DUPLICATES_SHEET);
  if (!sheetDup) {
    Browser.msgBox(`🔴 Error: No se encuentra '${DUPLICATES_SHEET}'.`);
    return;
  }

  const dataDup = sheetDup.getDataRange().getValues();
  const hDup = dataDup[0];

  // Mapear solo lo necesario
  const idxDup = {
    id: hDup.indexOf('offer_id'),
    winner: hDup.indexOf(COL_WINNER),
    pLat: hDup.indexOf('new_pickup_lat'),
    pLon: hDup.indexOf('new_pickup_lon')
    // Dropoff ignorado intencionalmente
  };

  if (idxDup.winner === -1) {
    Browser.msgBox(`🔴 Error: Falta columna '${COL_WINNER}'.`);
    return;
  }

  // Crear Mapa de Ganadores: ID -> {Only Pickup}
  let winnerMap = new Map();
  let countWinners = 0;

  for (let i = 1; i < dataDup.length; i++) {
    const row = dataDup[i];
    const signal = String(row[idxDup.winner]).trim().toLowerCase();
    
    if (signal === TRIGGER_WORD) {
      const id = String(row[idxDup.id]).trim();
      if (id) {
        winnerMap.set(id, {
          pLat: row[idxDup.pLat],
          pLon: row[idxDup.pLon]
        });
        countWinners++;
      }
    }
  }

  if (countWinners === 0) {
    Browser.msgBox("⚠️ No hay ganadores marcados con 'gana'.");
    return;
  }

  // --- 2. APLICAR A LAS FUENTES (SOLO PICKUP) ---
  let totalUpdates = 0;
  const TARGET_SHEET_NAMES = ['full_audit', 'joined_review_pending']; 

  TARGET_SHEET_NAMES.forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return;

    const data = sheet.getDataRange().getValues();
    const h = data[0];

    const idx = {
      id: h.indexOf('offer_id'),
      pLat: h.indexOf('new_pickup_lat'),
      pLon: h.indexOf('new_pickup_lon')
    };

    if (idx.id === -1 || idx.pLat === -1) {
      return; // Si no hay columnas de pickup, saltamos
    }

    let sheetUpdates = 0;

    for (let i = 1; i < data.length; i++) {
      const id = String(data[i][idx.id]).trim();
      
      if (winnerMap.has(id)) {
        const win = winnerMap.get(id);
        
        // CIRUGÍA LÁSER: SOLO PICKUP
        data[i][idx.pLat] = win.pLat;
        data[i][idx.pLon] = win.pLon;
        
        sheetUpdates++;
      }
    }

    if (sheetUpdates > 0) {
      sheet.getRange(1, 1, data.length, data[0].length).setValues(data);
      totalUpdates += sheetUpdates;
    }
  });

  Browser.msgBox(`✅ ACTUALIZACIÓN PICKUP COMPLETA\n\n- Ganadores: ${countWinners}\n- Filas corregidas: ${totalUpdates}\n\nEl Dropoff se mantuvo intacto.`);
}



/**
 * OPUS: FINAL NYE CONSOLIDATION (AUDIT-BASED)
 * -------------------------------------------
 * Objetivo: Generar el Dataset Maestro Final usando 'full_audit' como base.
 * Destino: 'iter_2_NYEJoin' 🥂
 * * Flujo:
 * 1. Carga Parches de 'iter_2'.
 * 2. Recorre 'full_audit' (Universo Completo).
 * 3. Si hay parche en iter_2 -> Usa coordenada nueva (is_new = TRUE).
 * 4. Si no -> Mantiene coordenada original de full_audit.
 */

function runAuditBasedConsolidation() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- FUENTES ---
  const UNIVERSE_SHEET = 'full_audit';  // Base + Contexto
  const PATCH_SHEET = 'iter_2';         // Correcciones
  
  const TARGET_SHEET = 'iter_2_NYEJoin';   // <--- EL DESTINO FESTIVO 🎉

  // --- 1. MEMORIZAR PARCHES (iter_2) ---
  const patchSheet = ss.getSheetByName(PATCH_SHEET);
  let patchMap = new Map();
  
  if (patchSheet) {
    const data = patchSheet.getDataRange().getValues();
    const h = data[0];
    const idx = {
      id: h.indexOf('offer_id'),
      pLat: h.indexOf('new_pickup_lat'), pLon: h.indexOf('new_pickup_lon'),
      dLat: h.indexOf('new_dropoff_lat'), dLon: h.indexOf('new_dropoff_lon')
    };

    // Crear Mapa: ID -> Coordenadas Nuevas
    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      const id = String(row[idx.id]).trim();
      if (id) {
        patchMap.set(id, {
          pLat: row[idx.pLat], pLon: row[idx.pLon],
          dLat: row[idx.dLat], dLon: row[idx.dLon]
        });
      }
    }
  }

  // --- 2. LEER UNIVERSO (full_audit) ---
  const auditSheet = ss.getSheetByName(UNIVERSE_SHEET);
  if (!auditSheet) {
    Browser.msgBox(`🔴 Error: No encuentro '${UNIVERSE_SHEET}'.`);
    return;
  }
  const auditData = auditSheet.getDataRange().getValues();
  const aH = auditData[0];
  
  // Mapeo basado en tus columnas de full_audit
  const aIdx = {
    id: aH.indexOf('offer_id'),
    // Originales
    orig_pLat: aH.indexOf('pickup_lat'),
    orig_pLon: aH.indexOf('pickup_lon'),
    orig_dLat: aH.indexOf('dropoff_lat'),
    orig_dLon: aH.indexOf('dropoff_lon'),
    // Contexto
    pAddr: aH.indexOf('pickup_address'),
    dAddr: aH.indexOf('dropoff_address')
  };

  if (aIdx.id === -1 || aIdx.orig_pLat === -1) {
    Browser.msgBox("🔴 Error: Faltan columnas clave (offer_id o lat/lon originales) en full_audit.");
    return;
  }

  // --- 3. CONSTRUIR MATRIZ FINAL ---
  const outputHeaders = [
    'offer_id', 
    'pickup_lat', 'pickup_lon', 'dropoff_lat', 'dropoff_lon', // Originales
    'pickup_address', 'dropoff_address',                      // Contexto
    'new_pickup_lat', 'new_pickup_lon', 'new_dropoff_lat', 'new_dropoff_lon', // Parches
    'final_pickup_lat', 'final_pickup_lon', 'final_dropoff_lat', 'final_dropoff_lon', // Finales
    'is_new' // Bandera
  ];

  let outputRows = [outputHeaders];
  let patchCount = 0;

  for (let i = 1; i < auditData.length; i++) {
    const row = auditData[i];
    const id = String(row[aIdx.id]).trim();
    if (!id) continue; // Saltar filas vacías

    // A. Datos Base (Originales + Contexto)
    const orig_pLat = row[aIdx.orig_pLat];
    const orig_pLon = row[aIdx.orig_pLon];
    const orig_dLat = row[aIdx.orig_dLat];
    const orig_dLon = row[aIdx.orig_dLon];
    const pAddr = row[aIdx.pAddr];
    const dAddr = row[aIdx.dAddr];

    // B. Buscar Parche
    let new_pLat = "", new_pLon = "", new_dLat = "", new_dLon = "";
    let isNew = false;

    if (patchMap.has(id)) {
      const patch = patchMap.get(id);
      new_pLat = patch.pLat; new_pLon = patch.pLon;
      new_dLat = patch.dLat; new_dLon = patch.dLon;
      isNew = true;
      patchCount++;
    }

    // C. Calcular Finales (Prioridad: Nuevo > Original)
    const final_pLat = (new_pLat !== "" && new_pLat != null) ? new_pLat : orig_pLat;
    const final_pLon = (new_pLon !== "" && new_pLon != null) ? new_pLon : orig_pLon;
    const final_dLat = (new_dLat !== "" && new_dLat != null) ? new_dLat : orig_dLat;
    const final_dLon = (new_dLon !== "" && new_dLon != null) ? new_dLon : orig_dLon;

    outputRows.push([
      id,
      orig_pLat, orig_pLon, orig_dLat, orig_dLon,
      pAddr, dAddr,
      new_pLat, new_pLon, new_dLat, new_dLon,
      final_pLat, final_pLon, final_dLat, final_dLon,
      isNew
    ]);
  }

  // --- 4. ESCRIBIR EN TARGET ---
  let targetSheet = ss.getSheetByName(TARGET_SHEET);
  if (!targetSheet) {
    targetSheet = ss.insertSheet(TARGET_SHEET);
  } else {
    targetSheet.clear(); 
  }

  targetSheet.getRange(1, 1, outputRows.length, outputRows[0].length).setValues(outputRows);
  
  // Formato
  targetSheet.getRange(1, 1, 1, outputRows[0].length).setFontWeight("bold");
  targetSheet.setFrozenRows(1);

  Browser.msgBox(
    `✅ CONSOLIDACIÓN DE AÑO NUEVO COMPLETADA 🎆\n\n` +
    `• Destino: ${TARGET_SHEET}\n` +
    `• Universo Procesado: ${outputRows.length - 1} filas\n` +
    `• Parches Aplicados (is_new): ${patchCount}`
  );
}