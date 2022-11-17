import React, { useEffect, useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import {
  Typography,
  Box,
  Divider,
  List,
  ListItem,
  CircularProgress,
} from '@mui/material';

import { ContentHeader, ContentBox } from 'src/components';
import { EmailDomain, DomainsService } from 'src/services/openapi';

const DOMAINS_PAGE_SIZE = 1000;

const TrustedDomains = () => {
  const { t } = useTranslation();
  const [domains, setDomains] = useState<EmailDomain[] | null>(null);

  useEffect(() => {
    const loadDomains = async () => {
      const result = [];
      let offset = 0;
      let response;
      do {
        response = await DomainsService.domainsList({
          limit: DOMAINS_PAGE_SIZE,
          offset,
        });
        const responseDomains = response.results || [];
        offset += responseDomains.length;
        result.push(...responseDomains);
      } while (response.next);
      setDomains(result);
    };
    loadDomains();
  }, []);

  return (
    <>
      <ContentHeader
        title={`${t('menu.about')} > ${t('about.trustedEmailDomains')}`}
      />
      <ContentBox maxWidth="md">
        <Box marginBottom={6}>
          <Typography component="div">
            <p>{t('about.trustedDomainsToProtectTournesol')}</p>
            <p>
              <Trans t={t} i18nKey="about.trustedDomainsGainMoreVotingRights">
                You can gain significantly more trust by validating{' '}
                <strong>an email address from a trusted domain</strong>, or by
                having other users vouch for you.
              </Trans>
            </p>
            <p>{t('about.trustedDomainsValuable')}</p>
          </Typography>
        </Box>
        <Box>
          <Typography variant="h4" color="secondary">
            {t('about.trustedDomainsCurrentList')}
          </Typography>
          <Divider />
          <List>
            {domains !== null ? (
              domains.map((domain) => (
                <ListItem
                  key={domain.domain}
                  dense
                  disableGutters
                  sx={{ fontSize: '14px' }}
                >
                  {domain.domain}
                </ListItem>
              ))
            ) : (
              <CircularProgress />
            )}
          </List>
        </Box>
      </ContentBox>
    </>
  );
};

export default TrustedDomains;
