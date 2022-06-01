export default Vue.component('pdf-preview', {
  props: ['entry'],
  computed: {
  },
  template: `
    <object :data="entry.extra_attributes.file.path" type="application/pdf"></object>
  `
});