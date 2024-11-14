import { useMemo } from 'react';
import { useSelector } from 'react-redux';

import { selectSettings } from 'src/features/settings/userSettingsSlice';

import { useCurrentPoll } from './useCurrentPoll';

/**
 * Return a list of PollCriteria ordered by the user's preferences.
 */
export const useOrderedCriteria = () => {
  const { criterias: pollCriteria } = useCurrentPoll();

  const userSettings = useSelector(selectSettings)?.settings;
  const orderedByPreferences = userSettings.videos?.comparison__criteria_order;

  const orderedCriteria = useMemo(() => {
    const remainingCriteria = [...pollCriteria];
    const results = [remainingCriteria[0]];
    remainingCriteria.shift();

    if (orderedByPreferences != undefined) {
      orderedByPreferences.forEach((critName) => {
        const found = remainingCriteria.findIndex(
          (pollCrit) => pollCrit.name === critName
        );

        if (found !== -1) {
          results.push(remainingCriteria.splice(found, 1)[0]);
        }
      });
    }

    return results.concat(remainingCriteria);
  }, [orderedByPreferences, pollCriteria]);

  return orderedCriteria;
};
