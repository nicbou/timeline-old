import ImageThumbnailComponent from './../thumbnails/image.js';
import VideoThumbnailComponent from './../thumbnails/video.js';
import { hasGeolocation } from './../../utils/entries.js';
import TimelineEntryIcon from './entry-icon.js';

export default Vue.component('gallery', {
  props: ['entry'],
  methods: {
    thumbnailType: function(entry) {
      if(entry.schema.startsWith('file.video')) {
        return 'video-thumbnail';
      }
      return 'image-thumbnail';
    },
    hasGeolocation,
  },
  template: `
    <div class="gallery">
      <entry-icon icon-class="fas fa-image" :entry="entry[0]"></entry-icon>
      <div class="meta">Gallery</div>
      <div class="content">
        <div class="thumbnail" v-for="subentry in entry" @click="$emit('select', subentry)">
          <component
            height="200"
            v-if="subentry.extra_attributes.previews"
            :is="thumbnailType(subentry)"
            :entry="subentry"
            :title="new Date(subentry.date_on_timeline).toLocaleString()"></component>
          <div class="media-icons">
            <i v-if="hasGeolocation(subentry)" class="fas fa-map-marker-alt"></i>
          </div>
        </div>
      </div>
    </div>
  `
});