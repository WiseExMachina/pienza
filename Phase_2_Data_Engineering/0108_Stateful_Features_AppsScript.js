// ====================================================================================
// ===               PROYECTO OPUS: MOTOR DE FEATURES (v1.0 - Unificado)            ===
// ====================================================================================

// ==============================================================================
// === CONFIGURACIÓN GLOBAL (ÚNICO LUGAR PARA EDITAR)                         ===
// ==============================================================================
const CONFIG = {
  sheetName: "Sheet1",
  
  // Nombres de Columnas de Entrada
  session_fk: "session_fk",
  offer_timestamp: "offer_timestamp",
  completed_timestamp: "completed_timestamp",
  start_timestamp: "start_timestamp",
  upfront_fare: "upfront_fare",
  offer_action_fk: "offer_action_fk",
  outcome_fk: "outcome_fk",
  dist_to_pickup_km: "dist_to_pickup_km",
  time_to_pickup_sec: "time_to_pickup_sec",
  est_trip_time_sec: "est_trip_time_sec",
  realized_fare: "realized_fare",
  spread_percentage: "spread_percentage",
  deadhead_wfp: "deadhead_wfp",
  delta_time_sec: "delta_time_sec",
  realized_traffic_index: "realized_traffic_index",
  
  // Nombres de Columnas de Destino (Output)
  time_since_last_offer: "time_since_last_offer",
  density_cols: ["offer_density_10sec", "offer_density_30sec", "offer_density_60sec", "offer_density_180sec"],
  consecutive_rejects: "consecutive_rejects",
  cycle_avg_dtp_km: "cycle_avg_dtp_km",
  cycle_std_dtp_km: "cycle_std_dtp_km",
  cycle_ttp_dtp_ratio: "cycle_ttp_dtp_ratio",
  dispatch_lead_time_sec: "dispatch_lead_time_sec",
  cycle_rolling_avg_spread: "cycle_rolling_avg_spread",
  total_accumulated_deadhead_sec: "total_accumulated_deadhead_sec",
  cycle_cumulative_net_earnings: "cycle_cumulative_net_earnings",
  eph_complete_ML: "eph_complete_ML",
  eph_realized_EDA: "eph_realized_EDA",
  eph_complete_EDA: "eph_complete_EDA",
  historical_time_delta_sec: "historical_time_delta_sec",historical_rolling_avg_traffic_index: "historical_rolling_avg_traffic_index",
};

// ==============================================================================
// === FUNCIONES DE AYUDA (DEFINIDAS UNA SOLA VEZ)                            ===
// ==============================================================================

/**
 * Parsea universalmente timestamps (texto u objetos de Fecha).
 */
function parseTimestamp_Universal(timestampValue) {
  if (timestampValue instanceof Date) { return timestampValue; }
  const timestampStr = timestampValue ? timestampValue.toString() : "";
  if (timestampStr.trim() === '') { return null; }
  try {
    const parts = timestampStr.match(/(\d{4})[:|-](\d{2})[:|-](\d{2})\s(\d{1,2}):(\d{2}):(\d{2})/);
    if (!parts) return null;
    const [ , year, month, day, hour, minute, second] = parts;
    const isoString = `${year}-${month}-${day}T${hour.padStart(2, '0')}:${minute}:${second}Z`;
    const dateObj = new Date(isoString);
    return isNaN(dateObj.getTime()) ? null : dateObj;
  } catch(e) { return null; }
}

/**
 * Calcula el promedio de un array.
 */
function calculateAverage(arr) {
  if (!arr || arr.length === 0) return null;
  const sum = arr.reduce((a, b) => a + b, 0);
  return sum / arr.length;
}

/**
 * Calcula la desviación estándar de un array.
 */
function calculateStdDev(arr, avg) {
  if (!arr || arr.length < 2) return 0;
  const squareDiffs = arr.map(value => (value - avg) ** 2);
  const avgSquareDiff = calculateAverage(squareDiffs);
  return Math.sqrt(avgSquareDiff);
}

// ==============================================================================
// === SCRIPT: calculateTimeSincePreviousOffer (v3.3 - Output in Seconds)     ===
// ==============================================================================

function calculateTimeSincePreviousOffer() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) { /* ... */ return; }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  const headers = data[0];
  
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const timestampColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const outcomeColIdx = headers.indexOf(CONFIG.outcome_fk);
  
  let targetColIdx = headers.indexOf(CONFIG.time_since_last_offer);
  if (targetColIdx === -1) { /* ... (código para añadir columna) ... */ }

  if ([sessionColIdx, timestampColIdx, outcomeColIdx].includes(-1)) { /* ... (código de error) ... */ return; }

  const outputValues = [];

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const previousRow = data[i - 1];

    const currentTimestamp = currentRow[timestampColIdx];
    const previousTimestamp = (i > 0) ? data[i-1][timestampColIdx] : null;
    
    const currentSession = currentRow[sessionColIdx];
    const previousSession = (i > 0) ? previousRow[sessionColIdx] : null;
    const previousOutcome = (i > 0) ? previousRow[outcomeColIdx] : null;

    let timeSince = null; 

    const isResetRow = (i === 1 || currentSession !== previousSession || previousOutcome === "completed");

    if (currentTimestamp instanceof Date) {
      if (isResetRow) {
        timeSince = null;
      } else if (previousTimestamp instanceof Date) {
        if (currentTimestamp >= previousTimestamp) {
          const diffMilliseconds = currentTimestamp - previousTimestamp;
          // --- CAMBIO CLAVE EN EL CÁLCULO ---
          timeSince = Math.round(diffMilliseconds / 1000); // Convertir a segundos
        } else {
          timeSince = null; // Datos desordenados
        }
      }
    }
    outputValues.push([timeSince]);
  }
  
  if (outputValues.length > 0) {
    // --- CAMBIO CLAVE EN EL FORMATO ---
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("0"); // Formato de número entero
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'time_since_last_offer' (en segundos) completado!");
  }
}

// ==============================================================================
// === SCRIPT: calculateOfferDensity (v2.1 - Refactored)                      ===
// === PURPOSE: Assumes clean Date objects and uses the global CONFIG object. ===
// ==============================================================================

