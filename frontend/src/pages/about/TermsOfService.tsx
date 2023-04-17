import React from 'react';

import { ContentBox, ContentHeader } from 'src/components';
import { useTranslation } from 'react-i18next';

const TermsOfServicePage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('termsOfService.termsOfService')}`}
      />
    </>
  );
};

export default TermsOfServicePage;
