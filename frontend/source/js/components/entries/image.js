export default Vue.component('image-entry', {
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
    imageWidth: function() {
      // Some entries can have a preview but no width. For example, a PDF has no width.
      if(this.entry.extra_attributes.media && this.entry.extra_attributes.media.width && this.entry.extra_attributes.height){
        return Math.floor(this.entry.extra_attributes.media.width/entry.extra_attributes.media.height * 200)
      }
    }
  },
  template: `
    <div class="image" v-if="entry.extra_attributes.previews">
      <img
        @click="$emit('select', entry)"
        :alt="entry.title"
        :title="entry.title"
        :src="imageSrc"
        :srcset="imageSrcSet"
        :width="imageWidth"
        height="200"
        />
      <div class="media-icons">
        <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
      </div>
    </div>
  `
});