import React from 'react';
import { useTranslation } from 'react-i18next';

import GenericEventsPage from 'src/pages/events/GenericEventsPage';
import { EventTypeEnum } from 'src/services/openapi';

const TournesolLivePage = () => {
  const { t } = useTranslation();
  return (
    <GenericEventsPage
      title={t('tournesolLivePage.title')}
      selectedMenuItem="live"
      eventType={EventTypeEnum.LIVE}
    />
  );
};

export default TournesolLivePage;
