import React, { useEffect, useState } from 'react';
import {
  Typography,
  Box,
  Divider,
  List,
  ListItem,
  CircularProgress,
} from '@material-ui/core';

import { ContentHeader, ContentBox } from 'src/components';
import { EmailDomain, DomainsService } from 'src/services/openapi';

const DOMAINS_PAGE_SIZE = 1000;

const TrustedDomains = () => {
  const [domains, setDomains] = useState<EmailDomain[] | null>(null);

  useEffect(() => {
    const loadDomains = async () => {
      const result = [];
      let offset = 0;
      let response;
      do {
        response = await DomainsService.domainsList(DOMAINS_PAGE_SIZE, offset);
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
      <ContentHeader title="About > Trusted email domains" />
      <ContentBox maxWidth="md">
        <Box marginBottom={6}>
          <Typography component="div">
            <p>
              In order to protect Tournesol from fake accounts, by default,
              Tournesol assigns a limited voting right to newly created
              accounts.
            </p>
            <p>
              You can gain significantly more voting rights by validating{' '}
              <strong>an email address from a trusted domain</strong>. We are
              currently working on designing additional means for contributors
              to gain voting rights.
            </p>
            <p>
              In any case, your contributions are valuable to us, as they will
              motivate further research in safe and ethical algorithms.
            </p>
          </Typography>
        </Box>
        <Box>
          <Typography variant="h4" color="secondary">
            Current list of trusted domains
          </Typography>
          <Divider />
          <List>
            {domains !== null ? (
              domains.map((domain) => (
                <ListItem key={domain.domain} dense disableGutters>
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