function calculateOfferDensity() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0]; // Usar let para poder modificarlo

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const timestampColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const outcomeColIdx = headers.indexOf(CONFIG.outcome_fk);

  if ([sessionColIdx, timestampColIdx, outcomeColIdx].includes(-1)) {
    Logger.log(`Índices encontrados: session=${sessionColIdx}, timestamp=${timestampColIdx}, outcome=${outcomeColIdx}`);
    SpreadsheetApp.getUi().alert("Error: Una o más columnas de entrada no se encontraron en 'calculateOfferDensity'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  // Encontrar o crear las columnas de destino
  const targetColIndices = [];
  CONFIG.density_cols.forEach(colName => {
    let colIdx = headers.indexOf(colName);
    if (colIdx === -1) {
      sheet.insertColumnsAfter(headers.length, 1);
      colIdx = headers.length;
      sheet.getRange(1, colIdx + 1).setValue(colName);
      headers.push(colName); // Actualizar nuestra copia de los encabezados
    }
    targetColIndices.push(colIdx);
  });
  
  const timeWindows = [10, 30, 60, 180];
  const outputValues = [];
  let currentSearchBlock = []; // "Memoria" del script

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const previousRow = data[i - 1];

    const currentTimestamp = currentRow[timestampColIdx];
    const currentSession = currentRow[sessionColIdx];
    const previousSession = (i > 1) ? previousRow[sessionColIdx] : null;
    const previousOutcome = (i > 1) ? previousRow[outcomeColIdx] : null;

    let densities = [null, null, null, null];

    if (currentTimestamp instanceof Date) {
      // Lógica de Reinicio del bloque de búsqueda
      if (i === 1 || currentSession !== previousSession || previousOutcome === "completed") {
        currentSearchBlock = []; 
      }
      
      currentSearchBlock.push(currentTimestamp);

      // Calcular densidades
      densities = timeWindows.map(windowSeconds => {
        const windowStart = new Date(currentTimestamp.getTime() - (windowSeconds * 1000));
        
        // Optimización: podar el bloque
        const maxWindowStart = new Date(currentTimestamp.getTime() - (Math.max(...timeWindows) * 1000));
        currentSearchBlock = currentSearchBlock.filter(ts => ts >= maxWindowStart);

        return currentSearchBlock.filter(ts => ts >= windowStart).length;
      });
    }
    
    outputValues.push(densities);
  }
  
  if (outputValues.length > 0) {
    // Escribir los resultados en las columnas de destino
    targetColIndices.forEach((colIdx, i) => {
      const columnData = outputValues.map(row => [row[i]]);
      sheet.getRange(2, colIdx + 1, columnData.length, 1).setValues(columnData).setNumberFormat("0");
    });
    SpreadsheetApp.getUi().alert("¡Cálculo de 'Offer Density' completado!");
  }
}




// ==============================================================================
// === SCRIPT: calculateConsecutiveRejects (v1.1 - Refactored)                ===
// === PURPOSE: Uses the global CONFIG object for all column name references. ===
// ==============================================================================

function calculateConsecutiveRejects() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0];

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const actionColIdx = headers.indexOf(CONFIG.offer_action_fk);
  
  // Encontrar o crear la columna de destino
  let targetColIdx = headers.indexOf(CONFIG.consecutive_rejects);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.consecutive_rejects);
    headers.push(CONFIG.consecutive_rejects);
  }

  if (sessionColIdx === -1 || actionColIdx === -1) {
    Logger.log(`Índices encontrados: session=${sessionColIdx}, action=${actionColIdx}`);
    SpreadsheetApp.getUi().alert("Error: No se encontraron 'session_fk' o 'offer_action_fk'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let rejectCounter = 0; // El contador de rechazos

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const currentSession = currentRow[sessionColIdx];
    const currentAction = currentRow[actionColIdx];

    // --- LÓGICA DE REINICIO DEL CONTADOR ---
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx]) {
      rejectCounter = 0;
    }

    // El valor de esta fila es el estado del contador *antes* de la acción actual
    outputValues.push([rejectCounter]);

    // --- LÓGICA DE ACTUALIZACIÓN DEL CONTADOR (PARA LA SIGUIENTE FILA) ---
    if (currentAction === "reject") {
      rejectCounter++;
    } else if (currentAction === "accepted") {
      rejectCounter = 0;
    }
    // Si la acción es otra cosa, el contador no cambia
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("0");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'consecutive_rejects' completado!");
  }
}





// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
// === SCRIPT: calculateCycleStatistics (v1.1 - Refactored)                   ===
// === PURPOSE: Calculates rolling average and std dev for a given metric,    ===
// ===          resetting per cycle. Uses the global CONFIG object.           ===
// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function calculateCycleStatistics() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0];

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const outcomeColIdx = headers.indexOf(CONFIG.outcome_fk);
  const metricColIdx = headers.indexOf(CONFIG.dist_to_pickup_km); // La métrica a analizar
  
  // Encontrar o crear las columnas de destino
  let avgColIdx = headers.indexOf(CONFIG.cycle_avg_dtp_km);
  if (avgColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    avgColIdx = headers.length;
    sheet.getRange(1, avgColIdx + 1).setValue(CONFIG.cycle_avg_dtp_km);
    headers.push(CONFIG.cycle_avg_dtp_km);
  }
  let stdColIdx = headers.indexOf(CONFIG.cycle_std_dtp_km);
  if (stdColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    stdColIdx = headers.length;
    sheet.getRange(1, stdColIdx + 1).setValue(CONFIG.cycle_std_dtp_km);
    headers.push(CONFIG.cycle_std_dtp_km);
  }
  
  if ([sessionColIdx, outcomeColIdx, metricColIdx].includes(-1)) {
    Logger.log(`Índices: session=${sessionColIdx}, outcome=${outcomeColIdx}, metric=${metricColIdx}`);
    SpreadsheetApp.getUi().alert("Error: Una o más columnas de entrada no se encontraron en 'calculateCycleStatistics'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let currentCycleValues = []; // Almacena los valores del ciclo actual

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const previousRow = data[i - 1];

    const currentSession = currentRow[sessionColIdx];
    const previousOutcome = (i > 1) ? previousRow[outcomeColIdx] : null;
    const currentMetricValue = parseFloat(currentRow[metricColIdx]);

    // --- LÓGICA DE REINICIO DEL CICLO ---
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx] || previousOutcome === "completed") {
      currentCycleValues = [];
    }

    let cycleAvg = null;
    let cycleStd = null;

    if (!isNaN(currentMetricValue)) {
      currentCycleValues.push(currentMetricValue);
      
      cycleAvg = calculateAverage(currentCycleValues);
      cycleStd = calculateStdDev(currentCycleValues, cycleAvg);
    }
    
    // Guardar ambos resultados en el orden correcto
    outputValues.push([cycleAvg, cycleStd]);
  }
  
  if (outputValues.length > 0) {
    // Escribir los datos en bloque, pero necesitamos los índices correctos
    // Este enfoque es más seguro si las columnas no son contiguas
    const avgData = outputValues.map(row => [row[0]]);
    const stdData = outputValues.map(row => [row[1]]);

    sheet.getRange(2, avgColIdx + 1, avgData.length, 1).setValues(avgData).setNumberFormat("0.00");
    sheet.getRange(2, stdColIdx + 1, stdData.length, 1).setValues(stdData).setNumberFormat("0.00");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'Cycle Statistics' (Avg/Std) completado!");
  }
}
















