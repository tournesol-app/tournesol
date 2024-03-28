import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Typography } from '@mui/material';

import {
  ContentHeader,
  ContentBoxLegalDocument,
  LegalPaper,
  ExternalLink,
} from 'src/components';

import AcceptableUse from './sections/AcceptableUse';
import AccountTerms from './sections/AccountTerms';
import CancellationAndTermination from './sections/CancellationAndTermination';
import ChangesToTheseTerms from './sections/ChangesToTheseTerms';
import CommunicationsWithAssociation from './sections/CommunicationsWithAssociation';
import Definitions from './sections/Definitions';
import Moderation from './sections/Moderation';

const TermsOfServicePage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('terms.termsOfService')}`}
      />
      <ContentBoxLegalDocument mainTitle={t('terms.termsOfService')}>
        {[
          <Definitions key="section_a" />,
          <AccountTerms key="section_b" />,
          <AcceptableUse key="section_c" />,
          <Moderation key="section_d" />,
          <CancellationAndTermination key="section_e" />,
          <CommunicationsWithAssociation key="section_f" />,
          <ChangesToTheseTerms key="section_g" />,
        ].map((section) => (
          <LegalPaper key={`paper_${section.key}`}>{section}</LegalPaper>
        ))}

        <LegalPaper>
          <Typography paragraph>
            {t('terms.copying.thisDocumentIsInspiredByTheGitHubTos')}
          </Typography>
          <Typography paragraph mb={0}>
            <Trans
              t={t}
              i18nKey="terms.copying.thePresentTextsAreDedicatedToThePublicDomain"
            >
              The present texts are dedicated to the Public Domain, as stated by
              the license{' '}
              <ExternalLink href="https://creativecommons.org/publicdomain/zero/1.0/">
                Creative Commons Zero v1.0 Universal (CC0 1.0)
              </ExternalLink>
              .
            </Trans>
          </Typography>
        </LegalPaper>
      </ContentBoxLegalDocument>
    </>
  );
};

export default TermsOfServicePage;
