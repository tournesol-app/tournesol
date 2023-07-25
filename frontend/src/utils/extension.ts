export const isMobileDevice = () => {
  if (navigator.userAgent.includes('Mobile')) return true;
  return false;
};

export const getWebBrowser = () => {
  if (navigator.userAgent.includes('Chrome/')) return 'chrome';
  if (navigator.userAgent.includes('Chromium/')) return 'chromium';
  if (navigator.userAgent.includes('Firefox/')) return 'firefox';
  return 'other';
};

export const getWebExtensionUrl = (browser?: string) => {
  const browserFamily = browser ?? getWebBrowser();
  if (browserFamily === 'other') {
    return undefined;
  }
  if (browserFamily === 'firefox') {
    return 'https://addons.mozilla.org/en-US/firefox/addon/tournesol-extension/';
  }
  return 'https://chrome.google.com/webstore/detail/tournesol-extension/nidimbejmadpggdgooppinedbggeacla';
};
