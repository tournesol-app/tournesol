import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Paper, useTheme, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { useScrollToLocation } from 'src/hooks';

const ManifestoPage = () => {
  // Draft is available in french only: force french lang for all users in this section
  const { t } = useTranslation(undefined, { lng: 'fr' });
  const theme = useTheme();
  useScrollToLocation();

  return (
    <>
      <ContentHeader title={t('manifesto.header')} />
      <ContentBox
        maxWidth="md"
        sx={{
          '&': {
            h3: {
              mt: 6,
              mb: 2,
              textDecorationLine: 'underline',
              textDecorationColor: theme.palette.divider,
              textDecorationThickness: '2px',
            },
            strong: {
              textDecorationLine: 'underline',
              textDecorationColor: theme.palette.primary.main,
              textDecorationThickness: '4px',
              textDecorationSkipInk: 'none',
            },
            table: {
              fontSize: '90%',
              borderCollapse: 'separate',
              borderSpacing: '0 1em',
            },
            tr: {
              backgroundColor: '#f2f2ff',
            },
            td: {
              verticalAlign: 'top',
              padding: '12px',
            },
            'li span': {
              fontSize: '90%',
              color: theme.palette.info.dark,
            },
          },
        }}
      >
        <Paper sx={{ p: 4 }}>
          <Typography variant="h1">{t('manifesto.title')}</Typography>

          <p>{t('manifesto.intro')}</p>

          <Typography variant="h3" id="part1">
            {t('manifesto.part1.title')}
          </Typography>

          <p>
            <Trans i18nKey="manifesto.part1.democracyDepends" t={t}>
              Notre fonctionnement démocratique dépend d’échanges d’informations
              qui ont désormais souvent lieu sur des plateformes numériques, et
              sont par conséquent organisés par ces IA de recommandation. Or, de
              nombreuses études scientifiques montrent que ces IA de
              recommandation nuisent à l’intérêt général :{' '}
              <strong>dégradation sans précédent de la santé mentale</strong>{' '}
              chez les jeunes
              <sup id="ref1">
                <a href="#note1">[1]</a>
              </sup>
              , <strong>polarisation</strong> du discours public
              <sup id="ref2">
                <a href="#note2">[2]</a>
              </sup>
              , <strong>manipulation d’élections</strong>
              <sup id="ref3">
                <a href="#note3">[3]</a>
              </sup>
              , désinformation
              <sup id="ref4">
                <a href="#note4">[4]</a>
              </sup>
              , contribution à des <strong>génocides</strong>
              <sup id="ref5">
                <a href="#note5">[5]</a>
              </sup>
              .
            </Trans>
          </p>

          <p>
            <Trans i18nKey="manifesto.part1.toOrganizeInformationFlow" t={t}>
              Pour organiser la circulation des informations, les géants du
              numérique utilisent ces IA de recommandation, qui fonctionnent
              selon des critères opaques, servent uniquement leurs intérêts
              économiques ou idéologiques, ne sont soumises à quasi aucune
              régulation et donc aucun contrôle démocratique.
            </Trans>
          </p>

          <p>
            <Trans i18nKey="manifesto.part1.againstPublicInterest" t={t}>
              En somme, les IA de recommandation actuelles favorisent largement
              des intérêts privés au détriment de l’intérêt général.
            </Trans>
          </p>

          <Typography variant="h3" id="part2">
            {t('manifesto.part2.title')}
          </Typography>

          <p>
            <Trans i18nKey="manifesto.part2.forRegulation" t={t}>
              Nous défendons l’idée de réguler ces espaces numériques et leurs
              IA de recommandation, à l’instar d’autres industries à haut risque
              (aviation, pharmaceutique ou agro-alimentaire).
            </Trans>
          </p>

          <p>
            <Trans i18nKey="manifesto.part2.existingLawsNotEnforced" t={t}>
              Nous demandons que{' '}
              <strong>
                les lois existantes soient effectivement appliquées
              </strong>
              , et que le numérique cesse d’être un espace de non-droit.
              L’Europe s’est dotée de plusieurs lois visant à encadrer les
              plateformes numériques (AI Act, DSA, DMA, RGPD) ; elles sont
              largement inappliquées
              <sup id="ref6">
                <a href="#note6">[6]</a>
              </sup>
              .
            </Trans>
          </p>

          <div>
            <Trans i18nKey="manifesto.part2.existingLawsInsufficient" t={t}>
              Plus encore, nous pensons que{' '}
              <strong>ces lois sont insuffisantes</strong>. Nous proposons
              d’introduire dans le corpus législatif de nouveaux principes, tels
              que:
            </Trans>
            <ul>
              <li>
                <p>
                  {t('manifesto.part2.propositions.authorization.main')}
                  {' – '}
                  <span>
                    {t('manifesto.part2.propositions.authorization.detail')}
                  </span>
                </p>
              </li>
              <li>
                <p>
                  {t('manifesto.part2.propositions.nonRecommendability.main')}
                  {' – '}
                  <span>
                    {t(
                      'manifesto.part2.propositions.nonRecommendability.detail'
                    )}
                  </span>
                </p>
              </li>
              <li>
                <p>
                  {t('manifesto.part2.propositions.configurationRight.main')}
                  {' – '}
                  <span>
                    {t(
                      'manifesto.part2.propositions.configurationRight.detail'
                    )}
                  </span>
                </p>
              </li>
            </ul>
          </div>

          <Typography variant="h3" id="part3">
            {t('manifesto.part3.title')}
          </Typography>

          <div>
            <Trans i18nKey="manifesto.part3.buildDemocraticDigitalSpace" t={t}>
              Concrètement, nous pensons que pour que nos espaces numériques
              soient alignés avec nos standards démocratiques et participent au
              bon fonctionnement de nos sociétés, il faudrait que leur mécanisme
              soit à minima,
            </Trans>
            <ul>
              <li>
                <p>
                  {t('manifesto.part3.requirements.transparent.title')}
                  {' – '}
                  <span>
                    {t('manifesto.part3.requirements.transparent.detail')}
                  </span>
                </p>
              </li>
              <li>
                <p>
                  {t('manifesto.part3.requirements.robust.title')}
                  {' – '}
                  <span>{t('manifesto.part3.requirements.robust.detail')}</span>
                </p>
              </li>
              <li>
                <p>
                  {t('manifesto.part3.requirements.wellTought.title')}
                  {' – '}
                  <span>
                    {t('manifesto.part3.requirements.wellTought.detail')}
                  </span>
                </p>
              </li>
              <li>
                <p>
                  {t('manifesto.part3.requirements.commonInformation.title')}
                  {' – '}
                  <span>
                    {t('manifesto.part3.requirements.commonInformation.detail')}
                  </span>
                </p>
              </li>
            </ul>
          </div>

          <p>
            <Trans i18nKey="manifesto.conclusion.digitalPlatforms" t={t}>
              Le mode de fonctionnement des plateformes numériques, lui-même,
              doit faciliter l’expression de la parole citoyenne. En ce sens,
              les contenus recommandés massivement sur les réseaux sociaux
              devraient refléter les intérêts et les opinions de la parole
              citoyenne
            </Trans>
          </p>

          <p>
            <Trans i18nKey="manifesto.conclusion.itIsPossible" t={t}>
              Cela est tout à fait possible, à condition de développer des IA de
              recommandation fondées sur les jugements réfléchis des citoyens,
              et non sur les intérêts des géants du numérique.
            </Trans>
          </p>

          <p>
            <Trans i18nKey="manifesto.conclusion.tournesolProject" t={t}>
              Le projet Tournesol.app développe une IA de recommandation
              alternative de ce type, qui s&apos;appuient sur vos jugements et
              vos intérêts. Venez essayer la plateforme :{' '}
              <a href="https://tournesol.app">https://tournesol.app/</a> !
            </Trans>
          </p>

          <p>
            <Trans i18nKey="manifesto.conclusion.tournesolAssociation" t={t}>
              Au-delà, l’association Tournesol regroupe des citoyens, des
              chercheurs, des vidéastes, des développeurs bénévoles. Elle a pour
              but de défendre les trois principes proposés dans ce manifeste.
            </Trans>
          </p>

          <p>
            <Trans i18nKey="manifesto.conclusion.contactAndActions" t={t}>
              Rejoignez-vous sur{' '}
              <a href="https://discord.com/invite/TvsFB8RNBV">notre Discord</a>,
              et impliquez-vous sur cette thématique :{' '}
              <a href="https://tournesol.app/actions">
                https://tournesol.app/actions
              </a>
              .
            </Trans>
          </p>

          <Typography variant="h3">{t('manifesto.toGoFurther')}</Typography>

          <ul>
            <li>
              <p>
                <em>Prosocial Media</em> (2025). A. Tang.{' '}
                <a href="https://arxiv.org/abs/2502.10834">[lien]</a>
              </p>
            </li>
            <li>
              <p>
                <em>
                  Tournesol: A quest for a large, secure and trustworthy
                  database of reliable human judgments
                </em>{' '}
                (2021). <a href="https://arxiv.org/abs/2107.07334">[lien]</a>
              </p>
            </li>
            <li>
              <p>
                <em>
                  La Dictature des Algorithmes, Une transition démocratique est
                  possible
                </em>{' '}
                (2023). J.-L. Fourquet, L. N. Hoang.{' '}
                <a href="https://tallandier.com/livre/la-dictature-des-algorithmes/">
                  [lien]
                </a>
              </p>
            </li>
          </ul>

          <Typography variant="h3">{t('manifesto.notes.title')}</Typography>

          <table>
            <tbody>
              <tr>
                <td id="note1">
                  <a href="#ref1">[1]</a>
                </td>
                <td>
                  <Trans
                    i18nKey="manifesto.notes.facebookFilesMentalHealth"
                    t={t}
                  >
                    D’après les Facebook Files, une étude interne à
                    Facebook/Méta montre qu’Instagram contribue à dégrader la
                    santé mentale des adolescentes [
                    <a href="https://www.wsj.com/tech/personal-tech/facebook-knows-instagram-is-toxic-for-teen-girls-company-documents-show-11631620739">
                      Facebook Knows Instagram Is Toxic for Teen Girls...
                    </a>
                    ,{' '}
                    <a href="https://www.theatlantic.com/ideas/archive/2021/11/facebooks-dangerous-experiment-teen-girls/620767/">
                      The Dangerous Experiment on Teen Girls
                    </a>
                    ]. Aux États-Unis, 57% des adolescentes confient éprouver
                    une tristesse persistante ou du désespoir, contre 36% en
                    2011, et 30% révèlent avoir déjà songé à se suicider, contre
                    19% en 2011 [
                    <a href="https://www.cdc.gov/yrbs/dstr/index.html">
                      CDC Report, pp. 57, 61
                    </a>
                    ]. Les tendances sont similaires à travers le monde [
                    <a href="https://www.afterbabel.com/p/international-mental-illness-part-one">
                      International Mental Illness (1/2)
                    </a>
                    ;
                    <a href="https://www.afterbabel.com/p/international-mental-illness-part-two">
                      International Mental Illness (2/2)
                    </a>
                    ]. D’après des psychologues, l’hypothèse de l’accès constant
                    aux réseaux sociaux explique le mieux cette crise de la
                    santé mentale [
                    <a href="https://www.afterbabel.com/p/13-explanations-mental-health-crisis">
                      13 explanations of mental health crisis
                    </a>
                    ].
                  </Trans>
                </td>
              </tr>
              <tr>
                <td id="note2">
                  <a href="#ref2">[2]</a>
                </td>
                <td>
                  <Trans
                    i18nKey="manifesto.notes.facebookFilesPoliticians"
                    t={t}
                  >
                    Les Facebook Files révèlent l’influence des IA de
                    recommandation de Facebook sur les politiciens en 2017. Des
                    politiciens européens ont notamment écrit à Facebook, en
                    insistant sur le fait que les IA favorisaient alors beaucoup
                    plus radicalement les discours clivants, ce qui
                    contraignaient ces politiciens à être plus haineux pour
                    survivre politiquement.
                  </Trans>
                </td>
              </tr>
              <tr>
                <td id="note3">
                  <a href="#ref3">[3]</a>
                </td>
                <td>
                  <Trans i18nKey="manifesto.notes.elections" t={t}>
                    Plusieurs études rapportent des manipulations de processus
                    électoraux en Roumanie en 2024 sur TikTok, qui ont conduit à
                    l’annulation et au report de l’élection présidentielle [
                    <a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5243802">
                      Bader and Szabo 2025
                    </a>
                    ;{' '}
                    <a href="https://www.ceeol.com/search/article-detail?id=1344519">
                      Seceleanu and Garabet 2025
                    </a>
                    ;{' '}
                    <a href="https://understandingwar.org/sites/default/files/Romania%20special%20edition%20PDF_0.pdf">
                      Harward 2024
                    </a>
                    ]. Ces cas d’ingérence étrangère font écho à de nombreuses
                    autres sur le même sujet, comme dans le cas de Cambridge
                    Analytica en 2015 et 2016.
                  </Trans>
                </td>
              </tr>
              <tr>
                <td id="note4">
                  <a href="#ref4">[4]</a>
                </td>
                <td>
                  <Trans i18nKey="manifesto.notes.amplification" t={t}>
                    La sur-optimisation de l’engagement a des implications très
                    dangereuses sur l’amplification de la polarisation affective
                    et la désinformation [Twitter and Tear Gas 2017, The Hype
                    Machine 2021, Toxic Data 2022].
                  </Trans>
                </td>
              </tr>
              <tr>
                <td id="note5">
                  <a href="#ref5">[5]</a>
                </td>
                <td>
                  <Trans i18nKey="manifesto.notes.genocides" t={t}>
                    L’Organisation des Nations Unies et Amnesty International
                    accusent Facebook d’avoir sciemment contribué à des
                    génocides, en particulier au génocide des Rohingyas en
                    Birmanie, en promouvant des discours de haine contre les
                    minorités [
                    <a href="https://www.amnesty.org/en/latest/news/2022/09/myanmar-facebooks-systems-promoted-violence-against-rohingya-meta-owes-reparations-new-report/">
                      Amnesty International #1
                    </a>
                    ,{' '}
                    <a href="https://www.amnesty.org/en/documents/asa16/5933/2022/en/">
                      Amnesty International #2
                    </a>
                    ].
                    {/* [TODO: sourcer ONU] */}
                  </Trans>
                </td>
              </tr>
              <tr>
                <td id="note6">
                  <a href="#ref6">[6]</a>
                </td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </Paper>
      </ContentBox>
    </>
  );
};

export default ManifestoPage;
