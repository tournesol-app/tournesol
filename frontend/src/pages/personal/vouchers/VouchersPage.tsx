import React from 'react';
import { useTranslation } from 'react-i18next';

import { ContentBox, ContentHeader } from 'src/components';

import { PersonalVouchersProvider } from './context';
import CreateVoucherForm from './CreateVoucherForm';
import GivenVouchers from './GivenVouchers';
import ReceivedVouchers from './ReceivedVouchers';

const PersonalVouchersPage = () => {
  const { t } = useTranslation();

  return (
    <PersonalVouchersProvider>
      <ContentHeader title={t('personalMenu.vouchers')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <CreateVoucherForm />
        <GivenVouchers />
        <ReceivedVouchers />
      </ContentBox>
    </PersonalVouchersProvider>
  );
};

export default PersonalVouchersPage;
