import React from 'react';
import { TFunction } from 'react-i18next';
import { SvgIconComponent } from '@mui/icons-material';
import {
  Entity,
  EntityNoExtraField,
  Recommendation,
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

export type RelatedEntityObject =
  | EntityNoExtraField
  | RelatedEntity
  | Recommendation;
export type VideoObject = Video | VideoSerializerWithCriteria;

/**
 * An exhaustive list of route ids helping to enforce type checking in each
 * place a route id is required.
 */
export enum RouteID {
  // public and collective routes
  Home = 'home',
  CollectiveRecommendations = 'collectiveRecommendations',
  EntityAnalysis = 'entityAnalysis',
  About = 'about',
  // public yet personal routes
  PublicPersonalRecommendationsPage = 'publicPersonalRecommendations',
  // private and personal routes
  Comparison = 'comparison',
  MyComparisons = 'myComparisons',
  MyComparedItems = 'myComparedItems',
  MyRateLaterList = 'myRateLaterList',
  MyFeedback = 'myFeedback',
}

export type OrderedDialogs = {
  [key: string]: { title: string; messages: Array<string> };
};

/**
 * A poll that can be displayed by <PollSelector>
 */
export type SelectablePoll = {
  name: string;
  // default actions displayed on `EntityCard` for anonymous users
  defaultAnonEntityActions: ActionList;
  // default actions displayed on `EntityCard` for authenticaed users
  defaultAuthEntityActions: ActionList;
  // if true, make the default value of the language filter on the
  // recommendation page match the browser language. not relevant for entities
  // with no language metadata
  defaultRecoLanguageDiscovery?: boolean;
  // default URL search parameters set by the `SideBar` when a user clicks on
  // the recommendation link. can be date=Month to retrieve the entities
  // uploaded during the last month for instance
  defaultRecoSearchParams?: string;
  // enable or disable the public personal recommendations feature.
  allowPublicPersonalRecommendations?: boolean;
  displayOrder: number;
  // the main criteria name. useful in some situations, like when you want
  // to exclude it from the rated high / rated low metric of the `EntityCard`
  // without hardcoding it everywhere in the application
  mainCriterionName: string;
  // the path used as URL prefix, must include leading and trailing slash
  path: string;
  // a list route id that will be disable in `PollRoutes` and `SideBar`
  disabledRouteIds?: Array<RouteID>;
  iconComponent: SvgIconComponent;
  withSearchBar: boolean;
  topBarBackground: string | null;
  // if false or undefined, the UI must not allow users to mark their
  // comparisons as public, and contributor ratings must be created with
  // is_public = false
  comparisonsCanBePublic?: boolean;
  tutorialLength?: number;
  // can be used by comparison series to limit the pool of entities
  // that are suggested after each comparison
  tutorialAlternatives?: () => Promise<Array<Entity | Recommendation>>;
  tutorialDialogs?: (t: TFunction) => OrderedDialogs;
  // redirect to this page after the last comparison is submitted
  tutorialRedirectTo?: string;
  // whether the 'unsafe' recommendations should be included by default
  unsafeDefault?: boolean;
};