// ==============================================================================
// === SCRIPT: calculateCycleTtpDtpRatio (v1.1 - Refactored)                  ===
// === PURPOSE: Calculates the rolling average of the TTP/DTP ratio per cycle,===
// ===          using the global CONFIG object.                               ===
// ==============================================================================

function calculateCycleTtpDtpRatio() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0];

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const outcomeColIdx = headers.indexOf(CONFIG.outcome_fk);
  const ttpColIdx = headers.indexOf(CONFIG.time_to_pickup_sec);
  const dtpColIdx = headers.indexOf(CONFIG.dist_to_pickup_km);
  
  // Encontrar o crear la columna de destino
  let targetColIdx = headers.indexOf(CONFIG.cycle_ttp_dtp_ratio);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.cycle_ttp_dtp_ratio);
    headers.push(CONFIG.cycle_ttp_dtp_ratio);
  }
  
  if ([sessionColIdx, outcomeColIdx, ttpColIdx, dtpColIdx].includes(-1)) {
    Logger.log(`Índices: session=${sessionColIdx}, outcome=${outcomeColIdx}, ttp=${ttpColIdx}, dtp=${dtpColIdx}`);
    SpreadsheetApp.getUi().alert("Error: Una o más columnas no se encontraron en 'calculateCycleTtpDtpRatio'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let currentCycleRatios = []; // Almacena los ratios del ciclo actual

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const previousRow = data[i - 1];

    const currentSession = currentRow[sessionColIdx];
    const previousOutcome = (i > 1) ? previousRow[outcomeColIdx] : null;
    
    const ttpValue = parseFloat(currentRow[ttpColIdx]);
    const dtpValue = parseFloat(currentRow[dtpColIdx]);

    // --- LÓGICA DE REINICIO DEL CICLO ---
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx] || previousOutcome === "completed") {
      currentCycleRatios = [];
    }

    let cycleRatioAvg = null;

    // Solo procesar si TTP es un número y DTP es un número mayor que cero
    if (!isNaN(ttpValue) && !isNaN(dtpValue) && dtpValue > 0) {
      const individualRatio = ttpValue / dtpValue;
      currentCycleRatios.push(individualRatio);
      cycleRatioAvg = calculateAverage(currentCycleRatios);
    }
    
    outputValues.push([cycleRatioAvg]);
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("0.00");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'cycle_ttp_dtp_ratio' completado!");
  }
}







// ====================================================================================
// === SCRIPT: calculateDispatchLeadTime (v3.2 - Refactored)                      ===
// === PURPOSE: Infers driver state from timestamps and uses the global CONFIG    ===
// ===          object. Assumes clean Date object inputs.                       ===
// ====================================================================================

function calculateDispatchLeadTime() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0];

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const timestampColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const completionTsColIdx = headers.indexOf(CONFIG.completed_timestamp);
  
  // Encontrar o crear la columna de destino
  let targetColIdx = headers.indexOf(CONFIG.dispatch_lead_time_sec);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.dispatch_lead_time_sec);
    headers.push(CONFIG.dispatch_lead_time_sec);
  }
  
  if ([sessionColIdx, timestampColIdx, completionTsColIdx].includes(-1)) {
    Logger.log(`Índices: session=${sessionColIdx}, timestamp=${timestampColIdx}, completion=${completionTsColIdx}`);
    SpreadsheetApp.getUi().alert("Error: Una o más columnas de entrada no se encontraron en 'calculateDispatchLeadTime'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let activeTripCompletionTime = null; // "Memoria" del viaje activo

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const currentSession = currentRow[sessionColIdx];
    const currentOfferTimestamp = currentRow[timestampColIdx];
    const currentCompletionTimestamp = currentRow[completionTsColIdx];

    let leadTime = null;

    // Reiniciar la "memoria" si es una nueva sesión
    if (i > 1 && currentSession !== data[i - 1][sessionColIdx]) {
      activeTripCompletionTime = null;
    }

    // --- LÓGICA DE ESTADO "POST-ACCIÓN" ---

    // 1. PRIMERO, CALCULAR USANDO LA MEMORIA DE LA ITERACIÓN ANTERIOR
    if (currentOfferTimestamp instanceof Date && activeTripCompletionTime instanceof Date) {
      if (currentOfferTimestamp <= activeTripCompletionTime) {
        const diffMilliseconds = activeTripCompletionTime - currentOfferTimestamp;
        leadTime = Math.round(diffMilliseconds / 1000); // Resultado en segundos
      } else {
        // La oferta llegó después de que el viaje terminó, así que reiniciamos la memoria para la siguiente iteración
        activeTripCompletionTime = null;
      }
    }
    
    outputValues.push([leadTime]); 

    // 2. DESPUÉS, ACTUALIZAR EL ESTADO PARA LA SIGUIENTE FILA
    if (currentCompletionTimestamp instanceof Date) {
      activeTripCompletionTime = currentCompletionTimestamp;
    }
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("0");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'dispatch_lead_time_sec' completado!");
  }
}











