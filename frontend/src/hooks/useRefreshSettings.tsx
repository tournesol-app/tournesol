import { useEffect } from 'react';

import { useAppDispatch } from 'src/app/hooks';
import { fetchUserSettings } from 'src/features/settings/userSettingsSlice';
import { useLoginState } from 'src/hooks';

export const useRefreshSettings = () => {
  const dispatch = useAppDispatch();
  const { isLoggedIn } = useLoginState();

  useEffect(() => {
    if (isLoggedIn) {
      dispatch(fetchUserSettings());
    }
  }, [dispatch, isLoggedIn]);
};
