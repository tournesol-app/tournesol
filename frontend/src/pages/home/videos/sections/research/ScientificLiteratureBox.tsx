import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Divider,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Paper,
  Typography,
  ListItemButton,
} from '@mui/material';
import {
  Campaign,
  MedicalInformation,
  MenuBook,
  VerifiedUser,
  HowToVote,
} from '@mui/icons-material';

const ScientificLiteratureBox = () => {
  const { t } = useTranslation();

  const papers = [
    {
      name: 'Tournesol: Permissionless Collaborative Algorithmic Governance with Security Guarantees.',
      submitted:
        'Romain Beylerian, Bérangère Colbois, Louis Faucon, Lê Nguyên Hoang, Aidan Jungo, ' +
        "Alain Le Noac'h, Adrien Matissart (2022). ArXiV.",
      url: 'https://arxiv.org/abs/2211.01179',
      icon: VerifiedUser,
    },
    {
      name: 'Tournesol: A quest for a large, secure and trustworthy database of reliable human judgments.',
      submitted:
        'Lê-Nguyên Hoang, Louis Faucon, Aidan Jungo, Sergei Volodin, Dalia Papuc, Orfeas Liossatos, ' +
        'Ben Crulis, Mariame Tighanimine, Isabela Constantin, Anastasiia Kucherenko, Alexandre Maurer, ' +
        'Felix Grimberg, Vlad Nitu, Chris Vossen, Sébastien Rouault, El-Mahdi El-Mhamdi (2021). ArXiV.',
      url: 'https://arxiv.org/abs/2107.07334',
      icon: MenuBook,
    },
    {
      name: 'Robust Sparse Voting',
      submitted:
        'Youssef Allouah, Rachid Guerraoui, Lê-Nguyên Hoang, Oscar Villemaud (2022). ArXiV.',
      url: 'https://arxiv.org/abs/2202.08656',
      icon: HowToVote,
    },
    {
      name: 'Recommendation Algorithms, a Neglected Opportunity for Public Health.',
      submitted:
        'Lê Nguyên Hoang, Louis Faucon & El-Mahdi El-Mhamdi (2021). Revue Médecine et Philosophie.',
      url: 'https://philpapers.org/rec/HOARAA',
      icon: MedicalInformation,
    },
    {
      name: 'Science Communication Desperately Needs More Aligned Recommendation Algorithms.',
      submitted: 'Lê Nguyên Hoang (2020). Frontiers Communications.',
      url: 'https://www.frontiersin.org/articles/10.3389/fcomm.2020.598454/full',
      icon: Campaign,
    },
  ];

  return (
    <Paper>
      <Box
        p={2}
        color="#fff"
        bgcolor="#1282B2"
        sx={{ borderTopLeftRadius: 'inherit', borderTopRightRadius: 'inherit' }}
      >
        <Typography variant="h4">
          {t('scientificLiteratureBox.scientificLiterature')}
        </Typography>
      </Box>
      {/* Here px=1 is used instead of the regular p=2 as the list as already
          enough built-in padding */}
      <Box px={1}>
        <List>
          {papers.map((paper, idx) => (
            <React.Fragment key={paper.name.replace(' ', '_')}>
              <ListItem>
                <ListItemAvatar>
                  <Avatar>
                    <paper.icon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemButton
                  href={paper.url}
                  target="_blank"
                  rel="noopener"
                  disableGutters
                >
                  <ListItemText
                    primary={paper.name}
                    secondary={paper.submitted}
                  />
                </ListItemButton>
              </ListItem>
              {idx !== papers.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Box>
    </Paper>
  );
};

export default ScientificLiteratureBox;