// ==============================================================================
// === SCRIPT: calculateRollingSpread (v1.5 - Refactored)                     ===
// === PURPOSE: Calculates temporally-correct rolling average of spread       ===
// ===          and uses the global CONFIG object.                            ===
// ==============================================================================

function calculateRollingSpread() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0];

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const offerTsColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const completedTsColIdx = headers.indexOf(CONFIG.completed_timestamp);
  const spreadColIdx = headers.indexOf(CONFIG.spread_percentage);
  
  // Encontrar o crear la columna de destino
  let targetColIdx = headers.indexOf(CONFIG.cycle_rolling_avg_spread);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.cycle_rolling_avg_spread);
    headers.push(CONFIG.cycle_rolling_avg_spread);
  }
  
  if ([sessionColIdx, offerTsColIdx, completedTsColIdx, spreadColIdx].includes(-1)) {
    Logger.log(`Índices: session=${sessionColIdx}, offerTs=${offerTsColIdx}, completedTs=${completedTsColIdx}, spread=${spreadColIdx}`);
    SpreadsheetApp.getUi().alert("Error: Una o más columnas de entrada no se encontraron en 'calculateRollingSpread'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let sessionCompletedTrips = []; // Memoria de objetos: {spread, completionTime}
  let lastKnownAverage = null;

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const currentSession = currentRow[sessionColIdx];
    const currentOfferTs = currentRow[offerTsColIdx];
    
    // --- LÓGICA DE REINICIO DEL CICLO ---
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx]) {
      sessionCompletedTrips = [];
      lastKnownAverage = null;
    }

    // --- LÓGICA DE ACTUALIZACIÓN DE "SABIDURÍA" ---
    if (currentOfferTs instanceof Date) {
      const knownTrips = sessionCompletedTrips.filter(trip => trip.completionTime < currentOfferTs);
      
      // Solo recalculamos el promedio si hay viajes "conocidos" en el pasado
      if (knownTrips.length > 0) {
        const knownSpreads = knownTrips.map(trip => trip.spread);
        lastKnownAverage = calculateAverage(knownSpreads);
      }
    }
    
    // Asignamos el último valor que calculamos (persiste si no hay nueva info)
    outputValues.push([lastKnownAverage]);

    // --- LÓGICA DE "APRENDER" SOBRE LA FILA ACTUAL PARA EL FUTURO ---
    const currentCompletedTs = currentRow[completedTsColIdx];
    const currentSpread = parseFloat(currentRow[spreadColIdx]);
    if (currentCompletedTs instanceof Date && !isNaN(currentSpread)) {
      sessionCompletedTrips.push({
        spread: currentSpread,
        completionTime: currentCompletedTs
      });
    }
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'cycle_rolling_avg_spread' completado!");
  }
}







// ====================================================================================
// === SCRIPT: calculateTotalAccumulatedDeadhead (v3.2 - Refactored)              ===
// === PURPOSE: Implements the final state machine for total deadhead, using the  ===
// ===          global CONFIG object and assuming clean Date object inputs.     ===
// ====================================================================================

function calculateTotalAccumulatedDeadhead() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0];

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const offerTsColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const completedTsColIdx = headers.indexOf(CONFIG.completed_timestamp);
  const startTsColIdx = headers.indexOf(CONFIG.start_timestamp);
  const outcomeColIdx = headers.indexOf(CONFIG.outcome_fk);
  const dtpColIdx = headers.indexOf(CONFIG.time_to_pickup_sec);
  const wfpColIdx = headers.indexOf(CONFIG.deadhead_wfp);
  
  // Encontrar o crear la columna de destino
  let targetColIdx = headers.indexOf(CONFIG.total_accumulated_deadhead_sec);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.total_accumulated_deadhead_sec);
    headers.push(CONFIG.total_accumulated_deadhead_sec);
  }
  
  if ([sessionColIdx, offerTsColIdx, completedTsColIdx, startTsColIdx, outcomeColIdx, dtpColIdx, wfpColIdx].includes(-1)) {
    Logger.log(`Índices: session=${sessionColIdx}, offerTs=${offerTsColIdx}, completedTs=${completedTsColIdx}, startTs=${startTsColIdx}, outcome=${outcomeColIdx}, dtp=${dtpColIdx}, wfp=${wfpColIdx}`);
    SpreadsheetApp.getUi().alert("Error: Una o más columnas no se encontraron en 'calculateTotalAccumulatedDeadhead'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  // --- Variables de Estado (La "Memoria") ---
  let accumulatedDeadhead = 0.0;
  let lastEventTimestamp = null;
  let activeTrip = { completionTime: null, wfpValue: null, wfpAdded: false, startTimestamp: null };

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const session = row[sessionColIdx];
    const offerTs = row[offerTsColIdx];

    // --- Reinicio de Sesión ---
    if (i === 1 || session !== data[i-1][sessionColIdx]) {
      accumulatedDeadhead = 0.0;
      lastEventTimestamp = offerTs instanceof Date ? offerTs : null;
      activeTrip = { completionTime: null, wfpValue: null, wfpAdded: false, startTimestamp: null };
    }

    if (offerTs instanceof Date) {
      // --- LÓGICA DE ESTADOS ---
      
      // Si el viaje activo anterior ya terminó, volvemos al estado "buscando"
      if (activeTrip.completionTime && offerTs > activeTrip.completionTime) {
        lastEventTimestamp = activeTrip.completionTime;
        activeTrip = { completionTime: null, wfpValue: null, wfpAdded: false, startTimestamp: null };
      }
      
      // ESTADO "BUSCANDO": Si no hay viaje activo...
      if (!activeTrip.completionTime) {
        if (lastEventTimestamp instanceof Date) {
          const deltaMs = offerTs - lastEventTimestamp;
          accumulatedDeadhead += (deltaMs > 0 ? deltaMs / 1000 : 0);
        }
      }
      
      // ESTADO "EN VIAJE": Comprobar si debemos añadir el WFP
      if (activeTrip.completionTime && !activeTrip.wfpAdded && activeTrip.startTimestamp && offerTs >= activeTrip.startTimestamp) {
        accumulatedDeadhead += activeTrip.wfpValue;
        activeTrip.wfpAdded = true;
      }
      
      lastEventTimestamp = offerTs;
    }

    // --- Evento de Aceptación ---
    const completedTs = row[completedTsColIdx];
    const currentOutcome = row[outcomeColIdx];
    if (completedTs instanceof Date && currentOutcome === "completed") {
      const dtpValue = parseFloat(row[dtpColIdx]) || 0;
      const wfpValue = parseFloat(row[wfpColIdx]) || 0;
      const startTs = row[startTsColIdx];
      
      accumulatedDeadhead += dtpValue; // Añadir DTP en el momento de la aceptación
      
      activeTrip = { 
        completionTime: completedTs, 
        wfpValue: wfpValue, 
        wfpAdded: false,
        startTimestamp: startTs 
      };
    }
    
    outputValues.push([accumulatedDeadhead]);
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("0");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'total_accumulated_deadhead_sec' completado!");
  }
}








