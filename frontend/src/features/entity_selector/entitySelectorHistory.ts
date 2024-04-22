import { SuggestionHistory } from 'src/features/suggestions/suggestionHistory';

export const selectorAHistory = new SuggestionHistory();
export const selectorBHistory = new SuggestionHistory();
const allSelectorsHistory = [selectorAHistory, selectorBHistory];

export const clearEntitySelectorsHistory = () => {
  allSelectorsHistory.forEach((history) => history.clear());
};
