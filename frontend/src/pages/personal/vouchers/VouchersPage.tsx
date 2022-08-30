import React from 'react';
import { useTranslation } from 'react-i18next';

import { ContentBox, ContentHeader } from 'src/components';

const PersonalVouchersPage = () => {
  const { t } = useTranslation();

  return (
    <>
      <ContentHeader title={t('personalMenu.vouchers')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        {' '}
      </ContentBox>
    </>
  );
};

export default PersonalVouchersPage;
