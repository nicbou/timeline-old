import ImageThumbnailComponent from './../thumbnails/image.js';
import VideoThumbnailComponent from './../thumbnails/video.js';

export default Vue.component('gallery', {
  props: ['entry'],
  methods: {
    thumbnailType: function(entry) {
      if(entry.schema.startsWith('file.video')) {
        return 'video-thumbnail';
      }
      return 'image-thumbnail';
    },
    hasGeolocation: function(entry) {
      return !!entry.extra_attributes.location;
    },
  },
  template: `
    <div class="gallery">
      <i class="icon fas fa-image"></i>
      <div class="meta">Gallery</div>
      <div class="content">
        <div class="thumbnail" v-for="subentry in entry">
          <component
            height="200"
            v-if="subentry.extra_attributes.previews"
            :is="thumbnailType(subentry)"
            :entry="subentry"
            :title="new Date(subentry.date_on_timeline).toLocaleString()"
            @click="$emit('select', subentry)"></component>
          <div class="media-icons">
            <i v-if="hasGeolocation(subentry)" class="fas fa-map-marker-alt"></i>
          </div>
        </div>
      </div>
    </div>
  `
});