// ==============================================================================
// === SCRIPT: calculateCumulativeEarnings (v1.1 - Refactored)                ===
// === PURPOSE: Calculates the temporally-correct cumulative sum of           ===
// ===          realized_fare per session. Uses the global CONFIG object.     ===
// ==============================================================================

function calculateCumulativeEarnings() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  let headers = data[0];

  // --- AHORA USA LAS CONSTANTES GLOBALES ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const offerTsColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const completedTsColIdx = headers.indexOf(CONFIG.completed_timestamp);
  const realizedFareColIdx = headers.indexOf(CONFIG.realized_fare);
  
  // Encontrar o crear la columna de destino
  let targetColIdx = headers.indexOf(CONFIG.cycle_cumulative_net_earnings);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.cycle_cumulative_net_earnings);
    headers.push(CONFIG.cycle_cumulative_net_earnings);
  }
  
  if ([sessionColIdx, offerTsColIdx, completedTsColIdx, realizedFareColIdx].includes(-1)) {
    Logger.log(`Índices: session=${sessionColIdx}, offerTs=${offerTsColIdx}, completedTs=${completedTsColIdx}, fare=${realizedFareColIdx}`);
    SpreadsheetApp.getUi().alert("Error: Una o más columnas no se encontraron en 'calculateCumulativeEarnings'. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let sessionCompletedTrips = []; // Memoria de objetos: {fare, completionTime}
  let lastCalculatedSum = 0;

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const currentSession = currentRow[sessionColIdx];
    const currentOfferTs = currentRow[offerTsColIdx];
    
    // --- LÓGICA DE REINICIO DEL CICLO ---
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx]) {
      sessionCompletedTrips = [];
      lastCalculatedSum = 0;
    }

    // --- LÓGICA DE ACTUALIZACIÓN DE "SABIDURÍA" ---
    if (currentOfferTs instanceof Date) {
      const knownTrips = sessionCompletedTrips.filter(trip => trip.completionTime < currentOfferTs);
      
      // A diferencia del promedio, aquí sumamos.
      if (knownTrips.length > 0) {
        const knownFares = knownTrips.map(trip => trip.fare);
        lastCalculatedSum = knownFares.reduce((a, b) => a + b, 0);
      } else {
        lastCalculatedSum = 0; // Si no hay viajes conocidos, la suma es 0
      }
    }
    
    // Asignamos la última suma que calculamos
    outputValues.push([lastCalculatedSum]);

    // --- LÓGICA DE "APRENDER" SOBRE LA FILA ACTUAL PARA EL FUTURO ---
    const currentCompletedTs = currentRow[completedTsColIdx];
    const currentFare = parseFloat(currentRow[realizedFareColIdx]);
    if (currentCompletedTs instanceof Date && !isNaN(currentFare)) {
      sessionCompletedTrips.push({
        fare: currentFare,
        completionTime: currentCompletedTs
      });
    }
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("$0.00"); // Formatear como moneda
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'cycle_cumulative_net_earnings' completado!");
  }
}




// ==============================================================================
// === EASTER EGG: Protocolo Cher Ami                                         ===
// ==============================================================================

function cherAmiMessage() {
  // Una lista de posibles mensajes para mostrar
  const messages = [
    "Coo coo... coo-de... 🕊️",
    "Fun Fact: Cher Ami, a pesar de recibir un disparo en el pecho y quedar ciego de un ojo, entregó con éxito el mensaje que salvó a los 194 hombres del 'Batallón Perdido'.",
    "No te preocupes, Arquitecto. Incluso cuando los datos parecen perdidos, el mensaje siempre llega. 🕊️",
    "Solo entregando los paquetes de datos, Arquitecto. Mensaje recibido. 🕊️",
    "Coo coo? 🕊️",
    "Visto Bueno (VoBo) a la misión. El mensaje fue entregado. 🕊️"
  ];

  // Elegir un mensaje al azar de la lista
  const randomIndex = Math.floor(Math.random() * messages.length);
  const selectedMessage = messages[randomIndex];

  // Mostrar el mensaje en una alerta
  SpreadsheetApp.getUi().alert("Un Mensaje de Cher Ami", selectedMessage, SpreadsheetApp.getUi().ButtonSet.OK);
}



// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
// === SCRIPT: calculate_eph_complete_ML (v3.1 - CONFIG Integrated)            ===
// === PURPOSE: Autonomous engine that correctly uses the global CONFIG object.===
// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

