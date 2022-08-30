import React from 'react';
import { useTranslation } from 'react-i18next';

import { ContentBox, ContentHeader } from 'src/components';

import CreateVoucherForm from './CreateVoucherForm';
import { PersonalVouchersProvider } from './context';

const PersonalVouchersPage = () => {
  const { t } = useTranslation();

  return (
    <PersonalVouchersProvider>
      <ContentHeader title={t('personalMenu.vouchers')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <CreateVoucherForm />
      </ContentBox>
    </PersonalVouchersProvider>
  );
};

export default PersonalVouchersPage;
