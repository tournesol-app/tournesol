import React from 'react';

import { useTranslation } from 'react-i18next';

import { ContentBox, ContentHeader } from 'src/components';
import UserActivityStats from './UserActivityStats';

const PersonalStatsPage = () => {
  const { t } = useTranslation();

  return (
    <>
      <ContentHeader title={t('personalMenu.myActivityStats')} />
      <ContentBox maxWidth="xl">
        <UserActivityStats />
      </ContentBox>
    </>
  );
};

export default PersonalStatsPage;
