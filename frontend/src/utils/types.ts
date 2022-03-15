import React from 'react';
import { SvgIconComponent } from '@mui/icons-material';
import {
  EntityNoExtraField,
  RelatedEntity,
  Video,
  VideoSerializerWithCriteria,
} from 'src/services/openapi';

export type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };

export interface JSONObject {
  [k: string]: JSONValue;
}

export type ActionList = Array<
  (({ uid }: { uid: string }) => JSX.Element) | React.ReactNode
>;

export type RelatedEntityObject = EntityNoExtraField | RelatedEntity;
export type VideoObject = Video | VideoSerializerWithCriteria;

/**
 * An exhaustive list of route ids helping to enforce type checking in each
 * place a routeId is required.
 */
export type routeId =
  | 'home'
  | 'recommendations'
  | 'comparison'
  | 'myComparisons'
  | 'myRatedVideos'
  | 'myRateLaterList'
  | 'about';

/**
 * A poll that can be displayed by <PollSelector>
 */
export type SelectablePoll = {
  name: string;
  displayOrder: number;
  // the path used as URL prefix, must include leading and trailing slash
  path: string;
  // a list route id that will be disable in `PollRoutes` and `SideBar`
  disabledRouteIds?: Array<routeId>;
  iconComponent: SvgIconComponent;
  withSearchBar: boolean;
  topBarBackground: string | null;
};
