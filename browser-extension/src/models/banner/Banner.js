/**
 * A banner displaying a message and an action button.
 */
export class Banner {
  constructor({
    name,
    dateStart,
    dateEnd,
    title,
    text,
    actionLabel,
    actionLink,
    securityAdvisory,
  }) {
    this.name = name;
    this.dateStart = dateStart;
    this.dateEnd = dateEnd;
    this.title = title;
    this.text = text;
    this.actionLabel = actionLabel;
    this.actionLink = actionLink;
    this.securityAdvisory = securityAdvisory;

    this.displayBannerKey = `displayBanner:${this.name}`;

    // Create the banner at the initialisation.
    this.element = this.createBanner();
  }

  display() {
    this.element.classList.add('displayed');
  }

  hide() {
    this.element.classList.remove('displayed');
  }

  bannerShouldBeDisplayed() {
    const now = new Date();

    if (this.dateStart <= now && now <= this.dateEnd) {
      return true;
    }

    return false;
  }

  async loadDisplayPreference() {
    const { displayBannerKey } = this;

    return new Promise((resolve) => {
      chrome.storage.local.get(displayBannerKey, (result) => {
        const displayBanner = result[displayBannerKey] ?? true;
        resolve(displayBanner);
      });
    });
  }

  async saveDisplayPreference(value) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [this.displayBannerKey]: value }, () => {
        resolve();
      });
    });
  }

  createBanner() {
    const banner = document.createElement('div');
    banner.id = 'tournesol_banner';
    banner.className = 'tournesol_banner';

    // Only display the banner if the user didn't explicitly close it.
    this.loadDisplayPreference().then((displayBanner) => {
      if (displayBanner) this.display();
    });

    // The first flex item is the campaign icon.
    const bannerIconContainer = document.createElement('div');
    const icon = document.createElement('img');
    icon.id = 'tournesol_banner_icon';
    const { iconName, iconClass, iconAltKey } = this.securityAdvisory
      ? {
          iconName: 'warning',
          iconClass: 'security',
          iconAltKey: 'securityIconAlt',
        }
      : {
          iconName: 'campaign',
          iconClass: 'campaign',
          iconAltKey: 'campaignIconAlt',
        };
    icon.setAttribute('src', chrome.runtime.getURL(`images/${iconName}.svg`));
    icon.classList.add(iconClass);
    icon.setAttribute('alt', chrome.i18n.getMessage(iconAltKey));
    bannerIconContainer.append(icon);
    banner.appendChild(bannerIconContainer);

    // The second flex item is the text.
    const bannerTextContainer = document.createElement('div');
    const bannerTitle = document.createElement('h2');
    bannerTitle.id = 'tournesol_banner_title';
    bannerTitle.textContent = this.title;
    bannerTextContainer.append(bannerTitle);

    const bannerText = document.createElement('p');
    bannerText.textContent = this.text;
    bannerTextContainer.append(bannerText);
    banner.appendChild(bannerTextContainer);

    // The third flex item is the action button.
    if (this.actionLabel && this.actionLink) {
      const actionButtonContainer = document.createElement('div');
      const actionButton = document.createElement('a');
      actionButton.textContent = this.actionLabel;
      actionButton.className = 'tournesol_mui_like_button';
      actionButton.setAttribute('href', this.actionLink);
      actionButton.setAttribute('target', '_blank');
      actionButton.setAttribute('rel', 'noopener');
      actionButtonContainer.append(actionButton);
      banner.appendChild(actionButtonContainer);
    }

    // The last flex item is the close button.
    const closeButtonContainer = document.createElement('div');
    closeButtonContainer.id = 'tournesol_banner_close_button_container';
    const closeButton = document.createElement('button');
    closeButton.className = 'tournesol_simple_button';
    const closeButtonImg = document.createElement('img');
    closeButtonImg.id = 'tournesol_banner_close_icon';
    closeButtonImg.setAttribute(
      'src',
      chrome.runtime.getURL('images/close.svg')
    );
    closeButtonImg.setAttribute('alt', chrome.i18n.getMessage('closeIconAlt'));
    closeButton.append(closeButtonImg);
    closeButtonContainer.append(closeButton);
    banner.appendChild(closeButtonContainer);

    closeButton.onclick = async () => {
      await this.saveDisplayPreference(false);
      this.hide();
    };

    return banner;
  }
}
