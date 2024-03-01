// chrome.browserAction.onClicked.addListener(function(activeTab) {
//     var newURL = "chrome-extension://"+chrome.runtime.id+"/src/prueba.html";
//     chrome.tabs.create({ url: newURL });
// });

document.addEventListener('DOMContentLoaded', function() {
    var openProjectButton = document.getElementById('openProject');
    openProjectButton.addEventListener('click', function() {
      chrome.tabs.create({ url: 'ruta_a_tu_proyecto.html' });
    });
  });