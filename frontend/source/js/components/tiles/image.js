export default Vue.component('image-tile', {
  props: ['entry'],
  computed: {
    tileStyle: function() {
      if(this.entry.extra_attributes.media && this.entry.extra_attributes.media.width && this.entry.extra_attributes.media.height) {
        return {
          width: `${this.entry.extra_attributes.media.width / this.entry.extra_attributes.media.height * 200}px`,
        }
      }
    },
    hasGeolocation: function() {
      return !!this.entry.extra_attributes.location;
    },
    imageSrc: function() {
      return entry.extra_attributes.previews.thumbnail;
    },
    imageSrcSet: function() {
      return `${this.entry.extra_attributes.previews.thumbnail} 1x, ${this.entry.extra_attributes.previews.thumbnail2x} 2x`;
    },
  },
  template: `
    <div class="tile image" :style="tileStyle">
      <img v-if="entry.extra_attributes.previews"
        @click="$emit('select', entry)"
        loading="lazy"
        :alt="entry.title"
        :src="imageSrc"
        :srcset="imageSrcSet"
        />
      <div class="tile-icons">
        <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
      </div>
    </div>
  `
});