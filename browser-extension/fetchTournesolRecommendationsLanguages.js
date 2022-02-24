/**
 * Save the recommendations languages from the Tournesol localStorage to the extension
 * local storage.
 */
function updateRecommendationsLanguages() {
  const recommendationsLanguages = localStorage.getItem('recommendationsLanguages')
  chrome.storage.local.set({recommendationsLanguages});
}

updateRecommendationsLanguages();
