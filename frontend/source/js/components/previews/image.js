export default Vue.component('image-preview', {
  props: ['entry'],
  computed: {
    imageSrcSet: function() {
        return `${this.entry.extra_attributes.previews.preview} 1x, ${this.entry.extra_attributes.previews.preview2x} 2x`;
    },
  },
  template: `
    <img
      :alt="entry.title"
      :src="entry.extra_attributes.previews.preview"
      :srcset="imageSrcSet"
      />
  `
});