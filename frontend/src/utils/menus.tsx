/**
 * Configuration of the Tournesol menus and definition of their related types.
 */

import { TFunction } from 'react-i18next';
import { AccountCircle, Settings, SvgIconComponent } from '@mui/icons-material';

export type TournesolMenuItemType = {
  id: string;
  text: string;
  icon: SvgIconComponent;
  to: string;
};

export const settingsMenu = (t: TFunction): Array<TournesolMenuItemType> => {
  return [
    {
      id: 'settings-profile',
      text: t('profile'),
      icon: AccountCircle,
      to: '/settings/profile',
    },
    {
      id: 'settings-account',
      text: t('settings.account'),
      icon: Settings,
      to: '/settings/account',
    },
  ];
};
