import { useSelector } from 'react-redux';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { getInitialRecoLanguages } from 'src/utils/recommendationsLanguages';
import { PollUserSettingsKeys } from 'src/utils/types';

export const usePreferredLanguages = ({ pollName }: { pollName: string }) => {
  const userSettings = useSelector(selectSettings).settings;
  let preferredLanguages =
    userSettings?.[pollName as PollUserSettingsKeys]?.feed_foryou__languages;

  preferredLanguages ??= getInitialRecoLanguages().split(',');

  return preferredLanguages;
};