function calculate_eph_complete_ML() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  const headers = data[0];

  // --- Encontrar índices de columnas usando el objeto CONFIG ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const offerTsColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const completedTsColIdx = headers.indexOf(CONFIG.completed_timestamp);
  const upfrontFareColIdx = headers.indexOf(CONFIG.upfront_fare);
  const ttpColIdx = headers.indexOf(CONFIG.time_to_pickup_sec);
  const estTimeColIdx = headers.indexOf(CONFIG.est_trip_time_sec);
  const spreadColIdx = headers.indexOf(CONFIG.spread_percentage);
  const wfpColIdx = headers.indexOf(CONFIG.deadhead_wfp);
  const lfrColIdx = headers.indexOf(CONFIG.time_since_last_offer);
  const historicalSpreadColIdx = headers.indexOf(CONFIG.cycle_rolling_avg_spread);
  
  let targetColIdx = headers.indexOf(CONFIG.eph_complete_ML);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.eph_complete_ML);
  }
  
  // --- Comprobación Robusta de Índices ---
  const requiredIndices = {
    session_fk: sessionColIdx, offer_timestamp: offerTsColIdx, completed_timestamp: completedTsColIdx,
    upfront_fare: upfrontFareColIdx, time_to_pickup_sec: ttpColIdx, est_trip_time_sec: estTimeColIdx,
    spread_percentage: spreadColIdx, deadhead_wfp: wfpColIdx, time_since_last_offer: lfrColIdx,
    cycle_rolling_avg_spread: historicalSpreadColIdx
  };

  const missingCols = Object.keys(requiredIndices).filter(key => requiredIndices[key] === -1);
  if (missingCols.length > 0) {
    SpreadsheetApp.getUi().alert(`Error: No se encontraron las siguientes columnas: ${missingCols.join(", ")}. Revisa CONFIG y los encabezados.`);
    return;
  }
  
  const outputValues = [];
  let sessionCompletedTrips_WFP = [];
  
  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const currentSession = currentRow[sessionColIdx];
    const currentOfferTs = parseTimestamp_Universal(currentRow[offerTsColIdx]);
    
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx]) {
      sessionCompletedTrips_WFP = [];
    }

    let calculated_eph_complete = null;

    if (currentOfferTs) {
      const knownWFPs = sessionCompletedTrips_WFP
        .filter(trip => trip.completionTime < currentOfferTs)
        .map(trip => trip.wfp);
      const wfp_rolling_avg_sec = calculateAverage(knownWFPs) || 0;

      const historical_spread_avg = parseFloat(currentRow[historicalSpreadColIdx]);
      const upfrontFare = parseFloat(currentRow[upfrontFareColIdx]);
      const ttp_actual_sec = parseFloat(currentRow[ttpColIdx]);
      const est_time_actual_sec = parseFloat(currentRow[estTimeColIdx]);
      const lfr_duration = currentRow[lfrColIdx];
      const lfr_real_so_far_sec = (typeof lfr_duration === 'number' && lfr_duration > 0) ? lfr_duration * 86400 : 0;
      
      if (!isNaN(upfrontFare) && !isNaN(historical_spread_avg) && !isNaN(ttp_actual_sec) && !isNaN(est_time_actual_sec)) {
        const ganancia_estimada = upfrontFare * historical_spread_avg;
        const tiempo_total_estimado_sec = lfr_real_so_far_sec + ttp_actual_sec + wfp_rolling_avg_sec + est_time_actual_sec;
        if (tiempo_total_estimado_sec > 0) {
          calculated_eph_complete = ganancia_estimada / (tiempo_total_estimado_sec / 3600);
        }
      }
    }
    
    outputValues.push([calculated_eph_complete]);

    const completedTs = parseTimestamp_Universal(currentRow[completedTsColIdx]);
    if (completedTs) {
      const wfp = parseFloat(currentRow[wfpColIdx]);
      const spread = parseFloat(currentRow[spreadColIdx]); // Necesitamos el spread para el futuro
      if (!isNaN(wfp) && !isNaN(spread)) {
          sessionCompletedTrips_WFP.push({
              wfp: wfp,
              spread: spread, // La memoria ahora debe guardar ambos
              completionTime: completedTs
          });
      }
    }
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("$0.00");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'eph_complete_ML' (v3.1) completado!");
  }
}







// ==============================================================================
// === SCRIPT: calculate_eph_realized_EDA_ONLY (v1.1)                         ===
// === PURPOSE: Calculates ONLY the 'eph_realized_EDA' feature.             ===
// ==============================================================================

function calculate_eph_realized_EDA() {
  // --- Setup: Use global CONFIG ---
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  const headers = data[0];

  // --- Find all necessary column indices from global CONFIG ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const outcomeColIdx = headers.indexOf(CONFIG.outcome_fk);
  const upfrontFareColIdx = headers.indexOf(CONFIG.upfront_fare);
  const realizedFareColIdx = headers.indexOf(CONFIG.realized_fare);
  const estTimeColIdx = headers.indexOf(CONFIG.est_trip_time_sec);
  const spreadColIdx = headers.indexOf(CONFIG.spread_percentage); // <<<--- Usando la columna original

  // --- Define and add the single target column ---
  const TARGET_COL_NAME = CONFIG.eph_realized_EDA;
  let targetColIdx = headers.indexOf(TARGET_COL_NAME);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(TARGET_COL_NAME);
  }
  
  // --- Check for missing input columns ---
  const requiredInputs = {
      session_fk: sessionColIdx, outcome_fk: outcomeColIdx, upfront_fare: upfrontFareColIdx,
      realized_fare: realizedFareColIdx, est_trip_time_sec: estTimeColIdx,
      spread_percentage: spreadColIdx
  };
  const missingCols = Object.keys(requiredInputs).filter(key => requiredInputs[key] === -1);
  if (missingCols.length > 0) {
      SpreadsheetApp.getUi().alert(`Error: Faltan columnas de entrada: ${missingCols.join(", ")}`);
      return;
  }
  
  // --- Step 1: Pre-calculate session average spreads ---
  const sessionSpreads = {};
  for (let i = 1; i < data.length; i++) {
    const session = data[i][sessionColIdx];
    const outcome = data[i][outcomeColIdx];
    const spread = parseFloat(data[i][spreadColIdx]);
    if (outcome === "completed" && !isNaN(spread)) {
      if (!sessionSpreads[session]) { sessionSpreads[session] = []; }
      sessionSpreads[session].push(spread);
    }
  }

  const sessionAverages = {};
  for (const session in sessionSpreads) {
    sessionAverages[session] = calculateAverage(sessionSpreads[session]);
  }
  
  // --- Step 2: Main loop to calculate the single feature ---
  const outputValues = [];
  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const session = currentRow[sessionColIdx];
    const outcome = currentRow[outcomeColIdx];
    const upfrontFare = parseFloat(currentRow[upfrontFareColIdx]);
    const realizedFare = parseFloat(currentRow[realizedFareColIdx]);
    const estTimeSec = parseFloat(currentRow[estTimeColIdx]);
    
    let calculated_eph_realized = null;
    let fareToUse = null;

    if (outcome === "completed") {
      fareToUse = realizedFare;
    } else if (sessionAverages[session]) {
      fareToUse = upfrontFare * sessionAverages[session];
    }

    if (fareToUse !== null && !isNaN(fareToUse) && estTimeSec > 0) {
      calculated_eph_realized = fareToUse / (estTimeSec / 3600);
    }
    
    outputValues.push([calculated_eph_realized]);
  }

  // --- Step 3: Write results back to the sheet ---
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("$0.00");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'eph_realized_EDA' (SOLAMENTE) completado!");
  }
}




