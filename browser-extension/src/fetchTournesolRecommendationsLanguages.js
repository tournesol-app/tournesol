/**
 * Save the recommendations languages from the Tournesol localStorage to the extension
 * local storage.
 */

function saveRecommendationsLanguages(recommendationsLanguages) {
  chrome.storage.local.set({ recommendationsLanguages });
}

function updateRecommendationsLanguages() {
  const recommendationsLanguages = localStorage.getItem(
    'recommendationsLanguages'
  );
  saveRecommendationsLanguages(recommendationsLanguages);
}

function handleRecommendationsLanguagesChange(event) {
  const { detail } = event;
  const { recommendationsLanguages } = detail;
  saveRecommendationsLanguages(recommendationsLanguages);
}

updateRecommendationsLanguages();

document.addEventListener(
  'tournesol:recommendationsLanguagesChange',
  handleRecommendationsLanguagesChange
);
