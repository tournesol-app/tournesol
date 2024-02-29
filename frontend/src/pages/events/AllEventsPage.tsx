import React from 'react';
import { useTranslation } from 'react-i18next';

import GenericEventsPage from './GenericEventsPage';

const AllEventsPage = () => {
  const { t } = useTranslation();
  return (
    <GenericEventsPage title={t('eventsPage.title')} selectedMenuItem="all" />
  );
};

export default AllEventsPage;
