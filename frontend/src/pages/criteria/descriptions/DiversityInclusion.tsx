import React from 'react';
import { Trans } from 'react-i18next';

import { ExternalLink } from 'src/components';

const DiversityInclusionDesc = () => (
  <Trans i18nKey="criteriaDescriptions.diversity_inclusion">
    <em>
      Does it promote tolerance, compassion and wider moral considerations?
    </em>
    <p>
      This criterion aims at identifying contents that promote a more diverse
      and inclusive view of the great diversity of all life. Contents that score
      high on &quot;diversity and inclusion&quot; should celebrate diversity and
      be appealing to minority groups. Among other things, diverse and inclusive
      content promote:
    </p>
    <ul>
      <li>
        The diversity of humanity&apos;s ethnics, beliefs and preferences,
        especially in fields that deeply lack such a diversity,
      </li>
      <li>The lifes of all sentient beings (e.g. non-human animals),</li>
      <li>The well-being of young and future generations,</li>
      <li>The diversity of genders and sexual orientations,</li>
      <li>
        The inclusion of all species in our moral circles and the protection of
        biodiversity.
      </li>
    </ul>
    <p>
      When judging this feature, contributors are encouraged to reflect on what
      both privileged and underprivileged viewers may feel when viewing the
      content. Contents that normalize biases or that disregard the interests of
      under-represented groups, purposely or not, should be rated negatively
      along this feature.
    </p>
    <h3>Example</h3>
    <p>
      Typically the below videos may be referred to as high diversity and
      inclusion.
    </p>
    <ul>
      <li>
        <ExternalLink href="https://www.youtube.com/watch?v=_JVwyW4zxQ4&t=775s">
          Tibees&apos; video &quot;The First Computer Program&quot;
        </ExternalLink>
      </li>
      <li>
        <ExternalLink href="https://tournesol.app/entities/yt:ybPgmjTRvMo">
          Mark Robert&apos;s video &quot;The Truth About my Son&quot;
        </ExternalLink>
      </li>
      <li>
        <ExternalLink href="https://tournesol.app/entities/yt:qF1DTK4U1AM">
          Jaiden Animations&apos; video &quot;Being not Straight&quot;
        </ExternalLink>
      </li>
      <li>
        <ExternalLink href="https://tournesol.app/entities/yt:Ok5sKLXqynQ">
          Vox&apos;s video &quot;Are we Automating Racism?&quot;
        </ExternalLink>
      </li>
    </ul>
  </Trans>
);

export default DiversityInclusionDesc;
