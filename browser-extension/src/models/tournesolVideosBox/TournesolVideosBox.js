import { convertDurationToClockDuration } from '../../utils.js';

export class TournesolVideosBox {
  static async makeBox(video, displayCriteria) {
    // Div whith everything about a video
    const video_box = document.createElement('div');
    video_box.className = 'video_box';

    // Div with thumbnail and video duration
    const thumb_div = TournesolVideosBox.getThumbDiv(video);

    video_box.append(thumb_div);

    // Div with uploader name, video title and tournesol score
    const details_div = TournesolVideosBox.getDetailsDiv(video);

    /**
     * If the content script is executed on the YT research page
     * add criteria to the details_div
     */
    if (displayCriteria) {
      const video_criteria = await TournesolVideosBox.getVideoCriteriaElement(
        video
      );

      details_div.append(video_criteria);
    }

    video_box.append(details_div);

    return video_box;
  }

  static async getVideoCriteriaElement(video) {
    const video_criteria = document.createElement('div');
    video_criteria.className = 'video_text video_criteria';

    // if there is more than the largely recommended criteria
    if (video.criteria_scores.length > 1) {
      /**
       * Filter the largely_recommended criteria out of the criteria_scores
       * and sort by score
       */
      const sortedCriteria = video.criteria_scores
        .filter((criteria) => criteria.criteria != 'largely_recommended')
        .sort((a, b) => a.score - b.score);

      const lowestCriteria = sortedCriteria[0];
      const highestCriteria = sortedCriteria[sortedCriteria.length - 1];

      const lowestCriteriaTitle = `${chrome.i18n.getMessage(
        lowestCriteria.criteria
      )}: ${Math.round(lowestCriteria.score)}`;
      const highestCriteriaTitle = `${chrome.i18n.getMessage(
        highestCriteria.criteria
      )}: ${Math.round(highestCriteria.score)}`;

      const lowestCriteriaIconUrl = `images/criteriaIcons/${lowestCriteria.criteria}.svg`;
      const highestCriteriaIconUrl = `images/criteriaIcons/${highestCriteria.criteria}.svg`;

      let lowestCriteriaIcon;
      let highestCriteriaIcon;

      if (highestCriteria.score > 0) {
        const svg = await fetch(
          chrome.runtime.getURL(highestCriteriaIconUrl)
        ).then((r) => r.text());

        highestCriteriaIcon = 'data:image/svg+xml;base64,' + window.btoa(svg);

        video_criteria.innerHTML += `${chrome.i18n.getMessage(
          'ratedHigh'
        )} <img src=${highestCriteriaIcon} title='${highestCriteriaTitle}' />`;
      }

      if (lowestCriteria.score < 0) {
        const svg = await fetch(
          chrome.runtime.getURL(lowestCriteriaIconUrl)
        ).then((r) => r.text());

        lowestCriteriaIcon = 'data:image/svg+xml;base64,' + window.btoa(svg);

        video_criteria.innerHTML += `${chrome.i18n.getMessage(
          'ratedLow'
        )} <img src=${lowestCriteriaIcon} title='${lowestCriteriaTitle}' />`;
      }
    }

    return video_criteria;
  }

  static getThumbDiv(video) {
    const thumb_div = document.createElement('div');
    thumb_div.setAttribute('class', 'thumb_div');

    const video_thumb = document.createElement('img');
    video_thumb.className = 'video_thumb';
    video_thumb.src = `https://img.youtube.com/vi/${video.metadata.video_id}/mqdefault.jpg`;
    thumb_div.append(video_thumb);

    const video_duration = document.createElement('p');
    video_duration.setAttribute('class', 'time_span');

    // Convert SECONDS to hh:mm:ss or mm:ss format depending on the duration

    var formatted_video_duration = convertDurationToClockDuration(
      video.metadata.duration
    );

    video_duration.append(document.createTextNode(formatted_video_duration));
    thumb_div.append(video_duration);

    const video_link = document.createElement('a');
    video_link.className = 'video_link';
    video_link.href = '/watch?v=' + video.metadata.video_id;
    thumb_div.append(video_link);

    return thumb_div;
  }

