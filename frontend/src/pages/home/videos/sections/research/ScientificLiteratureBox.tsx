import React, { useState } from 'react';
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
  Tabs,
  Tab,
} from '@mui/material';
import {
  Campaign,
  HowToVote,
  MedicalInformation,
  MenuBook,
  VerifiedUser,
  School,
} from '@mui/icons-material';

function a11yProps(index: number) {
  return {
    id: `scientific-literature-tab-${index}`,
    'aria-controls': `scientific-literature-tabpanel-${index}`,
  };
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index } = props;

  return (
    <Box
      id={`scientific-literature-tabpanel-${index}`}
      role="tabpanel"
      hidden={value !== index}
      aria-labelledby={`scientific-literature-tab-${index}`}
    >
      {value === index && <Box>{children}</Box>}
    </Box>
  );
}

const ScientificLiteratureBox = () => {
  const { t } = useTranslation();

  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, tabIdx: number) => {
    setSelectedTab(tabIdx);
  };

  const chosenArticles = [
    {
      name: 'Tournesol: Permissionless Collaborative Algorithmic Governance with Security Guarantees.',
      authors:
        'Romain Beylerian, Bérangère Colbois, Louis Faucon, Lê Nguyên Hoang, Aidan Jungo, ' +
        "Alain Le Noac'h, Adrien Matissart (2022). ArXiV.",
      url: 'https://arxiv.org/abs/2211.01179',
      icon: VerifiedUser,
    },
    {
      name: 'Tournesol: A quest for a large, secure and trustworthy database of reliable human judgments.',
      authors:
        'Lê-Nguyên Hoang, Louis Faucon, Aidan Jungo, Sergei Volodin, Dalia Papuc, Orfeas Liossatos, ' +
        'Ben Crulis, Mariame Tighanimine, Isabela Constantin, Anastasiia Kucherenko, Alexandre Maurer, ' +
        'Felix Grimberg, Vlad Nitu, Chris Vossen, Sébastien Rouault, El-Mahdi El-Mhamdi (2021). ArXiV.',
      url: 'https://arxiv.org/abs/2107.07334',
      icon: MenuBook,
    },
    {
      name: 'Robust Sparse Voting',
      authors:
        'Youssef Allouah, Rachid Guerraoui, Lê-Nguyên Hoang, Oscar Villemaud (2022). ArXiV.',
      url: 'https://arxiv.org/abs/2202.08656',
      icon: HowToVote,
    },
    {
      name: 'Recommendation Algorithms, a Neglected Opportunity for Public Health.',
      authors:
        'Lê Nguyên Hoang, Louis Faucon & El-Mahdi El-Mhamdi (2021). Revue Médecine et Philosophie.',
      url: 'https://philpapers.org/rec/HOARAA',
      icon: MedicalInformation,
    },
    {
      name: 'Science Communication Desperately Needs More Aligned Recommendation Algorithms.',
      authors: 'Lê Nguyên Hoang (2020). Frontiers Communications.',
      url: 'https://www.frontiersin.org/articles/10.3389/fcomm.2020.598454/full',
      icon: Campaign,
    },
  ];

  const studentWorks = [
    {
      name: 'Active learning for video recommendation system.',
      authors: "Marc Gay-Balmaz, EPFL Master's Thesis (2022).",
      url: 'https://www.dropbox.com/sh/kztfgpz0epfr460/AACO-37hc-KdZmgfxvsxHmjLa/Active%20Learning%20%28Marc%20Gay-Balmaz%29.pdf?dl=1',
      icon: School,
    },
    {
      name:
        'Byzantine-resilient account validation through vouching : research and application to' +
        ' Tournesol project.',
      authors: "Bérangère Colbois. EPFL Master's semester project (2022).",
      url: 'https://www.dropbox.com/sh/kztfgpz0epfr460/AAAXHAWRGKh3MWXhfSDUkVkXa/Vouching%20%28B%C3%A9rang%C3%A8re%20Colbois%29.pdf?dl=1',
      icon: School,
    },
    {
      name: 'Bayesian Byzantine Resistance.',
      authors: "Marc Vandelle. EPFL Master's semester project (2022).",
      url: 'https://www.dropbox.com/sh/kztfgpz0epfr460/AAA6m1mb4OfmiOZ3wUS8s4dLa/Bayesian%20Byzantine%20voting%20rights%20%28Mac%20Vandelle%29.pdf?dl=1',
      icon: School,
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
          {t('scientificLiteratureBox.ourPublications')}
        </Typography>
      </Box>
      <Box>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            aria-label="Publication types"
            textColor="secondary"
            indicatorColor="secondary"
          >
            <Tab
              label={t('scientificLiteratureBox.papers')}
              {...a11yProps(0)}
            />
            <Tab
              label={t('scientificLiteratureBox.studenWorks')}
              {...a11yProps(1)}
            />
          </Tabs>
        </Box>
        <TabPanel value={selectedTab} index={0}>
          <List>
            {chosenArticles.map((article, idx) => (
              <React.Fragment key={article.name.replace(' ', '_')}>
                <ListItem disablePadding>
                  <ListItemButton
                    href={article.url}
                    target="_blank"
                    rel="noopener"
                  >
                    <ListItemAvatar>
                      <Avatar>
                        <article.icon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={article.name}
                      secondary={article.authors}
                    />
                  </ListItemButton>
                </ListItem>
                {idx !== chosenArticles.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </TabPanel>
        <TabPanel value={selectedTab} index={1}>
          <List>
            {studentWorks.map((article, idx) => (
              <React.Fragment key={article.name.replace(' ', '_')}>
                <ListItem disablePadding>
                  <ListItemButton href={article.url}>
                    <ListItemAvatar>
                      <Avatar>
                        <article.icon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={article.name}
                      secondary={article.authors}
                    />
                  </ListItemButton>
                </ListItem>
                {idx !== studentWorks.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </TabPanel>
      </Box>
    </Paper>
  );
};

export default ScientificLiteratureBox;
