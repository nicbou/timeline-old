export default Vue.component('preview-video', {
  props: ['entry'],
  template: `
    <video autoplay controls
      :alt="entry.title"
      :src="entry.extra_attributes.previews.preview"/>
  `
});