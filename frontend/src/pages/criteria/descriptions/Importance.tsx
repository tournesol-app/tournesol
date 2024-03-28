import React from 'react';
import { Trans } from 'react-i18next';

import { ExternalLink } from 'src/components';

const ImportanceDesc = () => (
  <Trans i18nKey="criteriaDescriptions.importance">
    <em>
      Can additional focus on this topic have a significantly positive impact on
      the world?
    </em>
    <p>
      This criterion aims to combat the problem of <em>mute news</em>, which are
      information that do not have the attention that they should have for the
      good of humanity and beyond. As an example, as explained by{' '}
      <ExternalLink href="https://tournesol.app/entities/yt:KdiA12KeSL0">
        this PBS Hot Mess video
      </ExternalLink>
      , when it comes to mitigating climate change, asking viewers to switch off
      the light when not at home is orders of magnitude less important than,
      say, avoiding air travel.
    </p>
    <p>
      Contents that score high on &quot;important and actionable&quot; should
      present data and arguments with major consequences, as well as actionable
      plans that would have large-scale mpacts.
    </p>
    <h3>Scale</h3>
    <p>
      Plans with large-scale impacts are more important, as they affect more
      individuals at once.
    </p>
    <h3>Actionable and tractable</h3>
    <p>
      A content that simply lists problem is arguably less important to share
      than a content that both lists problems and propose actionable solutions.
    </p>
    <p>
      The content is all the more important if it calls for actionable plans
      from the viewers (even though these plans may consist in creating social
      pressure on other individuals).
    </p>
    <h3>Other aspects</h3>
    <p>
      When judging the importance of a content, it may be relevant to reflect on
      whether the content stresses the important features of the topic it
      discusses. In particular, introductions and conclusions may be what
      catches viewers&apos; attention the most. Does the content open and close
      with important considerations?
    </p>
    <p>
      According to Bayesianism, <em>surprising</em> data ought to have a much
      larger impact on a (Bayesian) viewer&apos;s beliefs. In practice, viewers
      are not Bayesian. This is why, in addition to presenting surprising data
      to viewers, it is also important to also stress the surprisingness of the
      data or argument, by highlighting it. This means underlining the
      neglectedness of the data or argument.
    </p>
  </Trans>
);

export default ImportanceDesc;
