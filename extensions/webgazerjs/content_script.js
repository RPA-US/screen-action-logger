import * as webgazer from './assets/js/webgazer/webgazer.js';
import * as JSZip from './libs/jszip.min.js';

// this array will store all the eye movements
 var gaze_points = [];
 var gaze_properties = {};
 let isFirstExecution = true;

 // start recording
 function recordGaze() {
     webgazer.setGazeListener(function (data, elapsedTime) {
         if (data == null) {
             return;
         }

         if(isFirstExecution){
             gaze_properties = {
                 "SlideShowStartDateTime": new Date().toISOString(),
                 "TimeZone": Intl.DateTimeFormat().resolvedOptions().timeZone
             };
             isFirstExecution = false;
         };
         var coordX = parseFloat(data.x.toFixed(2));
         var coordY = parseFloat(data.y.toFixed(2));
         var timestamp = Date.now();
         
         var UTCdate = new Date().toISOString().slice(0, -1);;
         var timezoneISO = Intl.DateTimeFormat().resolvedOptions().timeZone;

         var save_url = "http://127.0.0.1:8000/"+"?x="+coordX+";y="+coordY;
         // var temp_image = new Image();

         // temp_image.src= save_url;
         gaze_points.push([coordX, coordY, timestamp,UTCdate]);

     }).begin();
 }

 // exporting data to .csv file
 function saveGaze() {
     //Ajustar timestamps de cara a ScreenRPA
     console.log(gaze_points);
     if (gaze_points.length > 0) {
         // Tomar el primer timestamp como referencia
         let x = gaze_points[0][2];
         // Actualizar todos los timestamps en el array
         for (let i = 0; i < gaze_points.length; i++) {
             gaze_points[i][2] = gaze_points[i][2] - x;
         }
         // Establecer el primer timestamp a 1
         gaze_points[0][2] = 1;
         }

     //Crear zip con .csv y .json
     const zip = new JSZip();
     //Crear csv
     var csv = 'Gaze X,Gaze Y,Timestamp,UTCdate\n';
     gaze_points.forEach(function (row) {
         csv += row.join(',');
         csv += "\n";
     });

     //Crear json
     // var timezone = new Date().getTimezoneOffset();
     
     // var fechaUTC = new Date().toISOString();
     // var timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
     // const jsonData = {
     //     "SlideShowStartDateTime": fechaUTC,
     //     "TimeZone": timezone};
     const jsonString = JSON.stringify(gaze_properties);

     //Guardar archivos en zip
     zip.file("webgazer_gazeData.csv", csv);
     zip.file("webgazer_properties.json", jsonString);

     //Descargar zip
     zip.generateAsync({type:"blob"}).then(function(blob) {
         const enlaceDescarga = document.createElement('a');
         enlaceDescarga.href = URL.createObjectURL(blob);
         enlaceDescarga.target = '_blank';
         enlaceDescarga.download = 'gazeData.zip';
         enlaceDescarga.click();
     });

     //Guardar CSV antiguo
     // var hiddenElement = document.createElement('a');
     // hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
     // hiddenElement.target = '_blank';
     // hiddenElement.download = 'gazeData.csv';
     // hiddenElement.click();
 }

 function resume() {
     webgazer.resume();
 }

 function pause() {
     webgazer.pause();
 }

//To Do Websocket and API