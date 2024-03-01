
document.addEventListener('DOMContentLoaded', function() {
    var openProjectButton = document.getElementById('openProject');
    openProjectButton.addEventListener('click', function() {
      chrome.tabs.create({ url: 'webgazer.html' });
    });
  });