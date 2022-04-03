import React, { useState, useEffect } from 'react';

import { Typography, Link, Box } from '@mui/material';
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
  console.log(candidates);
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', p: 3 }}>
      <Typography variant="h3">Aide pour effectuer les comparaisons</Typography>
      <Typography paragraph>
        Si vous ne connaissez pas suffisemment bien les candidats et leur
        programmes, nous (l&apos;Association Tournesol) vous proposons les
        differentes sources d&apos;information ci-dessous que nous avons
        trouvées utiles.
      </Typography>

      <Typography variant="h4">
        Les site web officiels des candidats:
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
      <Typography variant="h4">Des comparateurs de programmes:</Typography>
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
      <Typography variant="h4">Les articles de Wikipedia:</Typography>
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
  );
};

export default ComparisonHelperPresidentielle2022;
