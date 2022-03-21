/**
 * Save the access token from the Tournesol localStorage to the extension
 * local storage.
 *
 * Send message `accessTokenRefreshed` when:
 *  - a Tournesol's access token is found
 *  - a Tournesol's access token is != than the one currently store in the
 *    extension local storage
 */
function updateAccessToken() {
  const rawState = JSON.parse(localStorage.getItem('persist:root')) || {};
  const token = JSON.parse(rawState.token) || {};
  const tournesolAccessToken = token.access_token;

  chrome.runtime.sendMessage(
    // Ask for the current extension's access token
    { message: 'extAccessTokenNeeded' },
    (resp) => {
      if (resp.access_token !== tournesolAccessToken) {
        chrome.storage.local.set({
          access_token: tournesolAccessToken || null,
        });

        // Inform the background script that a new Tournesol's access token is
        // available. It allows the extension to not display the Tournesol log
        // in form, when only a token refresh is needed.
        if (tournesolAccessToken) {
          chrome.runtime.sendMessage({
            message: 'accessTokenRefreshed',
          });
        }
      }
    }
  );
}

updateAccessToken();

chrome.runtime.onMessage.addListener(() => {
  // setTimeout seems to be necessary here, as the localStorage
  // (where the access token is persisted) is written asynchronously.
  setTimeout(updateAccessToken);
});
