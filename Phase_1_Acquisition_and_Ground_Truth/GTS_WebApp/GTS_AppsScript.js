// Code.gs - Versión para GTS-Streamlit
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    // El script ahora apunta a la hoja "data" de la nueva GSheet.
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("data");
    
    if (!sheet) {
      throw new Error("Sheet 'data' not found.");
    }

    const newRow = [
      new Date(),
      data.timestamp || null, data.rideId || null,
      data.status || null, data.latitude || null,
      data.longitude || null, data.address || null,
      data.upfrontFare || null, data.realizedFare || null
    ];
    sheet.appendRow(newRow);
    return ContentService.createTextOutput(JSON.stringify({ 'status': 'success' }));
  } catch (error) {
    Logger.log("Error in doPost: " + error.toString());
    return ContentService.createTextOutput(JSON.stringify({ 'status': 'error' }));
  }
}