// ==============================================================================
// === SCRIPT: calculate_eph_complete_EDA (v1.1 - Clean & Correct)            ===
// === PURPOSE: Calculates the post-facto 'eph_complete' for EDA. It uses a   ===
// ===          hybrid logic for fares and the final accumulated deadhead for ===
// ===          the total time cost.                                          ===
// ==============================================================================

function calculate_eph_complete_EDA() {
  // --- Setup: Use global CONFIG ---
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  const headers = data[0];

  // --- Find all column indices from global CONFIG ---
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const outcomeColIdx = headers.indexOf(CONFIG.outcome_fk);
  const upfrontFareColIdx = headers.indexOf(CONFIG.upfront_fare);
  const realizedFareColIdx = headers.indexOf(CONFIG.realized_fare);
  const estTimeColIdx = headers.indexOf(CONFIG.est_trip_time_sec);
  const spreadColIdx = headers.indexOf(CONFIG.spread_percentage);
  const accumulatedDeadheadColIdx = headers.indexOf(CONFIG.total_accumulated_deadhead_sec);

  // --- Define and add the single target column ---
  const TARGET_COL_NAME = CONFIG.eph_complete_EDA;
  let targetColIdx = headers.indexOf(TARGET_COL_NAME);
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(TARGET_COL_NAME);
  }
  
  // --- Check for missing input columns ---
  const requiredInputs = {
      session_fk: sessionColIdx, outcome_fk: outcomeColIdx, upfront_fare: upfrontFareColIdx,
      realized_fare: realizedFareColIdx, est_trip_time_sec: estTimeColIdx,
      spread_percentage: spreadColIdx, total_accumulated_deadhead_sec: accumulatedDeadheadColIdx
  };
  const missingCols = Object.keys(requiredInputs).filter(key => requiredInputs[key] === -1);
  if (missingCols.length > 0) {
      SpreadsheetApp.getUi().alert(`Error: Faltan columnas de entrada para EDA: ${missingCols.join(", ")}`);
      return;
  }
  
  // --- Step 1: Pre-calculate session average spreads (for imputation) ---
  const sessionSpreads = {};
  for (let i = 1; i < data.length; i++) {
    const session = data[i][sessionColIdx];
    const outcome = data[i][outcomeColIdx];
    const spread = parseFloat(data[i][spreadColIdx]);
    if (outcome === "completed" && !isNaN(spread)) {
      if (!sessionSpreads[session]) { sessionSpreads[session] = []; }
      sessionSpreads[session].push(spread);
    }
  }
  const sessionAverages = {};
  for (const session in sessionSpreads) {
    sessionAverages[session] = calculateAverage(sessionSpreads[session]);
  }
  
  // --- Step 2: Main loop to calculate the single feature ---
  const outputValues = [];
  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const session = currentRow[sessionColIdx];
    const outcome = currentRow[outcomeColIdx];
    const upfrontFare = parseFloat(currentRow[upfrontFareColIdx]);
    const realizedFare = parseFloat(currentRow[realizedFareColIdx]);
    const estTimeSec = parseFloat(currentRow[estTimeColIdx]);
    const accumulatedDeadhead = parseFloat(currentRow[accumulatedDeadheadColIdx]);
    
    let calculated_eph_complete = null;
    
    // 1. Determine the fare to use (real or imputed)
    let fareToUse = null;
    if (outcome === "completed") {
      fareToUse = realizedFare;
    } else if (sessionAverages[session]) {
      fareToUse = upfrontFare * sessionAverages[session];
    }

    // 2. Determine the total time to use
    // For EDA, the total time is the 'deadhead accumulated so far' + the estimated trip time.
    const totalCycleTimeSec = accumulatedDeadhead + estTimeSec;

    // 3. Calculate the EPH
    if (fareToUse !== null && !isNaN(fareToUse) && totalCycleTimeSec > 0) {
      calculated_eph_complete = fareToUse / (totalCycleTimeSec / 3600);
    }
    
    outputValues.push([calculated_eph_complete]);
  }

  // --- Step 3: Write results back to the sheet ---
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("$0.00");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'eph_complete_EDA' (SOLAMENTE) completado!");
  }
}



// ==============================================================================
// === SCRIPT: calculateRollingTimeDelta (v1.0)                               ===
// === PURPOSE: Calculates the rolling average of 'delta_time_sec' for each   ===
// ===          search cycle, using only past completed trip data to          ===
// ===          prevent data leakage.                                         ===
// ==============================================================================

function calculateRollingTimeDelta() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`Error: No se pudo encontrar la hoja "${CONFIG.sheetName}"`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  const headers = data[0];

  // Encontrar índices de columnas desde CONFIG
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const offerTsColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const completedTsColIdx = headers.indexOf(CONFIG.completed_timestamp);
  const deltaColIdx = headers.indexOf(CONFIG.delta_time_sec); // <<<--- El nuevo Input
  
  let targetColIdx = headers.indexOf(CONFIG.historical_time_delta_sec); // <<<--- El nuevo Output
  if (targetColIdx === -1) {
    sheet.insertColumnsAfter(headers.length, 1);
    targetColIdx = headers.length;
    sheet.getRange(1, targetColIdx + 1).setValue(CONFIG.historical_time_delta_sec);
  }
  
  if ([sessionColIdx, offerTsColIdx, completedTsColIdx, deltaColIdx].includes(-1)) {
    SpreadsheetApp.getUi().alert("Error: Una o más columnas no se encontraron para RollingTimeDelta. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let sessionCompletedTrips = []; // Memoria de objetos: {delta, completionTime}
  let lastKnownAverage = null;

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const currentSession = currentRow[sessionColIdx];
    const currentOfferTs = parseTimestamp_Universal(currentRow[offerTsColIdx]);
    
    // --- LÓGICA DE REINICIO DEL CICLO ---
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx]) {
      sessionCompletedTrips = [];
      lastKnownAverage = null;
    }

    // --- LÓGICA DE ACTUALIZACIÓN DE "SABIDURÍA" ---
    if (currentOfferTs) {
      const knownTrips = sessionCompletedTrips.filter(trip => trip.completionTime < currentOfferTs);
      
      if (knownTrips.length > 0) {
        const knownDeltas = knownTrips.map(trip => trip.delta);
        lastKnownAverage = calculateAverage(knownDeltas); // Reusa tu función de ayuda
      }
    }
    
    // --- ASIGNACIÓN DE VALOR A LA FILA ACTUAL ---
    outputValues.push([lastKnownAverage]);

    // --- LÓGICA DE "APRENDER" SOBRE LA FILA ACTUAL PARA EL FUTURO ---
    const currentCompletedTs = parseTimestamp_Universal(currentRow[completedTsColIdx]);
    const currentDelta = parseFloat(currentRow[deltaColIdx]);
    if (currentCompletedTs && !isNaN(currentDelta)) {
      sessionCompletedTrips.push({
        delta: currentDelta,
        completionTime: currentCompletedTs
      });
    }
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("0.00"); // Formateado como decimal
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'historical_time_delta_sec' completado!");
  }
}





