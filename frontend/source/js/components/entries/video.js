import VideoThumbnailComponent from './../thumbnails/video.js';
export default Vue.component('video-entry', {
  props: ['entry'],
  computed: {
    hasGeolocation: function() {
      return !!this.entry.extra_attributes.location;
    },
  },
  template: `
    <div class="video" @click="$emit('select', entry)" v-if="entry.extra_attributes.previews">
      <i class="icon fas fa-play-circle" :title="new Date(entry.date_on_timeline).toLocaleString()"></i>
      <div class="meta">{{ entry.title }}</div>
      <div class="content">
        <video-thumbnail :entry="entry" height="200"/>
        <div class="media-icons">
          <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
          <i class="fas fa-play-circle"></i>
        </div>
      </div>
    </div>
  `
});