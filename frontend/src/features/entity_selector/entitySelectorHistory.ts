import { SuggestionHistory } from 'src/features/suggestions/suggestionHistory';
import { autoSuggestionPool } from 'src/features/suggestions/suggestionPool';

export const selectorAHistory = new SuggestionHistory(autoSuggestionPool);
export const selectorBHistory = new SuggestionHistory(autoSuggestionPool);
const allSelectorsHistory = [selectorAHistory, selectorBHistory];

export const clearEntitySelectorsHistory = () => {
  allSelectorsHistory.forEach((history) => history.clear());
};