// ==============================================================================
// === SCRIPT: calculateRollingTrafficIndex (v1.0)                            ===
// === PURPOSE: Calculates the rolling average of 'realized_traffic_index'    ===
// ===          for each search cycle, using only past completed trip data.   ===
// ==============================================================================

function calculateRollingTrafficIndex() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  if (!sheet) { /* ... */ return; }

  const dataRange = sheet.getDataRange();
  const data = dataRange.getValues();
  const headers = data[0];

  // Encontrar índices de columnas desde CONFIG
  const sessionColIdx = headers.indexOf(CONFIG.session_fk);
  const offerTsColIdx = headers.indexOf(CONFIG.offer_timestamp);
  const completedTsColIdx = headers.indexOf(CONFIG.completed_timestamp);
  const trafficIndexColIdx = headers.indexOf(CONFIG.realized_traffic_index); // <<<--- Input
  
  let targetColIdx = headers.indexOf(CONFIG.historical_rolling_avg_traffic_index); // <<<--- Output
  if (targetColIdx === -1) { /* ... (código para añadir columna) ... */ }
  
  if ([sessionColIdx, offerTsColIdx, completedTsColIdx, trafficIndexColIdx].includes(-1)) {
    SpreadsheetApp.getUi().alert("Error: Una o más columnas no se encontraron para RollingTrafficIndex. Revisa la CONFIGURACIÓN.");
    return;
  }
  
  const outputValues = [];
  let sessionCompletedTrips = []; // Memoria de objetos: {index, completionTime}
  let lastKnownAverage = null;

  for (let i = 1; i < data.length; i++) {
    const currentRow = data[i];
    const currentSession = currentRow[sessionColIdx];
    const currentOfferTs = parseTimestamp_Universal(currentRow[offerTsColIdx]);
    
    // --- LÓGICA DE REINICIO ---
    if (i === 1 || currentSession !== data[i - 1][sessionColIdx]) {
      sessionCompletedTrips = [];
      lastKnownAverage = null;
    }

    // --- LÓGICA DE "SABIDURÍA" ---
    if (currentOfferTs) {
      const knownTrips = sessionCompletedTrips.filter(trip => trip.completionTime < currentOfferTs);
      if (knownTrips.length > 0) {
        const knownIndices = knownTrips.map(trip => trip.index);
        lastKnownAverage = calculateAverage(knownIndices); // Reusa tu función de ayuda
      }
    }
    
    // --- ASIGNACIÓN ---
    outputValues.push([lastKnownAverage]);

    // --- LÓGICA DE "APRENDER" ---
    const currentCompletedTs = parseTimestamp_Universal(currentRow[completedTsColIdx]);
    const currentTrafficIndex = parseFloat(currentRow[trafficIndexColIdx]);
    if (currentCompletedTs && !isNaN(currentTrafficIndex)) {
      sessionCompletedTrips.push({
        index: currentTrafficIndex,
        completionTime: currentCompletedTs
      });
    }
  }
  
  if (outputValues.length > 0) {
    sheet.getRange(2, targetColIdx + 1, outputValues.length, 1)
         .setValues(outputValues)
         .setNumberFormat("0.00");
    
    SpreadsheetApp.getUi().alert("¡Cálculo de 'historical_rolling_avg_traffic_index' completado!");
  }
}







// --- FUNCIÓN EXTRA: Menú personalizado (con Cher Ami Activado) ---
function onOpen() {
  SpreadsheetApp.getUi()
      .createMenu('🤖 Scripts Opus')
      .addItem('Calcular Time Since PREVIOUS Offer', 'calculateTimeSincePreviousOffer')
      .addItem('Calcular Offer Density', 'calculateOfferDensity')
      .addItem('Calcular Consecutive Rejects', 'calculateConsecutiveRejects')
      .addSeparator()
      .addItem('Calcular Cycle Statistics (Avg/Std)', 'calculateCycleStatistics')
      .addItem('Calcular Cycle TTP/DTP Ratio', 'calculateCycleTtpDtpRatio')
      .addSeparator()
      .addItem('Calcular Dispatch Lead Time', 'calculateDispatchLeadTime')
      .addSeparator()
      .addItem('Calcular Rolling Average Spread', 'calculateRollingSpread')
      .addItem('Calcular Total Accumulated Deadhead', 'calculateTotalAccumulatedDeadhead')
      .addItem('Calcular Cumulative Earnings', 'calculateCumulativeEarnings')
      .addSeparator()
      .addItem('Message Received... (Cher Ami)', 'cherAmiMessage')
      .addSeparator()
      .addItem('Calcular EPH Complete (ML)', 'calculate_eph_complete_ML')
      .addSeparator()
      .addItem('Calcular EPH Realized (EDA)', 'calculate_eph_realized_EDA')
      .addSeparator()
      .addItem('Calcular Rolling Time Delta', 'calculateRollingTimeDelta')
      .addSeparator()
      .addItem('Calcular Rolling Traffic Index', 'calculateRollingTrafficIndex')
      .addToUi();
}