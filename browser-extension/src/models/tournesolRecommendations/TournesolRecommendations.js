import { convertDurationToClockDuration } from '../../utils.js';
import { defaultTournesolRecommendationsOptions } from './TournesolRecommendationsOptions.js';

export class TournesolRecommendations {
  constructor(options = defaultTournesolRecommendationsOptions) {
    this.isPageLoaded = false;
    this.isExpanded = false;
    this.areRecommendationsLoading = false;
    this.areRecommendationsLoaded = false;
    this.videos = [];
    this.additionalVideos = [];
    this.recommendationsLanguage = 'en';

    this.videosPerRow = options.videosPerRow;
    this.rowsWhenExpanded = options.rowsWhenExpanded;
    this.path = options.path;
    this.banner = options.banner;
    this.parentComponentQuery = options.parentComponentQuery;
    this.handleResponse = this.handleResponse.bind(this);
  }

  getParentComponent() {
    try {
      // Get parent element for the boxes in youtube page
      let contents;

      contents = document.querySelector(this.parentComponentQuery);

      if (!contents || !contents.children[1]) return;

      return contents;
    } catch (error) {
      return;
    }
  }

  getTournesolComponent() {
    // remove the component before rerender so it's not duplicate
    if (this.tournesol_component) this.tournesol_component.remove();
    // Create new container
    let tournesol_container = document.createElement('div');
    tournesol_container.id = 'tournesol_container';

    // Add inline-block div
    const inline_div = document.createElement('div');
    inline_div.setAttribute('class', 'inline_div');

    // Add tournesol icon
    const tournesol_icon = document.createElement('img');
    tournesol_icon.setAttribute('id', 'tournesol_icon');
    tournesol_icon.setAttribute(
      'src',
      //chrome.extension.getURL('rate_now_icon.png'),
      'https://tournesol.app/svg/tournesol.svg'
    );
    tournesol_icon.setAttribute('width', '24');
    inline_div.append(tournesol_icon);

    // Add title
    const tournesol_title = document.createElement('h1');
    tournesol_title.id = 'tournesol_title';
    tournesol_title.append(chrome.i18n.getMessage('recommendedByTournesol'));
    inline_div.append(tournesol_title);

    // Display the campaign button only if there is a banner.
    if (this.banner.bannerShouldBeDisplayed()) {
      const campaignButton = document.createElement('button');
      campaignButton.id = 'tournesol_campaign_button';
      campaignButton.className = 'tournesol_simple_button';

      const campaignButtonImg = document.createElement('img');
      campaignButtonImg.setAttribute(
        'src',
        chrome.extension.getURL('images/campaign.svg')
      );
      campaignButtonImg.setAttribute('alt', 'Megaphone icon');
      campaignButton.append(campaignButtonImg);

      campaignButton.onclick = () => {
        chrome.storage.local.set({ displayBannerStudy2023: true }, () => {
          this.banner.displayBanner();
        });
      };

      inline_div.append(campaignButton);
    }

    // Refresh button
    const refresh_button = document.createElement('button');
    refresh_button.setAttribute('id', 'tournesol_refresh_button');
    fetch(chrome.runtime.getURL('images/sync-alt.svg'))
      .then((r) => r.text())
      .then((svg) => (refresh_button.innerHTML = svg));

    refresh_button.className = 'tournesol_simple_button';
    refresh_button.onclick = () => {
      refresh_button.disabled = true;
      this.loadRecommandations();
    };
    inline_div.append(refresh_button);

    // Add title
    const tournesol_link = document.createElement('a');
    tournesol_link.id = 'tournesol_link';
    tournesol_link.href = 'https://tournesol.app?utm_source=extension';
    tournesol_link.target = '_blank';
    tournesol_link.rel = 'noopener';
    tournesol_link.append(chrome.i18n.getMessage('learnMore'));
    inline_div.append(tournesol_link);

    // Bottom action bar
    const bottom_action_bar = document.createElement('div');
    bottom_action_bar.id = 'ts_container_bottom_action_bar';
    const expand_button = document.createElement('button');
    expand_button.setAttribute('id', 'tournesol_expand_button');

    // A new button is created on each video loading, the image must be loaded accordingly
    fetch(
      chrome.runtime.getURL(
        this.isExpanded ? 'images/chevron-up.svg' : 'images/chevron-down.svg'
      )
    )
      .then((r) => r.text())
      .then((svg) => (expand_button.innerHTML = svg));
    expand_button.className = 'tournesol_simple_button';
    expand_button.onclick = () => {
      expand_button.disabled = true;
      if (!this.areRecommendationsLoading && !this.isExpanded) {
        this.isExpanded = true;
        this.displayRecommendations();
      } else if (this.isExpanded) {
        this.isExpanded = false;
        this.displayRecommendations();
      }
    };
    bottom_action_bar.append(expand_button);

    tournesol_container.append(inline_div);

    if (this.banner.bannerShouldBeDisplayed()) {
      tournesol_container.append(this.banner.banner);
    }

    const videosFlexContainer = this.createVideosFlexContainer();
    tournesol_container.append(videosFlexContainer);

    this.videos.forEach((video) =>
      videosFlexContainer.append(this.make_video_box(video))
    );
    if (this.isExpanded) {
      this.additionalVideos.forEach((video) =>
        videosFlexContainer.append(this.make_video_box(video))
      );
    }
    tournesol_container.append(bottom_action_bar);

    if (this.path == '/results') {
      tournesol_container.classList.add('search');

      const view_more_container = document.createElement('div');
      view_more_container.classList = 'view_more_container';

      const view_more_link = document.createElement('a');
      view_more_link.className = 'tournesol_mui_like_button view_more_link';
      view_more_link.target = '_blank';
      view_more_link.rel = 'noopener';
      view_more_link.href = `https://tournesol.app/recommendations/?search=${
        this.searchQuery
      }&language=${this.recommandationsLanguages.replaceAll(
        ',',
        '%2C'
      )}&utm_source=extension`;
      view_more_link.textContent = chrome.i18n.getMessage('viewMore');

      view_more_container.append(view_more_link);
      tournesol_container.append(view_more_container);
    }

    return tournesol_container;
  }

