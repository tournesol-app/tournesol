document.addEventListener("DOMContentLoaded", (event) => {
  const IFRAME_ID = 'x-tournesol-iframe-inner';
  const REFRESH_BUTTON_ID = 'action-refresh-iframe';


  const enableRefreshButton = function enableRefreshButton() {
    const refresh = document.getElementById(REFRESH_BUTTON_ID);
    refresh.removeAttribute('disabled');
  }

  const refreshIframe = function refreshIframe() {
    const iframe = document.getElementById(IFRAME_ID);
    const refresh = document.getElementById(REFRESH_BUTTON_ID);

    refresh.disabled = true;
    iframe.addEventListener('load', enableRefreshButton);
    iframe.src = iframe.src;
  }

  const refresh = document.getElementById(REFRESH_BUTTON_ID);
  refresh.onclick = refreshIframe;
});
