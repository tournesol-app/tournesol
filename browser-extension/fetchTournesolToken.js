async function updateAccessToken() {
  const raw_state = JSON.parse(localStorage.getItem('persist:root')) || {};
  const token = JSON.parse(raw_state.token) || {};
  const access_token = token.access_token

  chrome.runtime.sendMessage(
    {message: "extAccessTokenNeeded"},
    (resp) => {
      if (resp.access_token !== access_token) {
        chrome.storage.local.set({access_token: access_token || null});

        if (access_token) {
          chrome.runtime.sendMessage({
            message: 'accessTokenRefreshed',
          });
        }
      }
    }
  )
}

updateAccessToken();

chrome.runtime.onMessage.addListener(() => {
  // setTimeout seems to be necessary here, as the localStorage
  // (where the access token is persisted) is written asynchronously.
  setTimeout(updateAccessToken)
});
