export default Vue.component('image-tile', {
  props: ['entry'],
  computed: {
    tileStyle: function() {
      if(this.entry.extra_attributes.width && this.entry.extra_attributes.height) {
        return {
          width: `${this.entry.extra_attributes.width / this.entry.extra_attributes.height * 200}px`,
        }
      }
    },
    hasGeolocation: function() {
      return !!this.entry.extra_attributes.location;
    },
    imageSrcSet: function() {
      return `${this.entry.extra_attributes.previews.thumbnail} 1x, ${this.entry.extra_attributes.previews.thumbnail2x} 2x`;
    }
  },
  template: `
    <div class="tile image" :style="tileStyle">
      <img
        @click="$emit('click', entry)"
        loading="lazy"
        :alt="entry.title"
        :src="entry.extra_attributes.previews.thumbnail"
        :srcset="imageSrcSet"
        />
      <div class="tile-icons">
        <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
      </div>
    </div>
  `
});