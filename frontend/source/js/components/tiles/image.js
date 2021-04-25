export default Vue.component('image-tile', {
  props: ['entry'],
  computed: {
    hasGeolocation: function() {
      return !!this.entry.extra_attributes.location;
    },
    imageSrc: function() {
      return this.entry.extra_attributes.previews.thumbnail;
    },
    imageSrcSet: function() {
      return `${this.entry.extra_attributes.previews.thumbnail} 1x, ${this.entry.extra_attributes.previews.thumbnail2x} 2x`;
    },
  },
  template: `
    <div class="image" v-if="entry.extra_attributes.previews">
      <img
        @click="$emit('select', entry)"
        :alt="entry.title"
        :src="imageSrc"
        :srcset="imageSrcSet"
        :width="Math.floor(entry.extra_attributes.media.width/entry.extra_attributes.media.height * 200)"
        height="200"
        />
      <div class="media-icons">
        <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
      </div>
    </div>
  `
});