/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';

/*
  Utils functions used to mock react-i18next Trans component.
  Imported from 
  https://github.com/i18next/react-i18next/blob/v11.15.1/example/test-jest/src/__mocks__/react-i18next.js
*/

const hasChildren = (node: any) =>
  (node && node.children) || (node.props && node.props.children);

const getChildren = (node: any) =>
  node && node.children ? node.children : node.props && node.props.children;

const renderNodes = (reactNodes: any): React.ReactNode => {
  if (typeof reactNodes === 'string') {
    return reactNodes;
  }

  return Object.keys(reactNodes).map((key, i) => {
    const child = reactNodes[key];
    const isElement = React.isValidElement(child);

    if (typeof child === 'string') {
      return child;
    }
    if (hasChildren(child)) {
      const inner = renderNodes(getChildren(child));
      return React.cloneElement(child, { ...child.props, key: i }, inner);
    }
    if (typeof child === 'object' && !isElement) {
      return Object.keys(child).reduce(
        (str, childKey) => `${str}${child[childKey]}`,
        ''
      );
    }

    return child;
  });
};

export const MockTrans = ({ children }: { children: React.ReactNode }) =>
  Array.isArray(children) ? renderNodes(children) : renderNodes([children]);
