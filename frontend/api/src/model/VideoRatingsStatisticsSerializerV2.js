/**
 * Tournesol API
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 2.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 *
 */

import ApiClient from '../ApiClient';

/**
 * The VideoRatingsStatisticsSerializerV2 model module.
 * @module model/VideoRatingsStatisticsSerializerV2
 * @version 2.0.0
 */
class VideoRatingsStatisticsSerializerV2 {
    /**
     * Constructs a new <code>VideoRatingsStatisticsSerializerV2</code>.
     * Give statistics on video ratings.
     * @alias module:model/VideoRatingsStatisticsSerializerV2
     * @param id {Number} 
     * @param video {String} 
     * @param publicUsername {String} The person who left the rating
     * @param score {Number} 
     * @param nComparisons {Number} Number of all pairwise comparisons for the video by the person
     */
    constructor(id, video, publicUsername, score, nComparisons) { 
        
        VideoRatingsStatisticsSerializerV2.initialize(this, id, video, publicUsername, score, nComparisons);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj, id, video, publicUsername, score, nComparisons) { 
        obj['id'] = id;
        obj['video'] = video;
        obj['public_username'] = publicUsername;
        obj['score'] = score;
        obj['n_comparisons'] = nComparisons;
    }

    /**
     * Constructs a <code>VideoRatingsStatisticsSerializerV2</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/VideoRatingsStatisticsSerializerV2} obj Optional instance to populate.
     * @return {module:model/VideoRatingsStatisticsSerializerV2} The populated <code>VideoRatingsStatisticsSerializerV2</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new VideoRatingsStatisticsSerializerV2();

            if (data.hasOwnProperty('id')) {
                obj['id'] = ApiClient.convertToType(data['id'], 'Number');
            }
            if (data.hasOwnProperty('video')) {
                obj['video'] = ApiClient.convertToType(data['video'], 'String');
            }
            if (data.hasOwnProperty('public_username')) {
                obj['public_username'] = ApiClient.convertToType(data['public_username'], 'String');
            }
            if (data.hasOwnProperty('score')) {
                obj['score'] = ApiClient.convertToType(data['score'], 'Number');
            }
            if (data.hasOwnProperty('n_comparisons')) {
                obj['n_comparisons'] = ApiClient.convertToType(data['n_comparisons'], 'Number');
            }
            if (data.hasOwnProperty('largely_recommended')) {
                obj['largely_recommended'] = ApiClient.convertToType(data['largely_recommended'], 'Number');
            }
            if (data.hasOwnProperty('reliability')) {
                obj['reliability'] = ApiClient.convertToType(data['reliability'], 'Number');
            }
            if (data.hasOwnProperty('importance')) {
                obj['importance'] = ApiClient.convertToType(data['importance'], 'Number');
            }
            if (data.hasOwnProperty('engaging')) {
                obj['engaging'] = ApiClient.convertToType(data['engaging'], 'Number');
            }
            if (data.hasOwnProperty('pedagogy')) {
                obj['pedagogy'] = ApiClient.convertToType(data['pedagogy'], 'Number');
            }
            if (data.hasOwnProperty('layman_friendly')) {
                obj['layman_friendly'] = ApiClient.convertToType(data['layman_friendly'], 'Number');
            }
            if (data.hasOwnProperty('diversity_inclusion')) {
                obj['diversity_inclusion'] = ApiClient.convertToType(data['diversity_inclusion'], 'Number');
            }
            if (data.hasOwnProperty('backfire_risk')) {
                obj['backfire_risk'] = ApiClient.convertToType(data['backfire_risk'], 'Number');
            }
            if (data.hasOwnProperty('better_habits')) {
                obj['better_habits'] = ApiClient.convertToType(data['better_habits'], 'Number');
            }
            if (data.hasOwnProperty('entertaining_relaxing')) {
                obj['entertaining_relaxing'] = ApiClient.convertToType(data['entertaining_relaxing'], 'Number');
            }
        }
        return obj;
    }


}

/**
 * @member {Number} id
 */
VideoRatingsStatisticsSerializerV2.prototype['id'] = undefined;

/**
 * @member {String} video
 */
VideoRatingsStatisticsSerializerV2.prototype['video'] = undefined;

/**
 * The person who left the rating
 * @member {String} public_username
 */
VideoRatingsStatisticsSerializerV2.prototype['public_username'] = undefined;

/**
 * @member {Number} score
 * @default 0.0
 */
VideoRatingsStatisticsSerializerV2.prototype['score'] = 0.0;

/**
 * Number of all pairwise comparisons for the video by the person
 * @member {Number} n_comparisons
 */
VideoRatingsStatisticsSerializerV2.prototype['n_comparisons'] = undefined;

/**
 * Should be largely recommended
 * @member {Number} largely_recommended
 */
VideoRatingsStatisticsSerializerV2.prototype['largely_recommended'] = undefined;

/**
 * Reliable and not misleading
 * @member {Number} reliability
 */
VideoRatingsStatisticsSerializerV2.prototype['reliability'] = undefined;

/**
 * Important and actionable
 * @member {Number} importance
 */
VideoRatingsStatisticsSerializerV2.prototype['importance'] = undefined;

/**
 * Engaging and thought-provoking
 * @member {Number} engaging
 */
VideoRatingsStatisticsSerializerV2.prototype['engaging'] = undefined;

/**
 * Clear and pedagogical
 * @member {Number} pedagogy
 */
VideoRatingsStatisticsSerializerV2.prototype['pedagogy'] = undefined;

/**
 * Layman-friendly
 * @member {Number} layman_friendly
 */
VideoRatingsStatisticsSerializerV2.prototype['layman_friendly'] = undefined;

/**
 * Diversity and Inclusion
 * @member {Number} diversity_inclusion
 */
VideoRatingsStatisticsSerializerV2.prototype['diversity_inclusion'] = undefined;

/**
 * Resilience to backfiring risks
 * @member {Number} backfire_risk
 */
VideoRatingsStatisticsSerializerV2.prototype['backfire_risk'] = undefined;

/**
 * Encourages better habits
 * @member {Number} better_habits
 */
VideoRatingsStatisticsSerializerV2.prototype['better_habits'] = undefined;

/**
 * Entertaining and relaxing
 * @member {Number} entertaining_relaxing
 */
VideoRatingsStatisticsSerializerV2.prototype['entertaining_relaxing'] = undefined;






export default VideoRatingsStatisticsSerializerV2;

