import React, { useState, useEffect } from 'react';

import { Typography, Link, Box, Grid } from '@mui/material';
import { getAllCandidates } from 'src/utils/polls/presidentielle2022';
import { Entity } from 'src/services/openapi';

const ComparisonHelperPresidentielle2022 = () => {
  const [candidates, setCandidates] = useState<Entity[]>([]);

  useEffect(() => {
    getAllCandidates().then((candidates) => {
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
          Si vous ne connaissez pas suffisemment bien les candidat.es et leurs
          programmes, nous (l&apos;Association Tournesol) vous proposons
          ci-dessous differentes sources d&apos;information que nous avons
          trouvées utiles.
        </Typography>
        <Grid container justifyContent="space-between">
          <Grid item>
            <Typography variant="h4" color="secondary">
              Sites web officiels des candidat.es
            </Typography>
            <ul>
              {' '}
              {candidates.map(
                ({ metadata }) =>
                  metadata && (
                    <li>
                      <Link
                        color="text.secondary"
                        href={metadata.website_url}
                        rel="noopener"
                        target="_blank"
                      >
                        {metadata.name}
                      </Link>
                    </li>
                  )
              )}
            </ul>
          </Grid>
          <Grid item>
            <Typography variant="h6">📰 Comparateurs de programmes</Typography>
            <ul>
              <li>
                <Link
                  color="text.secondary"
                  href="https://www.lemonde.fr/les-decodeurs/article/2022/02/16/election-presidentielle-2022-comparez-les-programmes-des-principaux-candidats_6113964_4355770.html"
                  rel="noopener"
                  target="_blank"
                >
                  Du journal Le Monde
                </Link>
              </li>
              <li>
                <Link
                  color="text.secondary"
                  href="https://www.humanite.fr/comparateur-des-programmes-presidentielle-2022"
                  rel="noopener"
                  target="_blank"
                >
                  Du journal l&apos;Humanité
                </Link>
              </li>
              <li>
                <Link
                  color="text.secondary"
                  href="https://comparateur-programmes.lefigaro.fr/"
                  rel="noopener"
                  target="_blank"
                >
                  Du journal Le Figaro
                </Link>
              </li>
            </ul>
            <Typography variant="h6">🌳 Analyses des mesures climat</Typography>
            <ul>
              <li>
                <Link
                  color="text.secondary"
                  href="https://reseauactionclimat.org/presidentielle-candidats-climat/"
                  rel="noopener"
                  target="_blank"
                >
                  par le Réseau Action Climat France
                </Link>
              </li>
              <li>
                <Link
                  color="text.secondary"
                  href="https://presidentielle2022.theshifters.org/decryptage/"
                  rel="noopener"
                  target="_blank"
                >
                  par The Shifters
                </Link>
              </li>
            </ul>
          </Grid>
        </Grid>
        <Typography variant="h4" color="secondary">
          Pages Wikipedia des candidat.es
        </Typography>
        <ul>
          {' '}
          {candidates.map(
            ({ metadata }) =>
              metadata && (
                <li>
                  <Link
                    color="text.secondary"
                    href={`https://fr.wikipedia.org/wiki/${encodeURIComponent(
                      metadata.frwiki_title
                    )}`}
                    rel="noopener"
                    target="_blank"
                  >
                    {metadata.name}
                  </Link>
                </li>
              )
          )}
        </ul>
      </Box>
    </>
  );
};

export default ComparisonHelperPresidentielle2022;
