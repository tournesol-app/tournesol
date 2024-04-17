import { UidHistory } from 'src/features/suggestions/uidHistory';

export const selectorAHistory = new UidHistory();
export const selectorBHistory = new UidHistory();
const allSelectorsHistory = [selectorAHistory, selectorBHistory];

export const clearEntitySelectorsHistory = () => {
  allSelectorsHistory.forEach((history) => history.clear());
};
