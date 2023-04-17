import { useTranslation } from 'react-i18next';
import { useAppDispatch, useAppSelector } from 'src/app/hooks';
import {
  fetchStatsData,
  selectStats,
} from 'src/features/comparisons/statsSlice';
import { getPollStats } from 'src/utils/api/stats';
import { PollStats } from 'src/utils/types';
import { useNotifications } from './useNotifications';

export const useStatsRefresh = () => {
  const statsState: PollStats = useAppSelector(selectStats);
  const dispatch = useAppDispatch();
  const { t } = useTranslation();
  const { showWarningAlert } = useNotifications();
  //this function fetches from /stats/ api, AND pushes/refreshes/dispatches the data into redux
  async function getPollStatsAsync(pollName: string) {
    try {
      const pollStats = await getPollStats(pollName);
      if (pollStats) {
        dispatch(fetchStatsData(pollStats));
      }
    } catch (reason) {
      showWarningAlert(t('home.theStatsCouldNotBeDisplayed'));
    }
  }

  return { statsState, getPollStatsAsync };
};