  static getDetailsDiv(video) {
    const details_div = document.createElement('div');
    details_div.setAttribute('class', 'details_div');

    const video_title = document.createElement('h2');
    video_title.className = 'video_title';

    const video_title_link = document.createElement('a');
    video_title_link.className = 'video_title_link';
    video_title_link.href = '/watch?v=' + video.metadata.video_id;
    video_title_link.append(video.metadata.name);

    video_title.append(video_title_link);
    details_div.append(video_title);

    const video_channel_details = document.createElement('div');
    video_channel_details.classList.add('video_channel_details');

    const video_uploader = document.createElement('p');
    video_uploader.className = 'video_text';

    const video_channel_link = document.createElement('a');
    video_channel_link.classList.add('video_channel_link');
    video_channel_link.textContent = video.metadata.uploader;
    video_channel_link.href = `https://youtube.com/channel/${video.metadata.channel_id}`;

    video_uploader.append(video_channel_link);
    video_channel_details.append(video_uploader);

    const video_views_publication = document.createElement('p');
    video_views_publication.className = 'video_text';
    video_views_publication.innerHTML = `${chrome.i18n.getMessage('views', [
      TournesolVideosBox.millifyViews(video.metadata.views),
    ])} <span class="dot">&nbsp•&nbsp</span> ${TournesolVideosBox.viewPublishedDate(
      video.metadata.publication_date
    )}`;
    video_channel_details.append(video_views_publication);
    details_div.append(video_channel_details);

    const video_score = document.createElement('p');
    video_score.className = 'video_text video_tournesol_rating';
    video_score.innerHTML = `<img
          class="tournesol_score_logo"
          src="https://tournesol.app/svg/tournesol.svg"
          alt="Tournesol logo"
        />
          <strong>
            ${video.tournesol_score.toFixed(0)}
            <span class="dot">&nbsp·&nbsp</span>
          </strong>
          <span>${chrome.i18n.getMessage('comparisonsBy', [
            video.n_comparisons,
          ])}</span>&nbsp
          <span class="contributors">
            ${chrome.i18n.getMessage('comparisonsContributors', [
              video.n_contributors,
            ])}
          </span>`;
    details_div.append(video_score);

    return details_div;
  }

  static millifyViews(videoViews) {
    // Intl.NumberFormat object is in-built and enables language-sensitive number formatting
    return Intl.NumberFormat('en', { notation: 'compact' }).format(videoViews);
  }

  static viewPublishedDate(publishedDate) {
    const date1 = new Date(publishedDate);
    const date2 = new Date();
    // we will find the difference in time of today's date and the published date, and will convert it into Days
    // after calculating no. of days, we classify it into days, weeks, months, years, etc.
    const diffTime = date2.getTime() - date1.getTime();

    if (diffTime < 0) {
      //in case the local machine UTC time is less than the published date
      return '';
    }
    const diffDays = Math.floor(diffTime / (1000 * 3600 * 24));

    if (diffDays == 0) {
      return chrome.i18n.getMessage('publishedToday');
    } else if (diffDays == 1) {
      return chrome.i18n.getMessage('publishedYesterday');
    } else if (diffDays < 31) {
      if (diffDays < 14) {
        return chrome.i18n.getMessage('publishedSomeDaysAgo', [diffDays]);
      } else {
        return chrome.i18n.getMessage('publishedSomeWeeksAgo', [
          Math.floor(diffDays / 7),
        ]);
      }
    } else if (diffDays < 365) {
      if (diffDays < 61) {
        return chrome.i18n.getMessage('publishedAMonthAgo');
      } else {
        return chrome.i18n.getMessage('publishedSomeMonthsAgo', [
          Math.floor(diffDays / 30),
        ]);
      }
    } else {
      if (diffDays < 730) {
        return chrome.i18n.getMessage('publishedAYearAgo');
      } else {
        return chrome.i18n.getMessage('publishedSomeYearsAgo', [
          Math.floor(diffDays / 365),
        ]);
      }
    }
  }
}
