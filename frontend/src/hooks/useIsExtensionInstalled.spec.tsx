import React from 'react';
import { render, screen } from '@testing-library/react';

import { useIsExtensionInstalled } from './useIsExtensionInstalled';

const EXTENSION_INSTALLED_ATTRIBUTE = 'data-tournesol-extension-installed';

const ExtensionProbe = () => {
  const isInstalled = useIsExtensionInstalled();
  return <span>{isInstalled ? 'installed' : 'not-installed'}</span>;
};

describe('useIsExtensionInstalled', () => {
  afterEach(() => {
    document.documentElement.removeAttribute(EXTENSION_INSTALLED_ATTRIBUTE);
  });

  it('returns false when the marker is absent', () => {
    render(<ExtensionProbe />);
    expect(screen.getByText('not-installed')).toBeInTheDocument();
  });

  it('returns true when the marker is already present at mount', () => {
    document.documentElement.setAttribute(
      EXTENSION_INSTALLED_ATTRIBUTE,
      'true'
    );
    render(<ExtensionProbe />);
    expect(screen.getByText('installed')).toBeInTheDocument();
  });

  it('detects the marker added after mount', async () => {
    render(<ExtensionProbe />);
    expect(screen.getByText('not-installed')).toBeInTheDocument();

    document.documentElement.setAttribute(
      EXTENSION_INSTALLED_ATTRIBUTE,
      'true'
    );

    expect(await screen.findByText('installed')).toBeInTheDocument();
  });
});
