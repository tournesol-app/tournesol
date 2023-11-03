import { useSelector } from 'react-redux';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { PollUserSettingsKeys } from 'src/utils/types';
import { recommendationsLanguagesFromNavigator } from 'src/utils/recommendationsLanguages';

export const usePreferredLanguages = ({ pollName }: { pollName: string }) => {
  const userSettings = useSelector(selectSettings).settings;
  let preferredLanguages =
    userSettings?.[pollName as PollUserSettingsKeys]
      ?.recommendations__default_languages;

  preferredLanguages ??= recommendationsLanguagesFromNavigator().split(',');

  return preferredLanguages;
};
