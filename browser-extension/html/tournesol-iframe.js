document.addEventListener("DOMContentLoaded", (event) => {
  const IFRAME_ID = 'x-tournesol-iframe-inner';
  const REFRESH_BUTTON_ID = 'action-refresh-iframe';

  const BUTTONS_INITIAL_OPACITY = '1';
  const BUTTONS_DISABLED_OPACITY = '0.4';

  const enableRefreshButton = function enableRefreshButton() {
    const refresh = document.getElementById(REFRESH_BUTTON_ID);
    refresh.removeAttribute('disabled');
    refresh.style.opacity = BUTTONS_INITIAL_OPACITY;
  }

  const refreshIframe = function refreshIframe() {
    const iframe = document.getElementById(IFRAME_ID);
    const refresh = document.getElementById(REFRESH_BUTTON_ID);

    refresh.disabled = true;
    refresh.style.opacity = BUTTONS_DISABLED_OPACITY;
    iframe.addEventListener('load', enableRefreshButton);
    iframe.src = iframe.src;
  }

  const refresh = document.getElementById(REFRESH_BUTTON_ID);
  refresh.onclick = refreshIframe;
});
