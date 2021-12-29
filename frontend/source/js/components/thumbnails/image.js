export default Vue.component('image-thumbnail', {
  props: ['entry', 'height'],
  computed: {
    src: function() {
      return this.entry.extra_attributes.previews.thumbnail;
    },
    srcset: function() {
      return `${this.entry.extra_attributes.previews.thumbnail} 1x, ${this.entry.extra_attributes.previews.thumbnail2x} 2x`;
    },
    width: function() {
      // Some entries can have a preview but no width. For example, a PDF has no width.
      if(this.entry.extra_attributes.media && this.entry.extra_attributes.media.width && this.entry.extra_attributes.height){
        return Math.floor(this.entry.extra_attributes.media.width/entry.extra_attributes.media.height * this.height)
      }
    }
  },
  template: `
    <img
      @click="$emit('select', entry)"
      :alt="entry.title"
      :height="height"
      :src="src"
      :srcset="srcset"
      :title="entry.title"
      :width="width"
      />
  `
});