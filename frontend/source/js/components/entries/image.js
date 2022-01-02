import ImageThumbnailComponent from './../thumbnails/image.js';
export default Vue.component('image-entry', {
  props: ['entry'],
  computed: {
    hasGeolocation: function() {
      return !!this.entry.extra_attributes.location;
    },
  },
  template: `
    <div class="image" @click="$emit('select', entry)" v-if="entry.extra_attributes.previews">
      <i class="icon fas fa-image" :title="new Date(entry.date_on_timeline).toLocaleString()"></i>
      <div class="meta">{{ entry.title }}</div>
      <div class="content">
        <image-thumbnail :entry="entry" height="200"/>
        <div class="media-icons">
          <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
        </div>
      </div>
    </div>
  `
});