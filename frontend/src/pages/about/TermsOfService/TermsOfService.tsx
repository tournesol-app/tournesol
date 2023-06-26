import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

import { Link, Typography } from '@mui/material';

import { ContentHeader } from 'src/components';

import AcceptableUse from './sections/AcceptableUse';
import AccountTerms from './sections/AccountTerms';
import CancellationAndTermination from './sections/CancellationAndTermination';
import ChangesToTheseTerms from './sections/ChangesToTheseTerms';
import CommunicationsWithAssociation from './sections/CommunicationsWithAssociation';
import Definitions from './sections/Definitions';
import Moderation from './sections/Moderation';
import { LegalDocument, LegalPaper } from 'src/components/LegalDocument';

const TermsOfServicePage = () => {
  const { t } = useTranslation();
  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('terms.termsOfService')}`}
      />
      <LegalDocument mainTitle={t('terms.termsOfService')}>
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
              <Link
                href="https://creativecommons.org/publicdomain/zero/1.0/"
                target="_blank"
                rel="noopener"
                sx={{
                  color: 'revert',
                  textDecoration: 'revert',
                }}
              >
                Creative Commons Zero v1.0 Universal (CC0 1.0)
              </Link>
              .
            </Trans>
          </Typography>
        </LegalPaper>
      </LegalDocument>
    </>
  );
};

export default TermsOfServicePage;