  createVideosFlexContainer() {
    const container = document.createElement('div');
    container.id = 'tournesol_videos_flexcontainer';
    return container;
  }

  make_video_box(video) {
    // Div whith everything about a video
    const video_box = document.createElement('div');
    video_box.className = 'video_box';

    // Div with thumbnail and video duration
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

    video_box.append(thumb_div);

    // Div with uploader name, video title and tournesol score
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
      this.millifyViews(video.metadata.views),
    ])} <span class="dot">&nbsp•&nbsp</span> ${this.viewPublishedDate(
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

    /**
     * If the content script is executed on the YT research page.
     */
    if (this.path == '/results') {
      const video_criteria = document.createElement('div');
      video_criteria.className = 'video_text video_criteria';

      if (video.criteria_scores.length > 1) {
        const sortedCriteria = video.criteria_scores
          .filter((criteria) => criteria.criteria != 'largely_recommended')
          .sort((a, b) => a.score - b.score);

        const lower = sortedCriteria[0];
        const higher = sortedCriteria[sortedCriteria.length - 1];

        const lowerCriteriaTitle = `${chrome.i18n.getMessage(
          lower.criteria
        )}: ${Math.round(lower.score)}`;
        const higherCriteriaTitle = `${chrome.i18n.getMessage(
          higher.criteria
        )}: ${Math.round(higher.score)}`;

        const lowerCriteriaIconUrl = `images/criteriaIcons/${lower.criteria}.svg`;
        const higherCriteriaIconUrl = `images/criteriaIcons/${higher.criteria}.svg`;
        let lowerCriteriaIcon;
        let higherCriteriaIcon;

        fetch(chrome.runtime.getURL(higherCriteriaIconUrl))
          .then((r) => r.text())
          .then((svg) => {
            higherCriteriaIcon =
              'data:image/svg+xml;base64,' + window.btoa(svg);

            if (higher.score > 0) {
              video_criteria.innerHTML += `${chrome.i18n.getMessage(
                'ratedHigh'
              )} <img src=${higherCriteriaIcon} title='${higherCriteriaTitle}' />`;
            }

            if (lower.score < 0) {
              fetch(chrome.runtime.getURL(lowerCriteriaIconUrl))
                .then((r) => r.text())
                .then(
                  (svg) =>
                    (lowerCriteriaIcon =
                      'data:image/svg+xml;base64,' + window.btoa(svg))
                )
                .then(() => {
                  video_criteria.innerHTML += ` ${chrome.i18n.getMessage(
                    'ratedLow'
                  )} <img src='${lowerCriteriaIcon}' title='${lowerCriteriaTitle}' />`;

                  details_div.append(video_criteria);
                });
            } else {
              details_div.append(video_criteria);
            }
          });
      }
    }

    video_box.append(details_div);

    return video_box;
  }

  // This part creates video boxes from API's response JSON
  displayRecommendations() {
    if (!this.videos || this.videos.length === 0) {
      // remove the component if we did not receive video from the response
      // so it remove the videos from the previous results
      if (this.tournesol_component) this.tournesol_component.remove();
      return;
    }

    // Timer will run until needed elements are generated
    var timer = window.setInterval(() => {
      /*
       ** Wait for needed elements to be generated
       ** It seems those elements are generated via javascript, so run-at document_idle in manifest is not enough to prevent errors
       **
       ** Some ids on video pages are duplicated, so I take the first non-duplicated id and search in its childs the correct div to add the recommendations
       ** Note: using .children[index] when child has no id
       */

      // Get the container on Youtube home page in which we will insert Tournesol's component
      let container = this.getParentComponent();

      if (!container) return;
      window.clearInterval(timer);

      // Generate component to display on Youtube home page

      this.tournesol_component = this.getTournesolComponent();
      container.insertBefore(this.tournesol_component, container.children[1]);
    }, 300);
  }

  handleResponse({
    data: videosResponse,
    recommandationsLanguages: languagesString = 'en',
  }) {
    this.areRecommendationsLoading = false;
    this.areRecommendationsLoaded = true;
    this.videos = videosResponse.slice(0, this.videosPerRow);
    this.additionalVideos = videosResponse.slice(this.videosPerRow);
    this.recommandationsLanguages = languagesString;

    if (this.isPageLoaded) {
      this.displayRecommendations();
    }
  }

  loadRecommandations() {
    // Only enable on youtube.com/
    if (location.pathname != this.path) return;

    if (this.areRecommendationsLoading) return;

    this.areRecommendationsLoading = true;

    chrome.runtime.sendMessage(
      {
        message: 'getTournesolRecommendations',
        videosNumber: this.videosPerRow,
        additionalVideosNumber: this.videosPerRow * (this.rowsWhenExpanded - 1),
      },
      this.handleResponse
    );
  }

  process() {
    this.isPageLoaded = true;

    if (location.pathname === this.path) {
      if (this.videos.length > 0) {
        this.displayRecommendations();
      } else if (!this.areRecommendationsLoaded) {
        // If the content script is loaded on a non-root URL the recommendations
        // are not loaded. So if the user then goes to the root URL and the content
        // script is not reloaded, we need to load the recommendations.
        this.loadRecommandations();
      }
    }
  }

  millifyViews(videoViews) {
    // Intl.NumberFormat object is in-built and enables language-sensitive number formatting
    return Intl.NumberFormat('en', { notation: 'compact' }).format(videoViews);
  }

  viewPublishedDate(publishedDate) {
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
