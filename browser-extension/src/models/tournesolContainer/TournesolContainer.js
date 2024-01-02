import { TournesolVideoCard } from '../tournesolVideoCard/TournesolVideoCard.js';
import { frontendUrl } from '../../config.js';

export class TournesolContainer {
  /**
   * @param {TournesolRecommendations} recommendations An object containing the videos to display.
   * @param {Banner} banner An optional banner displayed if its display conditions are satisfied.
   */
  constructor(recommendations, banner) {
    this.isExpanded = false;
    this.banner = banner;
    this.recommendations = recommendations;

    this.htmlID = 'tournesol_container';
  }

  /**
   * Remove the Tournesol container from the DOM and all potential duplicates.
   */
  removeExistingContainers() {
    const containers = document.querySelectorAll(`#${this.htmlID}`);
    if (containers.length > 0) {
      containers.forEach((container) => container.remove());
    }
  }

  createHTMLElement() {
    const tournesolContainer = document.createElement('div');
    tournesolContainer.id = this.htmlID;

    const topActionBar = this._createTopActionBar();
    const videosFlexContainer = this._createVideosFlexContainer();
    const bottomActionBar = this._createBottomActionBar();

    tournesolContainer.append(topActionBar);

    if (this.banner && this.banner.bannerShouldBeDisplayed()) {
      tournesolContainer.append(this.banner.element);
    }

    tournesolContainer.append(videosFlexContainer);

    this.recommendations.videos.forEach((video) => {
      const videoCard = TournesolVideoCard.makeCard(
        video,
        this.recommendations.displayCriteria
      );
      videosFlexContainer.append(videoCard);
    });

    if (this.isExpanded) {
      this.recommendations.additionalVideos.forEach((video) => {
        const videoCard = TournesolVideoCard.makeCard(
          video,
          this.recommendations.displayCriteria
        );
        videosFlexContainer.append(videoCard);
      });
    }

    tournesolContainer.append(bottomActionBar);

    if (location.pathname == '/results') {
      tournesolContainer.classList.add('search');

      const view_more_container = document.createElement('div');
      view_more_container.id = 'tournesol_view_more_results';

      const view_more_link = document.createElement('a');
      view_more_link.className =
        'tournesol_mui_like_button view_more_link small';
      view_more_link.target = '_blank';
      view_more_link.rel = 'noopener';
      view_more_link.href = `${frontendUrl}/recommendations?search=${
        this.recommendations.searchQuery
      }&language=${this.recommendations.recommandationsLanguages.replaceAll(
        ',',
        '%2C'
      )}&utm_source=extension`;
      view_more_link.textContent = chrome.i18n.getMessage('viewMore');

      view_more_container.append(view_more_link);
      tournesolContainer.append(view_more_container);
    }

    return tournesolContainer;
  }

  _createTopActionBar() {
    const topActionBar = document.createElement('div');
    topActionBar.id = 'ts_container_top_action_bar';

    // Tournesol icon
    const tournesolIcon = document.createElement('img');
    tournesolIcon.setAttribute('id', 'tournesol_icon');
    tournesolIcon.setAttribute('src', `${frontendUrl}/svg/tournesol.svg`);
    tournesolIcon.setAttribute('width', '24');
    topActionBar.append(tournesolIcon);

    // Container title
    const tournesolTitle = document.createElement('h1');
    tournesolTitle.id = 'tournesol_title';
    tournesolTitle.append(chrome.i18n.getMessage('recommendedByTournesol'));
    topActionBar.append(tournesolTitle);

    // Learn more
    const learnMore = document.createElement('a');
    learnMore.id = 'tournesol_link';
    learnMore.href = `${frontendUrl}?utm_source=extension`;
    learnMore.target = '_blank';
    learnMore.rel = 'noopener';
    learnMore.append(chrome.i18n.getMessage('learnMore'));
    topActionBar.append(learnMore);

    // Display the campaign button only if there is a banner.
    if (this.banner && this.banner.bannerShouldBeDisplayed()) {
      const campaignButton = document.createElement('button');
      campaignButton.id = 'tournesol_campaign_button';
      campaignButton.className = 'tournesol_simple_button emphatic';

      const campaignButtonImg = document.createElement('img');
      campaignButtonImg.setAttribute(
        'src',
        chrome.runtime.getURL('images/campaign.svg')
      );
      campaignButtonImg.setAttribute('alt', 'Megaphone icon');
      campaignButton.append(campaignButtonImg);

      campaignButton.onclick = async () => {
        await this.banner.saveDisplayPreference(true);
        this.banner.display();
      };

      topActionBar.append(campaignButton);
    }

    const preferencesButton = document.createElement('button');
    preferencesButton.id = 'tournesol_preferences_buton';
    preferencesButton.title = chrome.i18n.getMessage('menuPreferences');

    const preferencesImg = document.createElement('img');
    preferencesImg.src = chrome.runtime.getURL('images/settings.svg');
    preferencesButton.append(preferencesImg);

    preferencesButton.className = 'tournesol_simple_button';
    preferencesButton.onclick = () => {
      chrome.runtime.sendMessage({ message: 'openOptionsPage' });
    };
    topActionBar.append(preferencesButton);

    // Refresh button
    const refreshButton = document.createElement('button');
    refreshButton.id = 'tournesol_refresh_button';
    refreshButton.title = chrome.i18n.getMessage('refreshRecommendations');

    const refreshImg = document.createElement('img');
    refreshImg.src = chrome.runtime.getURL('images/sync-alt.svg');
    refreshButton.append(refreshImg);

    refreshButton.className = 'tournesol_simple_button';
    refreshButton.onclick = () => {
      refreshButton.disabled = true;
      this.recommendations.loadRecommandations();
    };
    topActionBar.append(refreshButton);

    return topActionBar;
  }

  _createBottomActionBar() {
    const bottomActionBar = document.createElement('div');
    bottomActionBar.id = 'ts_container_bottom_action_bar';
    const expand_button = document.createElement('button');
    expand_button.id = 'tournesol_expand_button';
    if (!this.isExpanded) {
      expand_button.title = chrome.i18n.getMessage('seeMoreRecommendations');
    }

    // A new button is created on each video loading, the image must be loaded accordingly
    const expandImg = document.createElement('img');
    expandImg.src = chrome.runtime.getURL(
      this.isExpanded ? 'images/chevron-up.svg' : 'images/chevron-down.svg'
    );
    expand_button.append(expandImg);

    expand_button.className = 'tournesol_simple_button';
    expand_button.onclick = () => {
      expand_button.disabled = true;
      if (!this.areRecommendationsLoading && !this.isExpanded) {
        this.isExpanded = true;
        this.recommendations.displayRecommendations();
      } else if (this.isExpanded) {
        this.isExpanded = false;
        this.recommendations.displayRecommendations();
      }
    };
    bottomActionBar.append(expand_button);

    return bottomActionBar;
  }

  _createVideosFlexContainer() {
    const container = document.createElement('div');
    container.id = 'tournesol_videos_flexcontainer';
    return container;
  }
}
