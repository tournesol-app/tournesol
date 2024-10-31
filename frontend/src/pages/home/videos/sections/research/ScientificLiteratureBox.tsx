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
  QueryStats,
  FormatQuote,
  Newspaper,
  Headphones,
  SwapHoriz,
  OndemandVideo,
} from '@mui/icons-material';
import TitledPaper from 'src/components/TitledPaper';

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
        'Lê Nguyên Hoang, Romain Beylerian, Bérangère Colbois, Julien Fageot, Louis Faucon, ' +
        "Aidan Jungo, Alain Le Noac'h, Adrien Matissart, Oscar Villemaud (2022). ArXiV.",
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
      name: 'Should YouTube make recommendations for the climate?',
      authors:
        'Martin Gibert, Lê-Nguyên Hoang, Maxime Lambrecht (2024). Ethics and Information Technology.',
      url: 'https://link.springer.com/article/10.1007/s10676-024-09784-4',
      icon: MenuBook,
    },
    {
      name: ' Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons',
      authors:
        'Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang, Oscar Villemaud (2024). AAAI.',
      url: 'https://ojs.aaai.org/index.php/AAAI/article/view/30020',
      icon: SwapHoriz,
    },
    {
      name: 'Robust Sparse Voting',
      authors:
        'Youssef Allouah, Rachid Guerraoui, Lê-Nguyên Hoang, Oscar Villemaud (2024). AISTATS.',
      url: 'https://arxiv.org/abs/2202.08656',
      icon: HowToVote,
    },
    {
      name: 'On the Strategyproofness of the Geometric Median',
      authors:
        'El-Mahdi El-Mhamdi, Sadegh Farhadkhani, Rachid Guerraoui, Lê-Nguyên Hoang (2023). AISTATS 2023.',
      url: 'https://proceedings.mlr.press/v206/el-mhamdi23a.html',
      icon: QueryStats,
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
      url: 'https://drive.google.com/uc?id=1Sg_Wk-zCryF4fB_KMIEywg9lOMxWI9_e&export=download',
      icon: School,
    },
    {
      name:
        'Byzantine-resilient account validation through vouching : research and application to' +
        ' Tournesol project.',
      authors: "Bérangère Colbois. EPFL Master's semester project (2022).",
      url: 'https://drive.google.com/uc?id=1aIld_UnkFNmQoFxbbFiN37DWKXdIkFqJ&export=download',
      icon: School,
    },
    {
      name: 'Bayesian Byzantine Resistance.',
      authors: "Marc Vandelle. EPFL Master's semester project (2022).",
      url: 'https://drive.google.com/uc?id=1Q4TBKW8vKWf6CCL77qCSvo92MOShBEDN&export=download',
      icon: School,
    },
  ];

  const theyCiteUs = [
    {
      name: 'Volition Learning: What Would You Prefer to Prefer?',
      authors:
        'Mohamed Lechiakh, Alexandre Maurer (2023). Artificial Intelligence in Human-Computer Interaction.',
      url: 'https://link.springer.com/chapter/10.1007/978-3-031-35891-3_35',
      icon: FormatQuote,
    },
    {
      name: "Algocratie : Vivre libre à l'heure des algorithmes",
      authors: 'Arthur Grimonpont (2022). Actes Sud.',
      url: 'https://www.actes-sud.fr/catalogue/sciences-humaines-et-sociales-sciences/algocratie',
      icon: FormatQuote,
    },
    {
      name: 'The human cost of ethical artificial intelligence',
      authors:
        'James Ruffle, Chris Foulon, Parashkev Nachev (2023). Brain Structure and Function.',
      url: 'https://link.springer.com/article/10.1007/s00429-023-02662-7',
      icon: FormatQuote,
    },
    {
      name: 'Model reports, a supervision tool for Machine Learning engineers and users',
      authors:
        'Amine Saboni, Mohamed Ouamane, Ouafae Bennis, Frédéric Krat (2021). European Conference on Electrical Engineering & COmputer Science.',
      url: 'https://hal.science/hal-03410903/',
      icon: FormatQuote,
    },
    {
      name: 'Identify ambiguous tasks combining crowdsourced labels by weighting Areas Under the Margin.',
      authors:
        'Tanguy Lefort, Benjamin Charlier, Alexis Joly, Joseph Salmon (2022). ArXiV.',
      url: 'https://arxiv.org/abs/2209.15380',
      icon: FormatQuote,
    },
  ];

  const inTheMedia = [
    {
      name: "Tournesol, une application pour repliquer face à la crise de l'information",
      authors: 'Jean-Philippe Peyrache (2024). La Brèche n°9',
      url: 'https://journal-labreche.fr/lisez-la-breche-n-9-en-numerique/',
      icon: Newspaper,
    },
    {
      name: "L'IA va-t-elle nous aider ou nous remplacer ? «Libé» fait débattre deux experts, Fatie Toko et Lê Nguyên Hoang",
      authors: 'Gurvan Kristanadjaja (2024). Libération',
      url: 'https://www.liberation.fr/idees-et-debats/lia-va-t-elle-nous-aider-ou-nous-remplacer-libe-fait-debattre-deux-experts-fatie-toko-et-le-nguyen-hoang-20240503_SK4TJBSNW5C3FA4RV2SW3ZES2M/',
      icon: Newspaper,
    },
    {
      name: 'IA : les algorithmes dirigent-ils le monde ? Le point de vue de Lê Nguyen Hoang',
      authors: 'Thimothée Dhellemmes (2024). Le Figaro',
      url: 'https://video.lefigaro.fr/figaro/video/intelligence-artificielle-les-algorithmes-dirigent-ils-le-monde/',
      icon: OndemandVideo,
    },
    {
      name: 'Les grands modèles de langage : quels risques ? Échange avec Lê Nguyên Hoang.',
      authors: 'Paroles de (2023). Conseil national du numérique.',
      url: 'https://cnnumerique.fr/paroles-de/les-grands-modeles-de-langage-quels-risques-echange-avec-le-nguyen-hoang',
      icon: Newspaper,
    },
    {
      name: 'Researchers turn to crowdsourcing for better YouTube recommendations',
      authors: 'Kyle Wiggers (2022). VentureBeat.',
      url: 'https://venturebeat.com/ai/researchers-turn-to-crowdsourcing-for-better-youtube-recommendations/',
      icon: Newspaper,
    },
    {
      name: 'AIs are out of (democratic) control',
      authors: 'Lê Nguyên Hoang (2023). SwissInfo.',
      url: 'https://www.swissinfo.ch/eng/ais-are-out-of--democratic--control/48427358',
      icon: Newspaper,
    },
    {
      name: 'Podcast - Comment dompter un algorithme ?',
      authors: 'Andreia Glanville, Huma Khamis (2023). RTS Micro-sciences.',
      url: 'https://www.rts.ch/info/sciences-tech/14000339-podcast-comment-dompter-un-algorithme.html',
      icon: Headphones,
    },
    {
      name: "L'intelligence artificielle : outil de domination ou d'émancipation ?",
      authors: 'Julien Hernandez (2023). Polytechnique Insights.',
      url: 'https://www.polytechnique-insights.com/tribunes/digital/lintelligence-artificielle-outil-de-domination-ou-demancipation/',
      icon: Newspaper,
    },
    {
      name: "L'AI contre la désinformation",
      authors: "Adrien Zerbini (2022). RTS Ça n'a pas de science !",
      url: 'https://www.rts.ch/la-1ere/programmes/cqfd/11969483-ca-n-a-pas-de-science-.html',
      icon: Headphones,
    },
    {
      name: "Les Lumières à l'ère du numérique.",
      authors: 'Rapport de la Commission (2022).',
      url: 'https://www.elysee.fr/emmanuel-macron/2022/01/11/remise-du-rapport-de-la-commission-bronner',
      icon: Newspaper,
    },
    {
      name: 'AI thinkers grapple with modern war',
      authors: 'Kate Kaye (2022). Protocol Enterprise. ',
      url: 'https://www.protocol.com/newsletters/protocol-enterprise/ai-russia-ukraine-zendesk-momentive',
      icon: Newspaper,
    },
    {
      name: "« L'industrie de l'information est probablement la plus dangereuse pour la société »",
      authors: 'Grégoire Barbey (2022). Heidi.News.',
      url: 'https://www.heidi.news/cyber/l-industrie-de-l-information-est-probablement-la-plus-dangereuse-pour-la-societe',
      icon: Newspaper,
    },
    {
      name: "Tournesol : l'algorithme d'utilité publique qui a besoin de vous !",
      authors: 'Julien Hernandez (2021). Futura Sciences.',
      url: 'https://www.futura-sciences.com/tech/actualites/intelligence-artificielle-tournesol-algorithme-utilite-publique-besoin-vous-87301/',
      icon: Newspaper,
    },
  ];

  return (
    <TitledPaper
      title={t('scientificLiteratureBox.publications')}
      titleId="publications"
      contentBoxPadding={0}
    >
      <>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            aria-label="Publication types"
            textColor="secondary"
            indicatorColor="secondary"
            variant="scrollable"
            scrollButtons="auto"
            allowScrollButtonsMobile
          >
            <Tab
              label={t('scientificLiteratureBox.ourPapers')}
              {...a11yProps(0)}
            />
            <Tab
              label={t('scientificLiteratureBox.studenWorks')}
              {...a11yProps(1)}
            />
            <Tab
              label={t('scientificLiteratureBox.theyCiteUs')}
              {...a11yProps(2)}
            />
            <Tab
              label={t('scientificLiteratureBox.inTheMedia')}
              {...a11yProps(3)}
            />
          </Tabs>
        </Box>
        <TabPanel value={selectedTab} index={0}>
          <List>
            {chosenArticles.map((article, idx) => (
              <React.Fragment key={article.name.replace(' ', '_')}>
                <ListItem disablePadding>
                  <ListItemButton href={article.url} rel="noreferrer">
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
                  <ListItemButton href={article.url} rel="noreferrer">
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
        <TabPanel value={selectedTab} index={2}>
          <List>
            {theyCiteUs.map((article, idx) => (
              <React.Fragment key={article.name.replace(' ', '_')}>
                <ListItem disablePadding>
                  <ListItemButton href={article.url} rel="noreferrer">
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
                {idx !== theyCiteUs.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </TabPanel>
        <TabPanel value={selectedTab} index={3}>
          <List>
            {inTheMedia.map((article, idx) => (
              <React.Fragment key={article.name.replace(' ', '_')}>
                <ListItem disablePadding>
                  <ListItemButton href={article.url} rel="noreferrer">
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
                {idx !== inTheMedia.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </TabPanel>
      </>
    </TitledPaper>
  );
};

export default ScientificLiteratureBox;
