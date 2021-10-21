const raw_state = JSON.parse(localStorage.getItem('persist:root'))
const token = JSON.parse(raw_state.token)
const access_token = token.access_token
console.log(access_token)
chrome.storage.local.set({access_token: access_token}, () => {
  console.log("Saved tournesol token in extension")
});