import React, { useState, useEffect } from 'react';

import { Typography, Box, Grid } from '@mui/material';

import { ExternalLink } from 'src/components';
import { getAllCandidates } from 'src/utils/polls/presidentielle2022';
import { EntityObject } from 'src/utils/types';

const ComparisonHelperPresidentielle2022 = () => {
  const [candidates, setCandidates] = useState<EntityObject[]>([]);

  useEffect(() => {
    getAllCandidates().then((results) => {
      const candidates = results.map((res) => res.entity);
      const sortedCandidates = [...candidates].sort((a, b) => {
        // Sort by last name
        const aName: string = a?.metadata?.name.split(' ').slice(1).join(' ');
        const bName: string = b?.metadata?.name.split(' ').slice(1).join(' ');
        return aName.localeCompare(bName);
      });
      setCandidates(sortedCandidates);
    });
  }, []);
  return (
    <>
      <Box sx={{ backgroundColor: '#eee', p: 3 }}>
        <Typography variant="h3">
          Aide pour effectuer les comparaisons
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', p: 3 }}>
        <Typography paragraph>
          Si vous ne connaissez pas suffisamment bien les candidat·es et leurs
          programmes, nous (l&apos;Association Tournesol) vous proposons
          ci-dessous differentes sources d&apos;information que nous avons
          trouvées utiles.
        </Typography>
        <Grid container justifyContent="space-between">
          <Grid item>
            <Typography variant="h4" color="secondary">
              Sites web officiels des candidat·es
            </Typography>
            <ul>
              {' '}
              {candidates.map(
                ({ metadata }) =>
                  metadata && (
                    <li key={metadata.name}>
                      <ExternalLink
                        href={metadata.website_url}
                        target="_blank"
                        sx={{ color: 'text.secondary' }}
                      >
                        {metadata.name}
                      </ExternalLink>
                    </li>
                  )
              )}
            </ul>
          </Grid>
          <Grid item>
            <Typography variant="h6">📰 Comparateurs de programmes</Typography>
            <ul>
              <li>
                <ExternalLink
                  href="https://www.lemonde.fr/les-decodeurs/article/2022/02/16/election-presidentielle-2022-comparez-les-programmes-des-principaux-candidats_6113964_4355770.html"
                  target="_blank"
                  sx={{ color: 'text.secondary' }}
                >
                  Du journal Le Monde
                </ExternalLink>
              </li>
              <li>
                <ExternalLink
                  href="https://www.humanite.fr/comparateur-des-programmes-presidentielle-2022"
                  target="_blank"
                  sx={{ color: 'text.secondary' }}
                >
                  Du journal l&apos;Humanité
                </ExternalLink>
              </li>
              <li>
                <ExternalLink
                  href="https://comparateur-programmes.lefigaro.fr/"
                  target="_blank"
                  sx={{ color: 'text.secondary' }}
                >
                  Du journal Le Figaro
                </ExternalLink>
              </li>
            </ul>
            <Typography variant="h6">🌳 Analyses des mesures climat</Typography>
            <ul>
              <li>
                <ExternalLink
                  href="https://reseauactionclimat.org/presidentielle-candidats-climat/"
                  target="_blank"
                  sx={{ color: 'text.secondary' }}
                >
                  par le Réseau Action Climat France
                </ExternalLink>
              </li>
              <li>
                <ExternalLink
                  href="https://presidentielle2022.theshifters.org/decryptage/"
                  target="_blank"
                  sx={{ color: 'text.secondary' }}
                >
                  par The Shifters
                </ExternalLink>
              </li>
            </ul>
          </Grid>
        </Grid>
        <Typography variant="h4" color="secondary">
          Pages Wikipedia des candidat·es
        </Typography>
        <ul>
          {' '}
          {candidates.map(
            ({ metadata }) =>
              metadata && (
                <li key={metadata.name}>
                  <ExternalLink
                    href={`https://fr.wikipedia.org/wiki/${encodeURIComponent(
                      metadata.frwiki_title
                    )}`}
                    target="_blank"
                    sx={{ color: 'text.secondary' }}
                  >
                    {metadata.name}
                  </ExternalLink>
                </li>
              )
          )}
        </ul>
      </Box>
    </>
  );
};

export default ComparisonHelperPresidentielle2022;
