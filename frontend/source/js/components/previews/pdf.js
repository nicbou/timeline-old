import ImagePreview from './image.js';

export default Vue.component('pdf-preview', {
  props: ['entry'],
  computed: {
  },
  template: `
    <object :data="entry.extra_attributes.file.path" type="application/pdf">
      <image-preview :entry="entry"></image-preview>
    </object>
  `
});
