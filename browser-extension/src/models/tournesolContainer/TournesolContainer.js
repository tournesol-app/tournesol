import { TournesolVideoCard } from '../tournesolVideoCard/TournesolVideoCard.js';

export class TournesolContainer {
  constructor(parent, banner) {
    this.isExpanded = false;
    this.parent = parent;
    this.banner = banner;
  }

  createHTMLElement() {
    // Create container
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
          this.banner.display();
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
      this.parent.loadRecommandations();
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
        this.parent.displayRecommendations();
      } else if (this.isExpanded) {
        this.isExpanded = false;
        this.parent.displayRecommendations();
      }
    };
    bottom_action_bar.append(expand_button);

    tournesol_container.append(inline_div);

    if (this.banner.bannerShouldBeDisplayed()) {
      tournesol_container.append(this.banner.banner);
    }

    const videosFlexContainer = this._createVideosFlexContainer();
    tournesol_container.append(videosFlexContainer);

    this.parent.videos.forEach((video) => {
      const videoCard = TournesolVideoCard.makeCard(
        video,
        this.parent.displayCriteria
      );
      videosFlexContainer.append(videoCard);
    });

    if (this.isExpanded) {
      this.parent.additionalVideos.forEach((video) => {
        const videoCard = TournesolVideoCard.makeCard(
          video,
          this.parent.displayCriteria
        );
        videosFlexContainer.append(videoCard);
      });
    }
    tournesol_container.append(bottom_action_bar);

    if (location.pathname == '/results') {
      tournesol_container.classList.add('search');

      const view_more_container = document.createElement('div');
      view_more_container.id = 'tournesol_view_more_results';

      const view_more_link = document.createElement('a');
      view_more_link.className =
        'tournesol_mui_like_button view_more_link small';
      view_more_link.target = '_blank';
      view_more_link.rel = 'noopener';
      view_more_link.href = `https://tournesol.app/recommendations/?search=${
        this.parent.searchQuery
      }&language=${this.parent.recommandationsLanguages.replaceAll(
        ',',
        '%2C'
      )}&utm_source=extension`;
      view_more_link.textContent = chrome.i18n.getMessage('viewMore');

      view_more_container.append(view_more_link);
      tournesol_container.append(view_more_container);
    }

    return tournesol_container;
  }

  _createVideosFlexContainer() {
    const container = document.createElement('div');
    container.id = 'tournesol_videos_flexcontainer';
    return container;
  }
}
