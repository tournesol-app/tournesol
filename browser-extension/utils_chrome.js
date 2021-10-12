chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    details.requestHeaders.push({name: 'Referer', value:'https://tournesol.app/'});
    return {requestHeaders: details.requestHeaders};
  },
  {urls: ["https://tournesol.app/*"]},
  ["blocking", "requestHeaders", "extraHeaders"]
);