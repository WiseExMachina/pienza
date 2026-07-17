/**
 * Geocodifica direcciones en lotes para evitar el time-out de ejecución.
 */
function geocodeRawRequests_BATCH() {
  const sheetName = 'raw_requests_polished'; // MODIFIQUE ESTO CON EL NOMBRE CORRECTO DE SU HOJA
  const BATCH_SIZE = 20; // Guardará el progreso cada 20 filas procesadas.

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    SpreadsheetApp.getUi().alert(`No se encontró la hoja: ${sheetName}`);
    return;
  }

  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();
  const headers = values[0];

  const indices = {
    pickupAddr: headers.indexOf('Pickup Location'),
    pickupLat: headers.indexOf('Pickup_Latitude'),
    pickupLng: headers.indexOf('Pickup_Longitude'),
    dropoffAddr: headers.indexOf('Dropoff Location'),
    dropoffLat: headers.indexOf('Dropoff_Latitude'),
    dropoffLng: headers.indexOf('Dropoff_Longitude')
  };

  if (Object.values(indices).includes(-1)) {
    SpreadsheetApp.getUi().alert('Error: Faltan columnas. Verifique los nombres.');
    return;
  }

  let processedInBatch = 0;
  for (let i = 1; i < values.length; i++) {
    let rowModified = false;

    // 1. Geocodificar Pickup
    if (values[i][indices.pickupAddr] && !values[i][indices.pickupLat]) {
      geocodeAddress(values, i, indices.pickupAddr, indices.pickupLat, indices.pickupLng, 'Pickup');
      rowModified = true;
    }

    // 2. Geocodificar Dropoff
    if (values[i][indices.dropoffAddr] && !values[i][indices.dropoffLat]) {
      geocodeAddress(values, i, indices.dropoffAddr, indices.dropoffLat, indices.dropoffLng, 'Dropoff');
      rowModified = true;
    }

    if (rowModified) {
      processedInBatch++;
    }

    // --- NUEVA LÓGICA DE BATCHING ---
    if (processedInBatch >= BATCH_SIZE) {
      // Escribir el lote actual en la hoja para guardar el progreso
      sheet.getRange(1, 1, values.length, values[0].length).setValues(values);
      SpreadsheetApp.flush(); // Asegura que la escritura se complete antes de continuar
      Logger.log(`--- LOTE GUARDADO. ${processedInBatch} filas procesadas. ---`);
      processedInBatch = 0; // Reiniciar el contador del lote
    }
  }

  // --- Escritura final para cualquier remanente ---
  sheet.getRange(1, 1, values.length, values[0].length).setValues(values);
  SpreadsheetApp.getUi().alert('Proceso de geocodificación completado.');
}


function geocodeAddress(values, rowIndex, addrIndex, latIndex, lngIndex, type) {
  // Esta función auxiliar no necesita cambios.
  const address = values[rowIndex][addrIndex];
  try {
    const geocoder = Maps.newGeocoder().geocode(address);
    if (geocoder.status === 'OK' && geocoder.results.length > 0) {
      const location = geocoder.results[0].geometry.location;
      values[rowIndex][latIndex] = location.lat;
      values[rowIndex][lngIndex] = location.lng;
      Logger.log(`Fila ${rowIndex + 1} (${type}): Éxito para '${address}'`);
    } else {
      Logger.log(`Fila ${rowIndex + 1} (${type}): No se encontraron resultados para '${address}' (${geocoder.status})`);
    }
    Utilities.sleep(1000);
  } catch (e) {
    Logger.log(`Fila ${rowIndex + 1} (${type}): Error - ${e.message}`);
  }
}
