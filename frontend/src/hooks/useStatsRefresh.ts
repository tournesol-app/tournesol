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
  const statsState: PollStats | undefined = useAppSelector(selectStats);
  const dispatch = useAppDispatch();
  const { t } = useTranslation();
  const { showWarningAlert } = useNotifications();

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
